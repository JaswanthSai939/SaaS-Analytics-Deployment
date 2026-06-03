import os
import requests

from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

oauth2 = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL
)


def get_google_user_info(result):

    try:

        if not result:
            return None

        # Handle both possible result structures
        token = result.get("token") or result

        access_token = (
            token.get("access_token")
            if isinstance(token, dict)
            else None
        )

        if not access_token:
            print("Google Login Error: No access token found in result")
            return None

        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        print(
            f"Google API Error [{response.status_code}]:",
            response.text
        )

        return None

    except requests.exceptions.Timeout:
        print("Google Login Error: Request timed out")
        return None

    except requests.exceptions.RequestException as e:
        print("Google Login Error (network):", e)
        return None

    except Exception as e:
        print("Google Login Error:", e)
        return None