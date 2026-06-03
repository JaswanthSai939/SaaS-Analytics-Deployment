import sys
import os

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)

sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from auth.login import login_user
from auth.google_auth import (
    oauth2,
    get_google_user_info
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display:none;
    }

    [data-testid="collapsedControl"] {
        display:none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Redirect immediately if already logged in
if st.session_state.get("logged_in"):
    st.switch_page("dashboard/pages/dashboard.py")
    st.stop()

# Dynamically read redirect URI from secrets (works locally and on Streamlit Cloud)
REDIRECT_URI = st.secrets.get("oauth", {}).get(
    "redirect_uri",
    "http://localhost:8501"
)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    st.title("Login")

    email = st.text_input(
        "Email"
    )

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

                st.session_state.user_name = (
                    user["name"]
                )

                st.session_state.user_email = (
                    user["email"]
                )

                st.rerun()

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
        redirect_uri=REDIRECT_URI,
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
                google_user.get(
                    "name",
                    "Google User"
                )
            )

            st.session_state.user_email = (
                google_user.get(
                    "email",
                    ""
                )
            )

            st.session_state.user_picture = (
                google_user.get(
                    "picture",
                    ""
                )
            )

            st.success(
                "Google Login Successful!"
            )

            st.rerun()

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
            "dashboard/register_page.py"
        )