from datetime import datetime
from models import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SkillCategory(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), default="Technical")
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False, index=True, default="General")
    skill = db.Column(db.String(100), nullable=False, index=True)
    interview_type = db.Column(db.String(30), nullable=False, default="Technical")  # Technical, HR
    difficulty = db.Column(db.String(20), nullable=False, default="Medium")  # Easy, Medium, Hard
    category = db.Column(db.String(100), nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    model_answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.JSON, nullable=False, default=list)  # List of essential keywords
    follow_up_to_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Self-referential relationship for linked follow-up questions
    follow_up_questions = db.relationship(
        "Question",
        backref=db.backref("parent_question", remote_side=[id]),
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "skill": self.skill,
            "interview_type": self.interview_type,
            "difficulty": self.difficulty,
            "category": self.category,
            "question_text": self.question_text,
            "model_answer": self.model_answer,
            "keywords": self.keywords or [],
            "follow_up_to_id": self.follow_up_to_id,
            "is_active": self.is_active,
        }
