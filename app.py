from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# Must be very first Streamlit command
st.set_page_config(
    page_title="CartIQ — Search Once. Compare Everywhere.",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.components import inject_custom_css, inject_floating_chat_widget  # noqa: E402
from ui.pages import render_search_page, render_ai_shopping_page, render_about_page  # noqa: E402
from ui.auth import render_auth_page  # noqa: E402
from ui.onboarding import render_onboarding_page  # noqa: E402


def main():
    inject_custom_css()

    # ── Stage routing ────────────────────────────────────────────────────────
    # Stage 1: Not authenticated → Sign In / Sign Up
    if "user" not in st.session_state or not st.session_state["user"]:
        render_auth_page()

    # Stage 2: Authenticated but onboarding not yet complete → How CartIQ Works
    elif not st.session_state.get("onboarding_completed", False):
        render_onboarding_page()

    # Stage 3: Authenticated and onboarded → Main CartIQ Application
    else:
        _render_main_app()


def _render_main_app():
    """Renders the full CartIQ application (Stage 3)."""

    # Compact top bar with user identity and sign-out
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.caption(
            f"🛒 CartIQ  ·  Signed in as **{st.session_state['user']['full_name']}** "
            f"({st.session_state['user']['email']})"
        )
    with top_right:
        if st.button("Sign Out", key="main_signout"):
            user_data = st.session_state.get("user")
            if user_data and not st.session_state.get("feedback_email_sent", False):
                st.session_state["feedback_email_sent"] = True
                try:
                    from backend.services.email_service import EmailService
                    email_service = EmailService()
                    email_service.send_feedback_email(
                        recipient_email=user_data.get("email"),
                        full_name=user_data.get("full_name")
                    )
                except Exception as e:
                    from utils.logger import logger
                    logger.warning(f"[SignOut] Exception sending feedback email: {e}")
            st.session_state.pop("user", None)
            st.session_state.pop("onboarding_completed", None)
            st.rerun()

    # Three-tab layout: Search & Discovery, AI Shopping Quick Questions, Architecture overview.
    # The product-comparison tab has been replaced with direct marketplace search links.
    tab_search, tab_ai, tab_about = st.tabs([
        "🔍 Product Search & Discovery",
        "🤖 AI Shopping Quick Questions",
        "ℹ️ Architecture & Spec"
    ])

    with tab_search:
        render_search_page()

    with tab_ai:
        render_ai_shopping_page()

    with tab_about:
        render_about_page()

    # Floating CartIQ AI Shopping Assistant widget — injected after all page content
    inject_floating_chat_widget()


if __name__ == "__main__":
    main()
