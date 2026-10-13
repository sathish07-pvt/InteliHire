from models import db, Question, InterviewSession, InterviewQuestion, PerformanceReport, User
from services.question_selection_service import QuestionSelectionService
from services.question_generation_service import QuestionGenerationService
from services.report_service import ReportService


def test_adaptive_difficulty_progression():
    # High score should increase difficulty
    assert QuestionSelectionService.get_adapted_difficulty("Easy", 85.0) == "Medium"
    assert QuestionSelectionService.get_adapted_difficulty("Medium", 90.0) == "Hard"
    assert QuestionSelectionService.get_adapted_difficulty("Hard", 95.0) == "Hard"  # Maxes out at Hard

    # Low score should reduce difficulty
    assert QuestionSelectionService.get_adapted_difficulty("Hard", 40.0) == "Medium"
    assert QuestionSelectionService.get_adapted_difficulty("Medium", 30.0) == "Easy"
    assert QuestionSelectionService.get_adapted_difficulty("Easy", 20.0) == "Easy"  # Min at Easy

    # Moderate score retains difficulty
    assert QuestionSelectionService.get_adapted_difficulty("Medium", 65.0) == "Medium"


def test_question_generator_safety():
    # Generator must produce valid dictionaries for all skills
    for skill in ["Java", "Python", "DBMS", "SQL", "Data Structures", "HTML/CSS", "JavaScript", "Spring Boot", "HR"]:
        gen = QuestionGenerationService.generate_question(skill=skill, difficulty="Medium")
        assert "question_text" in gen
        assert "model_answer" in gen
        assert "keywords" in gen
        assert len(gen["question_text"]) > 10
        assert gen["source"] == "generator"


def test_full_interview_workflow(client, auth_client, app):
    # 1. Setup session
    res_setup = auth_client.post("/interview/setup", data={
        "company": "TCS",
        "skill": "Java",
        "interview_type": "Technical",
        "difficulty": "Easy",
        "question_count": "5"
    }, follow_redirects=False)

    assert res_setup.status_code == 302
    session_url = res_setup.location
    session_uuid = session_url.split("/")[-1]

    # 2. View active session
    res_view = auth_client.get(f"/interview/{session_uuid}")
    assert res_view.status_code == 200
    assert b"Question 1 of 5" in res_view.data

    # 3. Submit an answer via JSON API
    res_submit = auth_client.post(f"/interview/{session_uuid}/submit", json={
        "user_answer": "Inheritance in Java allows a subclass to inherit attributes and methods from a superclass using extends."
    })
    assert res_submit.status_code == 200
    submit_json = res_submit.get_json()
    assert submit_json["success"] is True
    assert "evaluation" in submit_json
    assert submit_json["evaluation"]["score"] > 0

    # 4. Verify ownership protection: Another registered student cannot access this session
    with app.app_context():
        other_user = User.query.filter_by(email="other_student@example.com").first()
        if not other_user:
            other_user = User(name="Other Candidate", email="other_student@example.com", role="student")
            other_user.set_password("Student@123")
            db.session.add(other_user)
            db.session.commit()
        other_id = other_user.id
        other_name = other_user.name
        other_role = other_user.role

    with client.session_transaction() as sess:
        sess["user_id"] = other_id
        sess["user_name"] = other_name
        sess["user_role"] = other_role

    res_hack = client.get(f"/interview/{session_uuid}", follow_redirects=True)
    assert b"Unauthorized" in res_hack.data or b"Dashboard" in res_hack.data


def test_report_generation(app):
    with app.app_context():
        user = User.query.filter_by(email="teststudent@example.com").first()
        session = InterviewSession(
            user_id=user.id,
            company="Zoho",
            skill="Data Structures",
            question_count=2,
            current_index=1,
            status="completed"
        )
        db.session.add(session)
        db.session.flush()

        q1 = InterviewQuestion(
            session_id=session.id,
            order_index=1,
            question_text="How do you detect a cycle in a linked list?",
            model_answer="Floyd's algorithm uses slow and fast pointers.",
            difficulty="Medium",
            question_source="company_bank",
            user_answer="We use Floyd's cycle detection algorithm with a slow and fast pointer.",
            final_score=85.0,
            similarity_score=82.0,
            keyword_coverage=90.0,
            missing_concepts=[]
        )
        db.session.add(q1)
        db.session.commit()

        report = ReportService.generate_and_save_report(session)
        assert report is not None
        assert report.overall_score == 85.0
        assert report.readiness_percentage >= 80.0
        assert len(report.recommendations) > 0
