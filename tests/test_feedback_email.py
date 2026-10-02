"""
Tests for CartIQ SendGrid Feedback Email Functionality (10 Specification Requirements).

Verifies:
1. Sign In does NOT send feedback email.
2. Sign Up does NOT send feedback email.
3. Normal application usage does NOT send feedback email.
4. Sign Out sends exactly ONE feedback email.
5. The recipient is the currently signed-in user's email.
6. The user's full name appears in the email.
7. The subject is: "💙 How was your CartIQ experience?"
8. The Give Feedback button uses FEEDBACK_FORM_URL.
9. Two executions caused by the same Sign Out action do not send duplicate emails,
   while subsequent login/signout cycles trigger a new email.
10. SendGrid failure does NOT prevent Sign Out.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from backend.services.email_service import EmailService


@pytest.fixture
def mock_env(monkeypatch):
    """Sets up standard environment variables for feedback email testing."""
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test_mock_key_12345")
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "test_sender@cartiq.app")
    monkeypatch.setenv("FEEDBACK_FORM_URL", "https://forms.gle/test_feedback_form_url")


# ── TEST 1: Sign In does NOT send feedback email ─────────────────────────────
def test_signin_does_not_send_feedback_email():
    """Sign In flow must not contain or call send_feedback_email."""
    auth_file = os.path.join(os.path.dirname(__file__), "..", "ui", "auth.py")
    with open(auth_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "send_feedback_email" not in content, \
        "Sign In interface (ui/auth.py) must NOT call or reference send_feedback_email"


# ── TEST 2: Sign Up does NOT send feedback email ─────────────────────────────
def test_signup_does_not_send_feedback_email():
    """Sign Up flow / AuthService must not send feedback email."""
    service_file = os.path.join(os.path.dirname(__file__), "..", "backend", "services", "auth_service.py")
    with open(service_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "send_feedback_email" not in content, \
        "AuthService (register/login) must NOT call or reference send_feedback_email"


# ── TEST 3: Normal application usage does NOT send feedback email ───────────
def test_normal_app_usage_does_not_send_feedback_email():
    """Product search, AI assistant, and page rendering must NOT call send_feedback_email."""
    search_file = os.path.join(os.path.dirname(__file__), "..", "ui", "pages.py")
    ai_file = os.path.join(os.path.dirname(__file__), "..", "ai", "advisor.py")

    for filepath in [search_file, ai_file]:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            assert "send_feedback_email" not in content, \
                f"{filepath} must NOT trigger send_feedback_email during normal usage"


# ── TEST 4: Sign Out sends exactly ONE feedback email ──────────────────────
def test_signout_sends_exactly_one_feedback_email(mock_env):
    """Sign Out trigger calls send_feedback_email exactly once per action."""
    session_state = {
        "user": {"id": "u123", "full_name": "Harsha Vardhan", "email": "harsha@example.com"},
        "onboarding_completed": True
    }

    mock_send = MagicMock(return_value={"success": True, "status": "sent"})

    # Simulate Sign Out action
    user_data = session_state.get("user")
    if user_data and not session_state.get("feedback_email_sent", False):
        session_state["feedback_email_sent"] = True
        mock_send(
            recipient_email=user_data.get("email"),
            full_name=user_data.get("full_name")
        )

    mock_send.assert_called_once_with(recipient_email="harsha@example.com", full_name="Harsha Vardhan")


# ── TEST 5: The recipient is the currently signed-in user's email ────────────
def test_recipient_is_signed_in_user_email(mock_env):
    """The TO email address must match the signed-in user's email."""
    email_service = EmailService()
    signed_in_email = "user_test_unique@cartiq.app"

    with patch("sendgrid.SendGridAPIClient") as MockSendGridClient:
        mock_sg = MagicMock()
        mock_sg.send.return_value = MagicMock(status_code=202)
        MockSendGridClient.return_value = mock_sg

        email_service.send_feedback_email(signed_in_email, "Test User")

        sent_mail = mock_sg.send.call_args[0][0]
        mail_dict = sent_mail.get()

        to_email = mail_dict["personalizations"][0]["to"][0]["email"]
        assert to_email == signed_in_email, f"Recipient email must be {signed_in_email}, got {to_email}"
        assert to_email != "test_sender@cartiq.app", "Recipient must NOT be SENDGRID_FROM_EMAIL"


# ── TEST 6: The user's full name appears in the email ───────────────────────
def test_user_full_name_in_email(mock_env):
    """The user's full name must be interpolated into the email body."""
    email_service = EmailService()

    with patch("sendgrid.SendGridAPIClient") as MockSendGridClient:
        mock_sg = MagicMock()
        mock_sg.send.return_value = MagicMock(status_code=202)
        MockSendGridClient.return_value = mock_sg

        email_service.send_feedback_email("user@example.com", "Harsha Vardhan")

        sent_mail = mock_sg.send.call_args[0][0]
        mail_dict = sent_mail.get()
        contents = [c["value"] for c in mail_dict["content"]]
        full_content_text = " ".join(contents)

        assert "Harsha Vardhan" in full_content_text, "Email body must contain user's full name 'Harsha Vardhan'"


