from datetime import datetime
from models import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_skills = db.Column(db.JSON, default=list)  # list of extracted skill strings
    recommended_domains = db.Column(db.JSON, default=list)  # suggested interview tracks
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "parsed_skills": self.parsed_skills or [],
            "recommended_domains": self.recommended_domains or [],
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(30), default="Intermediate")
    source = db.Column(db.String(20), default="extracted")  # 'extracted' or 'manual'
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "skill_name", name="uq_user_skill"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "skill_name": self.skill_name,
            "proficiency": self.proficiency,
            "source": self.source,
        }
