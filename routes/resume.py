from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g, jsonify
from models import db, Resume, UserSkill
from routes.auth import login_required
from services.resume_service import ResumeService, SKILLS_DICTIONARY

resume_bp = Blueprint("resume", __name__, url_prefix="/resume")


@resume_bp.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    user = g.user
    latest_resume = (
        Resume.query
        .filter_by(user_id=user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    user_skills = UserSkill.query.filter_by(user_id=user.id).all()
    available_skills = list(SKILLS_DICTIONARY.keys())

    if request.method == "POST":
        if "resume_file" not in request.files:
            flash("No file part provided in the request.", "danger")
            return redirect(request.url)

        file = request.files["resume_file"]
        if file.filename == "":
            flash("Please choose a PDF resume file to upload.", "warning")
            return redirect(request.url)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        save_result = ResumeService.save_uploaded_pdf(file, upload_folder, user.id)

        if not save_result["success"]:
            flash(save_result["error"], "danger")
            return redirect(request.url)

        # Extract text via PyMuPDF
        extract_result = ResumeService.extract_text_from_pdf(save_result["filepath"])

        if not extract_result["success"]:
            flash(extract_result["error"], "warning" if extract_result.get("is_scanned") else "danger")
            # If scanned, we still record the uploaded file metadata
            resume_record = Resume(
                user_id=user.id,
                filename=save_result["filename"],
                file_path=save_result["filepath"],
                raw_text="",
                parsed_skills=[],
                recommended_domains=[]
            )
            db.session.add(resume_record)
            db.session.commit()
            return redirect(url_for("resume.analyze"))

        # Skill extraction and recommendations
        analysis = ResumeService.extract_skills_and_recommendations(extract_result["text"])
        detected_skills = analysis["skills"]
        recommendations = analysis["recommendations"]

        resume_record = Resume(
            user_id=user.id,
            filename=save_result["filename"],
            file_path=save_result["filepath"],
            raw_text=extract_result["text"][:10000],  # store first 10k chars
            parsed_skills=detected_skills,
            recommended_domains=recommendations
        )
        db.session.add(resume_record)

        # Sync detected skills with user_skills table
        for skill_name in detected_skills:
            existing = UserSkill.query.filter_by(user_id=user.id, skill_name=skill_name).first()
            if not existing:
                db.session.add(UserSkill(
                    user_id=user.id,
                    skill_name=skill_name,
                    proficiency="Intermediate",
                    source="extracted"
                ))

        db.session.commit()
        flash(f"Resume processed successfully! Detected {len(detected_skills)} skills.", "success")
        return redirect(url_for("resume.analyze"))

    return render_template(
        "resume/analyze.html",
        latest_resume=latest_resume,
        user_skills=user_skills,
        available_skills=available_skills
    )


@resume_bp.route("/skills/add", methods=["POST"])
@login_required
def add_skill():
    user = g.user
    skill_name = request.form.get("skill_name", "").strip()
    proficiency = request.form.get("proficiency", "Intermediate").strip()

    if not skill_name:
        flash("Skill name cannot be empty.", "warning")
        return redirect(url_for("resume.analyze"))

    existing = UserSkill.query.filter_by(user_id=user.id, skill_name=skill_name).first()
    if existing:
        flash(f"'{skill_name}' is already in your skills list.", "info")
    else:
        db.session.add(UserSkill(
            user_id=user.id,
            skill_name=skill_name,
            proficiency=proficiency,
            source="manual"
        ))
        db.session.commit()
        flash(f"Added '{skill_name}' to your skill profile.", "success")

    return redirect(url_for("resume.analyze"))


@resume_bp.route("/skills/remove/<int:skill_id>", methods=["POST"])
@login_required
def remove_skill(skill_id):
    user = g.user
    user_skill = UserSkill.query.filter_by(id=skill_id, user_id=user.id).first()
    if user_skill:
        db.session.delete(user_skill)
        db.session.commit()
        flash(f"Removed '{user_skill.skill_name}' from your profile.", "info")
    else:
        flash("Skill not found.", "warning")

    return redirect(url_for("resume.analyze"))
