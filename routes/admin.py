import json
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, User, Question, Company, SkillCategory, InterviewSession
from routes.auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

COMPANIES = ["TCS", "Infosys", "Zoho", "Accenture", "Amazon", "Google", "General"]
SKILLS = [
    "Java", "Python", "DBMS", "SQL", "Data Structures",
    "HTML/CSS", "JavaScript", "Spring Boot", "General Programming", "HR"
]
DIFFICULTIES = ["Easy", "Medium", "Hard"]


@admin_bp.route("")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_questions = Question.query.count()
    total_interviews = InterviewSession.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    recent_questions = Question.query.order_by(Question.created_at.desc()).limit(8).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_questions=total_questions,
        total_interviews=total_interviews,
        recent_users=recent_users,
        recent_questions=recent_questions
    )


@admin_bp.route("/users")
@admin_required
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/questions")
@admin_required
def questions_list():
    company_filter = request.args.get("company", "").strip()
    skill_filter = request.args.get("skill", "").strip()
    difficulty_filter = request.args.get("difficulty", "").strip()

    query = Question.query

    if company_filter:
        query = query.filter(Question.company.ilike(company_filter))
    if skill_filter:
        query = query.filter(Question.skill.ilike(skill_filter))
    if difficulty_filter:
        query = query.filter(Question.difficulty == difficulty_filter)

    questions = query.order_by(Question.created_at.desc()).all()

    return render_template(
        "admin/questions.html",
        questions=questions,
        companies=COMPANIES,
        skills=SKILLS,
        difficulties=DIFFICULTIES,
        current_company=company_filter,
        current_skill=skill_filter,
        current_difficulty=difficulty_filter
    )


@admin_bp.route("/questions/add", methods=["GET", "POST"])
@admin_required
def question_add():
    if request.method == "POST":
        company = request.form.get("company", "General").strip()
        skill = request.form.get("skill", "").strip()
        interview_type = request.form.get("interview_type", "Technical").strip()
        difficulty = request.form.get("difficulty", "Medium").strip()
        category = request.form.get("category", "").strip()
        question_text = request.form.get("question_text", "").strip()
        model_answer = request.form.get("model_answer", "").strip()
        keywords_raw = request.form.get("keywords", "").strip()
        follow_up_to_id = request.form.get("follow_up_to_id", "").strip()

        # Validation
        if not question_text or not model_answer or not skill:
            flash("Question text, model answer, and skill are required fields.", "danger")
            return redirect(url_for("admin.question_add"))

        # Parse keywords (comma-separated to list)
        keywords_list = [k.strip() for k in keywords_raw.split(",") if k.strip()]

        new_question = Question(
            company=company,
            skill=skill,
            interview_type=interview_type,
            difficulty=difficulty,
            category=category,
            question_text=question_text,
            model_answer=model_answer,
            keywords=keywords_list,
            follow_up_to_id=int(follow_up_to_id) if follow_up_to_id.isdigit() else None
        )
        db.session.add(new_question)
        db.session.commit()

        flash("New question added to bank successfully.", "success")
        return redirect(url_for("admin.questions_list"))

    all_questions = Question.query.order_by(Question.skill, Question.question_text).all()
    return render_template(
        "admin/question_form.html",
        action="Add",
        question=None,
        companies=COMPANIES,
        skills=SKILLS,
        difficulties=DIFFICULTIES,
        all_questions=all_questions
    )


@admin_bp.route("/questions/edit/<int:question_id>", methods=["GET", "POST"])
@admin_required
def question_edit(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == "POST":
        question.company = request.form.get("company", "General").strip()
        question.skill = request.form.get("skill", "").strip()
        question.interview_type = request.form.get("interview_type", "Technical").strip()
        question.difficulty = request.form.get("difficulty", "Medium").strip()
        question.category = request.form.get("category", "").strip()
        question.question_text = request.form.get("question_text", "").strip()
        question.model_answer = request.form.get("model_answer", "").strip()
        keywords_raw = request.form.get("keywords", "").strip()
        follow_up_to_id = request.form.get("follow_up_to_id", "").strip()

        if not question.question_text or not question.model_answer or not question.skill:
            flash("Question text, model answer, and skill are required fields.", "danger")
            return redirect(url_for("admin.question_edit", question_id=question_id))

        question.keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        question.follow_up_to_id = int(follow_up_to_id) if follow_up_to_id.isdigit() else None

        db.session.commit()
        flash("Question updated successfully.", "success")
        return redirect(url_for("admin.questions_list"))

    all_questions = Question.query.filter(Question.id != question.id).order_by(Question.skill).all()
    return render_template(
        "admin/question_form.html",
        action="Edit",
        question=question,
        companies=COMPANIES,
        skills=SKILLS,
        difficulties=DIFFICULTIES,
        all_questions=all_questions
    )


@admin_bp.route("/questions/delete/<int:question_id>", methods=["POST"])
@admin_required
def question_delete(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "info")
    return redirect(url_for("admin.questions_list"))


@admin_bp.route("/seed", methods=["POST"])
@admin_required
def seed_database():
    from app import seed_sample_data
    count = seed_sample_data()
    flash(f"Question bank re-seeded successfully ({count} questions).", "success")
    return redirect(url_for("admin.questions_list"))
