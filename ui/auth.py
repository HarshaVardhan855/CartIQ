import streamlit as st
from backend.services.auth_service import AuthService
from database.connection import init_db

# Ensure tables are created when auth page is loaded
init_db()
auth_service = AuthService()

def render_auth_page():
    """
    Renders the Sign In / Sign Up UI for Stage 1.
    """
    st.markdown("<h1 style='text-align: center; color: #6366f1;'>CartIQ</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; margin-bottom: 2rem;'>Search Once. Compare Everywhere.</h4>", unsafe_allow_html=True)

    # Use a container to center the form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_register = st.tabs(["Sign In", "Sign Up"])

        with tab_login:
            with st.form("login_form"):
                st.subheader("Sign In")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)

                if submit:
                    success, user_data, msg = auth_service.authenticate_user(email, password)
                    if success:
                        st.session_state["user"] = user_data
                        st.session_state.pop("feedback_email_sent", None)
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_register:
            with st.form("register_form"):
                st.subheader("Create an Account")
                full_name = st.text_input("Full Name *")
                email_reg = st.text_input("Email *")
                password_reg = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Confirm Password *", type="password")
                submit_reg = st.form_submit_button("Create Account", use_container_width=True)

                if submit_reg:
                    if not full_name or not email_reg or not password_reg or not confirm_password:
                        st.error("All fields are required.")
                    elif password_reg != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        success, msg = auth_service.register_user(full_name, email_reg, password_reg)
                        if success:
                            st.success(f"{msg} You can now Sign In.")
                        else:
                            st.error(msg)

