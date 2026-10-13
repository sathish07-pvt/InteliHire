from routes.auth import auth_bp
from routes.main import main_bp
from routes.resume import resume_bp
from routes.interview import interview_bp
from routes.admin import admin_bp

__all__ = [
    "auth_bp",
    "main_bp",
    "resume_bp",
    "interview_bp",
    "admin_bp",
]
