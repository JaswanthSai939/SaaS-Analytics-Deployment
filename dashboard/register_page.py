import sys
import os

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from auth.register import register_user

st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:

    st.title("Create Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Register",
        use_container_width=True
    ):

        if not name or not email or not password:

            st.error("Please fill all fields")

        else:

            success = register_user(
                name,
                email,
                password
            )

            if success:

                st.success(
                    "Registration Successful! Please login."
                )

            else:

                st.error(
                    "Email Already Exists"
                )

    st.markdown("---")

    st.markdown(
        "Already have an account?"
    )

    if st.button(
        "Back to Login",
        use_container_width=True
    ):
        st.switch_page("login")