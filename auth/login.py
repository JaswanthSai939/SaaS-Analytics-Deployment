from database.mongodb_connection import users_collection
from auth.password_utils import verify_password


def login_user(email, password):

    user = users_collection.find_one(
        {"email": email}
    )

    if not user:
        return None

    if verify_password(
        password,
        user["password"]
    ):
        return user

    return None