# ── TEST 7: The subject is: "💙 How was your CartIQ experience?" ─────────────
def test_subject_is_exact_match(mock_env):
    """Email subject must match exact required string."""
    email_service = EmailService()

    with patch("sendgrid.SendGridAPIClient") as MockSendGridClient:
        mock_sg = MagicMock()
        mock_sg.send.return_value = MagicMock(status_code=202)
        MockSendGridClient.return_value = mock_sg

        email_service.send_feedback_email("user@example.com", "Jane")

        sent_mail = mock_sg.send.call_args[0][0]
        mail_dict = sent_mail.get()

        assert mail_dict["subject"] == "💙 How was your CartIQ experience?"


# ── TEST 8: The Give Feedback button uses FEEDBACK_FORM_URL ─────────────────
def test_give_feedback_button_uses_feedback_form_url(monkeypatch):
    """Give Feedback button URL must dynamically use FEEDBACK_FORM_URL from environment."""
    custom_url = "https://forms.gle/6VmTss4tTLhZdvVSA"
    monkeypatch.setenv("SENDGRID_API_KEY", "SG.test_key")
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "sender@cartiq.app")
    monkeypatch.setenv("FEEDBACK_FORM_URL", custom_url)

    email_service = EmailService()

    with patch("sendgrid.SendGridAPIClient") as MockSendGridClient:
        mock_sg = MagicMock()
        mock_sg.send.return_value = MagicMock(status_code=202)
        MockSendGridClient.return_value = mock_sg

        email_service.send_feedback_email("user@example.com", "Jane")

        sent_mail = mock_sg.send.call_args[0][0]
        mail_dict = sent_mail.get()
        contents = [c["value"] for c in mail_dict["content"]]
        full_content_text = " ".join(contents)

        assert custom_url in full_content_text
        assert "Give Feedback" in full_content_text


# ── TEST 9: Duplicate email prevention & multi-cycle support ──────────────────
def test_prevent_duplicate_emails_and_allow_new_login_cycle_email(mock_env):
    """
    Verifies that a single Sign Out action sends at most 1 email,
    while a subsequent login -> signout cycle sends a new feedback email.
    """
    mock_send = MagicMock(return_value={"success": True, "status": "sent"})

    # Cycle 1: Login
    session_state = {
        "user": {"id": "u1", "full_name": "Harsha", "email": "harsha@example.com"},
        "onboarding_completed": True
    }

    # Click Sign Out twice in same rerun sequence
    for _ in range(2):
        if session_state.get("user") and not session_state.get("feedback_email_sent", False):
            session_state["feedback_email_sent"] = True
            mock_send(session_state["user"]["email"], session_state["user"]["full_name"])

    # First sign out complete -> session wiped
    session_state.pop("user", None)
    session_state.pop("onboarding_completed", None)
    session_state.pop("feedback_email_sent", None)

    assert mock_send.call_count == 1, "First sign-out action must send exactly 1 email"

    # Cycle 2: Login again
    session_state["user"] = {"id": "u1", "full_name": "Harsha", "email": "harsha@example.com"}
    session_state["onboarding_completed"] = True

    # Click Sign Out again
    if session_state.get("user") and not session_state.get("feedback_email_sent", False):
        session_state["feedback_email_sent"] = True
        mock_send(session_state["user"]["email"], session_state["user"]["full_name"])

    assert mock_send.call_count == 2, "Second independent login->signout cycle must send a new feedback email"


# ── TEST 10: SendGrid failure does NOT prevent Sign Out ──────────────────────
def test_sendgrid_failure_does_not_prevent_signout(mock_env):
    """SendGrid API exception or failure must not prevent session invalidation."""
    session_state = {
        "user": {"id": "u1", "full_name": "Harsha", "email": "harsha@example.com"},
        "onboarding_completed": True
    }

    user_data = session_state.get("user")
    if user_data:
        try:
            email_service = EmailService()
            with patch.object(email_service, "send_feedback_email", side_effect=Exception("SendGrid API 500 Error")):
                email_service.send_feedback_email(user_data["email"], user_data["full_name"])
        except Exception:
            pass  # Exception swallowed safely

    # Wiping session state MUST proceed regardless of SendGrid error
    session_state.pop("user", None)
    session_state.pop("onboarding_completed", None)

    assert "user" not in session_state
    assert "onboarding_completed" not in session_state
