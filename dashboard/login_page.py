import sys
import os

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from auth.login import login_user
from auth.google_auth import oauth2, get_google_user_info

# Hide sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}
[data-testid="collapsedControl"] {display:none;}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    st.title("Login")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        if not email or not password:

            st.error(
                "Please fill all fields"
            )

        else:

            user = login_user(
                email,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user_name = user["name"]
                st.session_state.user_email = user["email"]

                st.switch_page(
                    os.path.join(
                        DASHBOARD_DIR,
                        "dashboard_page.py"
                    )
                )

            else:

                st.error(
                    "Invalid Credentials"
                )

    st.markdown("---")

    st.subheader(
        "Or Continue With Google"
    )

    result = oauth2.authorize_button(
        name="Continue with Google",
        redirect_uri="https://saas-analytics-deployment-hhwehhkbpyihotsrxylkh.streamlit.app/oauth2callback",
        scope="openid email profile",
        key="google_login"
    )

    if result:

        google_user = get_google_user_info(
            result
        )

        if google_user:

            st.session_state.logged_in = True

            st.session_state.user_name = (
                google_user["name"]
            )

            st.session_state.user_email = (
                google_user["email"]
            )

            st.session_state.user_picture = (
                google_user["picture"]
            )

            st.switch_page(
                os.path.join(
                    DASHBOARD_DIR,
                    "dashboard_page.py"
                )
            )

        else:

            st.error(
                "Unable to fetch Google user information"
            )

    st.markdown("---")

    st.write(
        "Don't have an account?"
    )

    if st.button(
        "Create Account",
        use_container_width=True
    ):

        st.switch_page(
            os.path.join(
                DASHBOARD_DIR,
                "register_page.py"
            )
        )