from models import User


def test_user_registration_success(client, app):
    response = client.post("/register", data={
        "name": "Jane Candidate",
        "email": "jane@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to IntelliHire" in response.data or b"Dashboard" in response.data

    with app.app_context():
        user = User.query.filter_by(email="jane@example.com").first()
        assert user is not None
        assert user.name == "Jane Candidate"
        assert user.role == "student"  # Strict role check: cannot register as admin
        assert user.check_password("Password123")


def test_registration_duplicate_email_prevented(client, app):
    # First registration
    client.post("/register", data={
        "name": "Original User",
        "email": "dup@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    })
    # Log out so next request tests the registration endpoint as a guest
    client.get("/logout")

    # Duplicate attempt
    response = client.post("/register", data={
        "name": "Duplicate User",
        "email": "dup@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    }, follow_redirects=True)

    assert b"already exists" in response.data


def test_login_and_logout(client):
    # Register first
    client.post("/register", data={
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "SecretPassword123",
        "confirm_password": "SecretPassword123"
    })
    client.get("/logout")

    # Correct login
    res = client.post("/login", data={
        "email": "loginuser@example.com",
        "password": "SecretPassword123"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Dashboard" in res.data

    # Incorrect login
    client.get("/logout")
    res_bad = client.post("/login", data={
        "email": "loginuser@example.com",
        "password": "WrongPassword"
    }, follow_redirects=True)
    assert b"Invalid email or password" in res_bad.data


def test_student_cannot_access_admin_portal(auth_client):
    res = auth_client.get("/admin", follow_redirects=True)
    assert b"Access denied: Administrator privileges required" in res.data


def test_admin_can_access_admin_portal(admin_client):
    res = admin_client.get("/admin")
    assert res.status_code == 200
    assert b"Administrator Portal" in res.data or b"System Control Center" in res.data
