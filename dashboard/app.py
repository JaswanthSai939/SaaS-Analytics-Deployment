import sys
import os

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from auth.session_manager import initialize_session

initialize_session()

st.set_page_config(
    page_title="SaaS Analytics",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

login_page = st.Page(
    os.path.join(DASHBOARD_DIR, "login_page.py"),
    title="Login",
    url_path="login"
)

register_page = st.Page(
    os.path.join(DASHBOARD_DIR, "register_page.py"),
    title="Register",
    url_path="register"
)

dashboard_page = st.Page(
    os.path.join(DASHBOARD_DIR, "dashboard_page.py"),
    title="Dashboard",
    url_path="dashboard"
)

insights_page = st.Page(
    os.path.join(DASHBOARD_DIR, "insights_page.py"),
    title="Insights",
    url_path="insights"
)

if st.session_state.logged_in:
    pg = st.navigation(
        [dashboard_page, insights_page],
        position="hidden"
    )
else:
    pg = st.navigation(
        [login_page, register_page],
        position="hidden"
    )

pg.run()