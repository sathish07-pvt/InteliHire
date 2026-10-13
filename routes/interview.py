from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g, abort
from models import db, InterviewSession, InterviewQuestion, PerformanceReport, UserSkill
from routes.auth import login_required
from services.question_selection_service import QuestionSelectionService
from services.nlp_evaluation_service import NLPEvaluationService
from services.report_service import ReportService

interview_bp = Blueprint("interview", __name__, url_prefix="/interview")

COMPANIES = ["TCS", "Infosys", "Zoho", "Accenture", "Amazon", "Google", "General"]
SKILLS = [
    "Java", "Python", "DBMS", "SQL", "Data Structures",
    "HTML/CSS", "JavaScript", "Spring Boot", "General Programming", "HR"
]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
QUESTION_COUNTS = [5, 10, 15]


@interview_bp.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    user = g.user
    user_skills = [s.skill_name for s in UserSkill.query.filter_by(user_id=user.id).all()]

    if request.method == "POST":
        company = request.form.get("company", "General").strip()
        skill = request.form.get("skill", "Java").strip()
        interview_type = request.form.get("interview_type", "Technical").strip()
        difficulty = request.form.get("difficulty", "Medium").strip()
        try:
            q_count = int(request.form.get("question_count", 5))
        except ValueError:
            q_count = 5

        # Validation
        if company not in COMPANIES:
            company = "General"
        if skill not in SKILLS:
            skill = "General Programming"
        if difficulty not in DIFFICULTIES:
            difficulty = "Medium"
        if q_count not in QUESTION_COUNTS:
            q_count = 5

        # Create session
        new_session = InterviewSession(
            user_id=user.id,
            company=company,
            skill=skill,
            interview_type=interview_type,
            difficulty=difficulty,
            question_count=q_count,
            current_index=0,
            status="in_progress"
        )
        db.session.add(new_session)
        db.session.flush()

        # Select first question
        first_q_data = QuestionSelectionService.select_next_question(
            skill=skill,
            company=company,
            interview_type=interview_type,
            target_difficulty=difficulty,
            used_question_ids=[],
            used_question_texts=[],
            previous_question_id=None,
            previous_score=None
        )

        first_q = InterviewQuestion(
            session_id=new_session.id,
            question_id=first_q_data.get("question_id"),
            order_index=1,
            question_text=first_q_data["question_text"],
            model_answer=first_q_data["model_answer"],
            keywords=first_q_data.get("keywords", []),
            difficulty=first_q_data.get("difficulty", difficulty),
            question_source=first_q_data.get("source", "generator")
        )
        db.session.add(first_q)
        db.session.commit()

        return redirect(url_for("interview.session_view", session_uuid=new_session.session_uuid))

    return render_template(
        "interview/setup.html",
        companies=COMPANIES,
        skills=SKILLS,
        difficulties=DIFFICULTIES,
        question_counts=QUESTION_COUNTS,
        user_skills=user_skills
    )


@interview_bp.route("/<string:session_uuid>")
@login_required
def session_view(session_uuid):
    user = g.user
    interview_session = InterviewSession.query.filter_by(session_uuid=session_uuid).first()

    if not interview_session:
        flash("Interview session not found.", "danger")
        return redirect(url_for("main.dashboard"))

    # Security check: Ownership validation
    if interview_session.user_id != user.id:
        flash("Unauthorized: You cannot access another candidate's interview session.", "danger")
        return redirect(url_for("main.dashboard"))

    if interview_session.status == "completed":
        return redirect(url_for("interview.report_view", session_uuid=session_uuid))

    current_q = (
        InterviewQuestion.query
        .filter_by(session_id=interview_session.id, order_index=interview_session.current_index + 1)
        .first()
    )

    if not current_q:
        # Generate current question if missing
        used_ids = [q.question_id for q in interview_session.questions if q.question_id]
        used_texts = [q.question_text for q in interview_session.questions]
        next_data = QuestionSelectionService.select_next_question(
            skill=interview_session.skill,
            company=interview_session.company,
            interview_type=interview_session.interview_type,
            target_difficulty=interview_session.difficulty,
            used_question_ids=used_ids,
            used_question_texts=used_texts
        )
        current_q = InterviewQuestion(
            session_id=interview_session.id,
            question_id=next_data.get("question_id"),
            order_index=interview_session.current_index + 1,
            question_text=next_data["question_text"],
            model_answer=next_data["model_answer"],
            keywords=next_data.get("keywords", []),
            difficulty=next_data.get("difficulty", interview_session.difficulty),
            question_source=next_data.get("source", "generator")
        )
        db.session.add(current_q)
        db.session.commit()

    return render_template(
        "interview/session.html",
        interview_session=interview_session,
        current_question=current_q
    )


