"""
Stage 2: How CartIQ Works — Onboarding Page.

Shown to authenticated users BEFORE they enter the main CartIQ application.
Completion is tracked via st.session_state["onboarding_completed"] = True.
"""

import streamlit as st


def render_onboarding_page():
    """
    Renders the Stage 2 onboarding/how-it-works screen.
    Authenticated users see this before the main CartIQ application.
    Clicking "Continue to CartIQ" sets onboarding_completed=True in session state.
    """

    user_name = st.session_state.get("user", {}).get("full_name", "there")

    # ── Top Sign-Out row ─────────────────────────────────────────────────────
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.caption(f"Signed in as **{st.session_state['user']['email']}**")
    with top_right:
        if st.button("Sign Out", key="onboarding_signout"):
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

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <div style="font-size:3rem;">🛒</div>
            <h1 style="color:#6366f1; margin:0.25rem 0;">CartIQ</h1>
            <h3 style="color:#475569; font-weight:600; margin:0.25rem 0;">
                Search Once. Compare Everywhere.
            </h3>
            <p style="color:#64748b; font-size:1.1rem; max-width:600px; margin:0.75rem auto 0;">
                CartIQ helps you discover products, explore marketplace options, and get
                AI-powered shopping guidance — all from one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── How It Works: 4-step flow ────────────────────────────────────────────
    st.markdown(
        "<h2 style='text-align:center; color:#1e293b;'>How CartIQ Works</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#64748b; margin-bottom:1.5rem;'>"
        "Four simple steps from search to smarter shopping."
        "</p>",
        unsafe_allow_html=True,
    )

    step_col1, step_col2, step_col3, step_col4 = st.columns(4)

    _step_card(step_col1, "🔎", "Search",
               "Tell CartIQ what you're looking for — in plain language.")
    _step_card(step_col2, "🤖", "Understand",
               "CartIQ interprets your shopping request and extracts key intent.")
    _step_card(step_col3, "🛍️", "Discover",
               "Explore real marketplace destinations on Amazon, Flipkart, and Meesho.")
    _step_card(step_col4, "💡", "Assist",
               "Ask the AI Shopping Assistant for product and buying guidance.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Feature Cards ────────────────────────────────────────────────────────
    st.markdown(
        "<h2 style='text-align:center; color:#1e293b;'>What can you do with CartIQ?</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)

    _feature_card(feat_col1, "🔎", "Product Discovery",
                  "Search for products using natural language. No complex filters required.")
    _feature_card(feat_col2, "🛍️", "Marketplace Options",
                  "Explore real marketplace destinations such as Amazon, Flipkart, and Meesho.")
    _feature_card(feat_col3, "🤖", "AI Shopping Assistant",
                  "Ask questions about product features, specifications, and buying considerations.")
    _feature_card(feat_col4, "💡", "Smarter Shopping",
                  "Get useful guidance before deciding what to buy — without the noise.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── AI Assistant Examples ────────────────────────────────────────────────
    st.markdown(
        "<h2 style='text-align:center; color:#1e293b;'>Need help deciding?</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#64748b;'>"
        "The CartIQ AI Shopping Assistant can answer questions like:"
        "</p>",
        unsafe_allow_html=True,
    )

    ai_col1, ai_col2 = st.columns(2)
    example_questions = [
        "💻 What features should I look for in an HP Victus laptop?",
        "🎧 What should I check before buying wireless earbuds?",
        "📱 How do I compare two smartphones side by side?",
        "🛒 Which marketplace suits my type of purchase?",
    ]
    for i, q in enumerate(example_questions):
        target = ai_col1 if i % 2 == 0 else ai_col2
        target.markdown(
            f"""
            <div style="
                background:#f8fafc;
                border:1.5px solid #e2e8f0;
                border-radius:10px;
                padding:0.75rem 1rem;
                margin-bottom:0.75rem;
                font-size:0.93rem;
                color:#334155;
            ">{q}</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Honest data note ─────────────────────────────────────────────────────
    st.info(
        "**ℹ️ A note on marketplace data:** CartIQ connects your search experience "
        "directly with marketplace destinations. When verified live marketplace data "
        "is not available, CartIQ sends you to the real marketplace search page rather "
        "than inventing product information.",
        icon=None,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── CTA ─────────────────────────────────────────────────────────────────
    cta_left, cta_center, cta_right = st.columns([2, 2, 2])
    with cta_center:
        if st.button("🚀 Continue to CartIQ", use_container_width=True, type="primary"):
            st.session_state["onboarding_completed"] = True
            st.rerun()

    st.markdown(
        "<p style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:0.5rem;'>"
        f"Welcome, {user_name}! You're about to enter the CartIQ experience."
        "</p>",
        unsafe_allow_html=True,
    )


# ── Helper renderers ──────────────────────────────────────────────────────────

def _step_card(col, icon: str, title: str, body: str):
    col.markdown(
        f"""
        <div style="
            background:#ffffff;
            border:1.5px solid #e8e5ff;
            border-radius:14px;
            padding:1.25rem 1rem;
            text-align:center;
            height:100%;
            box-shadow:0 2px 12px rgba(99,102,241,0.08);
        ">
            <div style="font-size:2rem;">{icon}</div>
            <h4 style="color:#6366f1; margin:0.5rem 0 0.4rem;">{title}</h4>
            <p style="color:#64748b; font-size:0.88rem; margin:0;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _feature_card(col, icon: str, title: str, body: str):
    col.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#f8fafc,#f0f0ff);
            border:1.5px solid #e2e8f0;
            border-radius:14px;
            padding:1.25rem 1rem;
            text-align:center;
            height:100%;
            box-shadow:0 2px 10px rgba(0,0,0,0.04);
        ">
            <div style="font-size:1.8rem;">{icon}</div>
            <h4 style="color:#1e293b; margin:0.5rem 0 0.4rem;">{title}</h4>
            <p style="color:#64748b; font-size:0.85rem; margin:0;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
