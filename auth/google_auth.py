import requests
import streamlit as st

from streamlit_oauth import OAuth2Component

CLIENT_ID = st.secrets[
    "GOOGLE_CLIENT_ID"
]

CLIENT_SECRET = st.secrets[
    "GOOGLE_CLIENT_SECRET"
]

AUTHORIZE_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)

TOKEN_URL = (
    "https://oauth2.googleapis.com/token"
)

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL
)

def get_google_user_info(result):

    try:

        access_token = (
            result["token"]["access_token"]
        )

        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={
                "Authorization":
                f"Bearer {access_token}"
            }
        )

        if response.status_code == 200:

            return response.json()

        return None

    except Exception as e:

        print(e)

        return None