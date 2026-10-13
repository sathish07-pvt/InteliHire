from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from models import db, User, InterviewSession, PerformanceReport, UserSkill
from routes.auth import login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if g.user:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = g.user
    sessions = (
        InterviewSession.query
        .filter_by(user_id=user.id, status="completed")
        .order_by(InterviewSession.created_at.desc())
        .all()
    )

    total_interviews = len(sessions)
    scores = [s.report.overall_score for s in sessions if s.report]
    
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    highest_score = round(max(scores), 1) if scores else 0.0
    latest_score = round(scores[0], 1) if scores else 0.0

    # Calculate overall interview readiness percentage
    if scores:
        readiness = round(min(100.0, (avg_score * 0.7) + (latest_score * 0.3)), 1)
    else:
        readiness = 0.0

    # Skill-wise performance analysis
    skill_scores = {}
    for s in sessions:
        if s.report:
            skill_scores.setdefault(s.skill, []).append(s.report.overall_score)

    skill_averages = {
        k: round(sum(v) / len(v), 1) for k, v in skill_scores.items()
    }

    strong_skills = [k for k, v in skill_averages.items() if v >= 70.0]
    weak_skills = [k for k, v in skill_averages.items() if v < 60.0]

    # Chart 1: Chronological score progression (oldest to newest, up to 10)
    chronological = list(reversed(sessions[:10]))
    chart_dates = [s.created_at.strftime("%b %d") for s in chronological]
    chart_scores = [round(s.report.overall_score, 1) if s.report else 0 for s in chronological]

    # Chart 2: Skill-wise distribution
    chart_skills = list(skill_averages.keys())
    chart_skill_scores = list(skill_averages.values())

    # User's uploaded skills
    user_skills = UserSkill.query.filter_by(user_id=user.id).all()

    return render_template(
        "dashboard/dashboard.html",
        user=user,
        total_interviews=total_interviews,
        avg_score=avg_score,
        highest_score=highest_score,
        latest_score=latest_score,
        readiness=readiness,
        strong_skills=strong_skills,
        weak_skills=weak_skills,
        recent_sessions=sessions[:5],
        chart_dates=chart_dates,
        chart_scores=chart_scores,
        chart_skills=chart_skills,
        chart_skill_scores=chart_skill_scores,
        user_skills=user_skills
    )


@main_bp.route("/history")
@login_required
def history():
    user = g.user
    sessions = (
        InterviewSession.query
        .filter_by(user_id=user.id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    return render_template("dashboard/history.html", sessions=sessions)


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = g.user
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if name:
            user.name = name

        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                return redirect(url_for("main.profile"))
            if new_password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("main.profile"))
            user.set_password(new_password)

        db.session.commit()
        session["user_name"] = user.name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("main.profile"))

    user_skills = UserSkill.query.filter_by(user_id=user.id).all()
    return render_template("dashboard/profile.html", user=user, user_skills=user_skills)
