from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.resume import Resume, UserSkill
from models.question import Question, Company, SkillCategory
from models.interview import InterviewSession, InterviewQuestion, PerformanceReport

__all__ = [
    "db",
    "User",
    "Resume",
    "UserSkill",
    "Question",
    "Company",
    "SkillCategory",
    "InterviewSession",
    "InterviewQuestion",
    "PerformanceReport",
]
