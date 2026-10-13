import uuid
from datetime import datetime
from models import db


class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.String(100), nullable=False)
    interview_type = db.Column(db.String(30), nullable=False, default="Technical")
    difficulty = db.Column(db.String(20), nullable=False, default="Medium")
    question_count = db.Column(db.Integer, nullable=False, default=5)
    current_index = db.Column(db.Integer, default=0, nullable=False)  # 0 to question_count - 1
    status = db.Column(db.String(30), default="in_progress", nullable=False)  # 'in_progress', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    questions = db.relationship(
        "InterviewQuestion",
        backref="session",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.order_index"
    )
    report = db.relationship(
        "PerformanceReport",
        backref="session",
        uselist=False,
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "session_uuid": self.session_uuid,
            "company": self.company,
            "skill": self.skill,
            "interview_type": self.interview_type,
            "difficulty": self.difficulty,
            "question_count": self.question_count,
            "current_index": self.current_index,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class InterviewQuestion(db.Model):
    __tablename__ = "interview_questions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("interview_sessions.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=True)
    order_index = db.Column(db.Integer, nullable=False)  # 1-based order
    question_text = db.Column(db.Text, nullable=False)
    model_answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.JSON, default=list)
    difficulty = db.Column(db.String(20), nullable=False, default="Medium")
    question_source = db.Column(db.String(50), nullable=False)  # 'company_bank', 'general_bank', 'generator'
    
    # Candidate responses & NLP Evaluation
    user_answer = db.Column(db.Text, nullable=True)
    similarity_score = db.Column(db.Float, default=0.0)
    keyword_coverage = db.Column(db.Float, default=0.0)
    final_score = db.Column(db.Float, default=0.0)
    strengths = db.Column(db.JSON, default=list)
    weaknesses = db.Column(db.JSON, default=list)
    missing_concepts = db.Column(db.JSON, default=list)
    feedback = db.Column(db.Text, nullable=True)
    answered_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "order_index": self.order_index,
            "question_text": self.question_text,
            "difficulty": self.difficulty,
            "question_source": self.question_source,
            "user_answer": self.user_answer,
            "similarity_score": round(self.similarity_score or 0.0, 1),
            "keyword_coverage": round(self.keyword_coverage or 0.0, 1),
            "final_score": round(self.final_score or 0.0, 1),
            "strengths": self.strengths or [],
            "weaknesses": self.weaknesses or [],
            "missing_concepts": self.missing_concepts or [],
            "feedback": self.feedback,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }


class PerformanceReport(db.Model):
    __tablename__ = "performance_reports"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("interview_sessions.id"), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    average_score = db.Column(db.Float, nullable=False, default=0.0)
    technical_knowledge_score = db.Column(db.Float, nullable=False, default=0.0)
    readiness_percentage = db.Column(db.Float, nullable=False, default=0.0)
    strong_topics = db.Column(db.JSON, default=list)
    weak_topics = db.Column(db.JSON, default=list)
    missing_concepts = db.Column(db.JSON, default=list)
    recommendations = db.Column(db.JSON, default=list)
    summary_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "overall_score": round(self.overall_score, 1),
            "average_score": round(self.average_score, 1),
            "technical_knowledge_score": round(self.technical_knowledge_score, 1),
            "readiness_percentage": round(self.readiness_percentage, 1),
            "strong_topics": self.strong_topics or [],
            "weak_topics": self.weak_topics or [],
            "missing_concepts": self.missing_concepts or [],
            "recommendations": self.recommendations or [],
            "summary_notes": self.summary_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
