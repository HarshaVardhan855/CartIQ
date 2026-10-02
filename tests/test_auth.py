import pytest
from backend.services.auth_service import AuthService
from database.connection import init_db, SessionLocal
from database.models import UserModel, Base

@pytest.fixture(scope="module")
def setup_db():
    init_db()
    db = SessionLocal()
    # clean up users table
    db.query(UserModel).delete()
    db.commit()
    yield
    db.query(UserModel).delete()
    db.commit()
    db.close()

@pytest.fixture
def auth_service(setup_db):
    return AuthService()

def test_successful_registration(auth_service):
    success, msg = auth_service.register_user("Test User", "test@example.com", "securepassword")
    assert success is True
    assert msg == "User registered successfully."

def test_duplicate_email_registration(auth_service):
    # Already registered in previous test
    success, msg = auth_service.register_user("Test User 2", "test@example.com", "securepassword2")
    assert success is False
    assert msg == "Email is already registered."

def test_invalid_email(auth_service):
    success, msg = auth_service.register_user("Invalid Email User", "not-an-email", "securepassword")
    assert success is False
    assert msg == "Invalid email address format."

def test_missing_required_fields(auth_service):
    success, msg = auth_service.register_user("", "missing@example.com", "securepassword")
    assert success is False
    assert msg == "Full Name is required."

def test_password_security(auth_service):
    success, msg = auth_service.register_user("Short Pass User", "short@example.com", "short")
    assert success is False
    assert msg == "Password must be at least 8 characters long."

def test_successful_login(auth_service):
    success, user_data, msg = auth_service.authenticate_user("test@example.com", "securepassword")
    assert success is True
    assert user_data is not None
    assert user_data["email"] == "test@example.com"
    assert user_data["full_name"] == "Test User"
    assert "password_hash" not in user_data  # Should not expose password hash in session data
    assert "password" not in user_data

def test_incorrect_password(auth_service):
    success, user_data, msg = auth_service.authenticate_user("test@example.com", "wrongpassword")
    assert success is False
    assert user_data is None
    assert msg == "Invalid email or password."

def test_unknown_email(auth_service):
    success, user_data, msg = auth_service.authenticate_user("unknown@example.com", "securepassword")
    assert success is False
    assert user_data is None
    assert msg == "Invalid email or password."
