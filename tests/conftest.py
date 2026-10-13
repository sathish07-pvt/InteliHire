import pytest
import os
import shutil
from app import create_app
from config import TestConfig
from models import db, User, Question


@pytest.fixture(scope="session")
def app():
    test_app = create_app(TestConfig)
    yield test_app
    # Cleanup test uploads if created
    test_upload = test_app.config["UPLOAD_FOLDER"]
    if os.path.exists(test_upload):
        shutil.rmtree(test_upload, ignore_errors=True)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """Provides a test client pre-authenticated as a student."""
    with app.app_context():
        # Ensure student user exists
        student = User.query.filter_by(email="teststudent@example.com").first()
        if not student:
            student = User(name="Test Student", email="teststudent@example.com", role="student")
            student.set_password("Student@123")
            db.session.add(student)
            db.session.commit()
        s_id = student.id
        s_name = student.name
        s_role = student.role

    with client.session_transaction() as sess:
        sess["user_id"] = s_id
        sess["user_name"] = s_name
        sess["user_role"] = s_role

    return client


@pytest.fixture
def admin_client(client, app):
    """Provides a test client pre-authenticated as an administrator."""
    with app.app_context():
        admin = User.query.filter_by(email="admin@intellihire.com").first()
        if not admin:
            admin = User(name="System Admin", email="admin@intellihire.com", role="admin")
            admin.set_password("Admin@12345")
            db.session.add(admin)
            db.session.commit()
        a_id = admin.id
        a_name = admin.name
        a_role = admin.role

    with client.session_transaction() as sess:
        sess["user_id"] = a_id
        sess["user_name"] = a_name
        sess["user_role"] = a_role

    return client