@interview_bp.route("/<string:session_uuid>/submit", methods=["POST"])
@login_required
def submit_answer(session_uuid):
    user = g.user
    interview_session = InterviewSession.query.filter_by(session_uuid=session_uuid).first()

    if not interview_session or interview_session.user_id != user.id:
        return jsonify({"success": False, "error": "Unauthorized or invalid session."}), 403

    if interview_session.status == "completed":
        return jsonify({
            "success": True,
            "completed": True,
            "redirect_url": url_for("interview.report_view", session_uuid=session_uuid)
        })

    current_q = (
        InterviewQuestion.query
        .filter_by(session_id=interview_session.id, order_index=interview_session.current_index + 1)
        .first()
    )

    if not current_q:
        return jsonify({"success": False, "error": "Active question not found."}), 404

    # Prevent duplicate submission
    if current_q.answered_at is not None:
        return jsonify({
            "success": False,
            "error": "This question has already been answered. Please proceed to the next question."
        }), 400

    data = request.get_json(silent=True) or request.form
    user_answer = data.get("user_answer", "").strip()

    # NLP Answer Evaluation
    eval_result = NLPEvaluationService.evaluate_answer(
        question=current_q.question_text,
        model_answer=current_q.model_answer,
        user_answer=user_answer,
        keywords=current_q.keywords or []
    )

    # Persist evaluation
    current_q.user_answer = user_answer
    current_q.similarity_score = eval_result["similarity_score"]
    current_q.keyword_coverage = eval_result["keyword_coverage"]
    current_q.final_score = eval_result["final_score"]
    current_q.strengths = eval_result["strengths"]
    current_q.weaknesses = eval_result["weaknesses"]
    current_q.missing_concepts = eval_result["missing_concepts"]
    current_q.feedback = eval_result["feedback"]
    current_q.answered_at = datetime.utcnow()

    # Determine if interview continues or completes
    next_index = interview_session.current_index + 1
    is_completed = next_index >= interview_session.question_count

    if is_completed:
        interview_session.status = "completed"
        interview_session.completed_at = datetime.utcnow()
        db.session.commit()
        ReportService.generate_and_save_report(interview_session)
        redirect_url = url_for("interview.report_view", session_uuid=session_uuid)
    else:
        interview_session.current_index = next_index
        # Pre-select next adaptive question
        used_ids = [q.question_id for q in interview_session.questions if q.question_id]
        used_texts = [q.question_text for q in interview_session.questions]
        next_q_data = QuestionSelectionService.select_next_question(
            skill=interview_session.skill,
            company=interview_session.company,
            interview_type=interview_session.interview_type,
            target_difficulty=interview_session.difficulty,
            used_question_ids=used_ids,
            used_question_texts=used_texts,
            previous_question_id=current_q.question_id,
            previous_score=current_q.final_score
        )
        next_q = InterviewQuestion(
            session_id=interview_session.id,
            question_id=next_q_data.get("question_id"),
            order_index=next_index + 1,
            question_text=next_q_data["question_text"],
            model_answer=next_q_data["model_answer"],
            keywords=next_q_data.get("keywords", []),
            difficulty=next_q_data.get("difficulty", interview_session.difficulty),
            question_source=next_q_data.get("source", "generator")
        )
        db.session.add(next_q)
        db.session.commit()
        redirect_url = url_for("interview.session_view", session_uuid=session_uuid)

    return jsonify({
        "success": True,
        "completed": is_completed,
        "evaluation": {
            "score": current_q.final_score,
            "similarity": current_q.similarity_score,
            "coverage": current_q.keyword_coverage,
            "strengths": current_q.strengths,
            "weaknesses": current_q.weaknesses,
            "missing_concepts": current_q.missing_concepts,
            "feedback": current_q.feedback
        },
        "next_question_number": next_index + 1 if not is_completed else None,
        "redirect_url": redirect_url
    })


@interview_bp.route("/<string:session_uuid>/report")
@login_required
def report_view(session_uuid):
    user = g.user
    interview_session = InterviewSession.query.filter_by(session_uuid=session_uuid).first()

    if not interview_session:
        flash("Interview report not found.", "danger")
        return redirect(url_for("main.dashboard"))

    if interview_session.user_id != user.id:
        flash("Unauthorized: You cannot access another candidate's performance report.", "danger")
        return redirect(url_for("main.dashboard"))

    report = PerformanceReport.query.filter_by(session_id=interview_session.id).first()
    if not report:
        report = ReportService.generate_and_save_report(interview_session)

    questions = (
        InterviewQuestion.query
        .filter_by(session_id=interview_session.id)
        .order_by(InterviewQuestion.order_index)
        .all()
    )

    # Prepare chart labels & values for question-by-question breakdown
    chart_labels = [f"Q{q.order_index}" for q in questions]
    chart_scores = [round(q.final_score or 0.0, 1) for q in questions]

    return render_template(
        "interview/report.html",
        interview_session=interview_session,
        report=report,
        questions=questions,
        chart_labels=chart_labels,
        chart_scores=chart_scores
    )
