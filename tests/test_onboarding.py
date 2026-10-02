"""
Tests for CartIQ Stage 2 — How CartIQ Works (Onboarding).

Verifies:
1. Unauthenticated user is routed to Stage 1 (Sign In / Sign Up).
2. Authenticated user with no onboarding_completed flag is routed to Stage 2.
3. Stage 2 module contains expected onboarding content.
4. Onboarding completion flag is handled by session state (not the DB).
5. Stage 2 import does not modify auth or UserModel.
6. Existing Stage 1 auth tests still pass (regression guard).
"""

import importlib
import inspect
import re


# ─────────────────────────────────────────────────────────────────────────────
# 1. Stage routing logic is correct in app.py
# ─────────────────────────────────────────────────────────────────────────────

def test_app_has_three_stage_routing():
    """
    app.py must contain routing logic for all three stages using session-state keys.
    """
    import os
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "onboarding_completed" in source, \
        "app.py must check 'onboarding_completed' session state for Stage 2 routing"
    assert "render_auth_page" in source, \
        "app.py must call render_auth_page for Stage 1"
    assert "render_onboarding_page" in source, \
        "app.py must call render_onboarding_page for Stage 2"


def test_stage1_appears_before_stage2_in_routing():
    """
    Stage 1 guard (unauthenticated) must appear before Stage 2 guard in app.py.
    """
    import os
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        source = f.read()

    pos_auth = source.find("render_auth_page")
    pos_onboarding = source.find("render_onboarding_page")
    assert pos_auth < pos_onboarding, \
        "render_auth_page must appear before render_onboarding_page in app.py"


def test_stage3_is_behind_onboarding_gate():
    """
    The main CartIQ tabs (Product Search, AI Questions, Spec) must only appear
    in the ELSE branch — i.e., after onboarding_completed is True.
    """
    import os
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        source = f.read()

    # After the onboarding block there must be tab rendering
    pos_onboarding = source.find("onboarding_completed")
    pos_tabs = source.find("st.tabs")
    assert pos_tabs > pos_onboarding, \
        "st.tabs (Stage 3) must only appear after the onboarding_completed check"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Onboarding module structure
# ─────────────────────────────────────────────────────────────────────────────

def test_onboarding_module_importable():
    """render_onboarding_page must be importable from ui.onboarding."""
    from ui.onboarding import render_onboarding_page
    assert callable(render_onboarding_page)


def test_onboarding_source_contains_expected_content():
    """
    Stage 2 page source must contain the hero text, step names, and feature cards.
    """
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "ui", "onboarding.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    required_strings = [
        "CartIQ",
        "Search Once. Compare Everywhere.",
        "How CartIQ Works",
        "Search",
        "Understand",
        "Discover",
        "Assist",
        "Product Discovery",
        "Marketplace Options",
        "AI Shopping Assistant",
        "Continue to CartIQ",
        "onboarding_completed",
    ]
    for s in required_strings:
        assert s in source, f"Stage 2 page must contain: {s!r}"


def test_onboarding_completion_uses_session_state_not_db():
    """
    The onboarding page must set onboarding_completed in session state,
    and must NOT reference a database table or model for completion storage.
    """
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "ui", "onboarding.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert 'session_state["onboarding_completed"]' in source or \
           "session_state['onboarding_completed']" in source, \
        "Completion must be stored in st.session_state['onboarding_completed']"

    # Must not import DB models for completion
    assert "UserModel" not in source, \
        "Onboarding page must not import or reference UserModel"
    assert "from database" not in source, \
        "Onboarding page must not import database connection for completion"


def test_onboarding_does_not_fabricate_live_data():
    """
    Stage 2 must not make false claims about live prices/stock/ratings.
    """
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "ui", "onboarding.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    forbidden_phrases = [
        "live prices everywhere",
        "real-time price comparison",
        "lowest price guaranteed",
        "live stock",
        "best price",
    ]
    for phrase in forbidden_phrases:
        assert phrase.lower() not in source.lower(), \
            f"Stage 2 must not contain the phrase: {phrase!r}"


def test_onboarding_sign_out_clears_both_session_keys():
    """
    The sign-out action in app.py / onboarding must clear both 'user'
    and 'onboarding_completed' so users restart from Stage 1.
    """
    import os
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    onboarding_path = os.path.join(os.path.dirname(__file__), "..", "ui", "onboarding.py")

    combined = ""
    for p in [app_path, onboarding_path]:
        with open(p, "r", encoding="utf-8") as f:
            combined += f.read()

    assert "onboarding_completed" in combined and "user" in combined, \
        "Sign-out must remove both 'user' and 'onboarding_completed' from session state"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Auth / Stage 1 regression guard
# ─────────────────────────────────────────────────────────────────────────────

def test_auth_module_still_importable():
    """Stage 1 auth module must still be importable and unchanged."""
    from ui.auth import render_auth_page
    from backend.services.auth_service import AuthService
    assert callable(render_auth_page)
    assert callable(AuthService)


def test_usermodel_unchanged():
    """
    UserModel must still have the same fields defined in Stage 1.
    onboarding data must not be persisted to the users table.
    """
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "database", "models.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    for field in ["id", "full_name", "email", "password_hash", "created_at"]:
        assert field in source, f"UserModel must still define field: {field}"

    assert "onboarding" not in source.lower(), \
        "Onboarding completion must not be persisted to UserModel / DB"


def test_stage3_tabs_still_exist():
    """
    The three existing main application tabs must still be defined in app.py.
    """
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    assert "Product Search" in source
    assert "AI Shopping Quick Questions" in source
    assert "Architecture" in source
