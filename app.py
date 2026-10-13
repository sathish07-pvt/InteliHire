import os
import json
from pathlib import Path
from flask import Flask, render_template
from flask_migrate import Migrate
from config import Config
from models import db, User, Question, Company, SkillCategory
from routes import auth_bp, main_bp, resume_bp, interview_bp, admin_bp

migrate = Migrate()


def create_app(config_class=Config):
    """Application factory for IntelliHire AI Mock Interview Platform."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(admin_bp)

    # Context processors
    @app.context_processor
    def inject_global_data():
        return {
            "app_name": "IntelliHire",
            "app_tagline": "Practice Smarter. Interview Better."
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    # Create tables and initial seeds
    with app.app_context():
        db.create_all()
        seed_admin_account(app)
        seed_sample_data()

    return app


def seed_admin_account(app):
    """Seeds the initial administrator user if not present."""
    admin_email = app.config.get("ADMIN_EMAIL", "admin@intellihire.com")
    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin_user = User(
            name=app.config.get("ADMIN_NAME", "System Administrator"),
            email=admin_email,
            role="admin"
        )
        admin_user.set_password(app.config.get("ADMIN_PASSWORD", "Admin@12345"))
        db.session.add(admin_user)
        db.session.commit()
        print(f"[IntelliHire] Initial administrator seeded: {admin_email}")


def seed_sample_data() -> int:
    """Seeds the question bank from data/seed_questions.json and links follow-ups."""
    seed_file = Path(__file__).resolve().parent / "data" / "seed_questions.json"
    if not seed_file.exists():
        return 0

    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        print(f"[IntelliHire] Error loading seed file: {e}")
        return 0

    slug_to_id = {}
    seeded_count = 0

    # Step 1: Add or update questions
    for q_data in items:
        existing = Question.query.filter_by(question_text=q_data["question_text"]).first()
        if not existing:
            new_q = Question(
                company=q_data.get("company", "General"),
                skill=q_data.get("skill", "General Programming"),
                interview_type=q_data.get("interview_type", "Technical"),
                difficulty=q_data.get("difficulty", "Medium"),
                category=q_data.get("category", "General"),
                question_text=q_data["question_text"],
                model_answer=q_data["model_answer"],
                keywords=q_data.get("keywords", []),
                is_active=True
            )
            db.session.add(new_q)
            db.session.flush()
            if "slug" in q_data:
                slug_to_id[q_data["slug"]] = new_q.id
            seeded_count += 1
        else:
            if "slug" in q_data:
                slug_to_id[q_data["slug"]] = existing.id

    db.session.commit()

    # Step 2: Link follow-up relationships
    for q_data in items:
        if q_data.get("follow_up_slug") and q_data.get("slug"):
            parent_id = slug_to_id.get(q_data["slug"])
            child_id = slug_to_id.get(q_data["follow_up_slug"])
            if parent_id and child_id:
                child_q = db.session.get(Question, child_id)
                if child_q and child_q.follow_up_to_id != parent_id:
                    child_q.follow_up_to_id = parent_id

    db.session.commit()
    if seeded_count > 0:
        print(f"[IntelliHire] Question bank initialized with {seeded_count} practice questions.")
    return seeded_count


app = create_app()

if __name__ == "__main__":
    print("[IntelliHire] Starting development server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
