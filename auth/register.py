from database.mongodb_connection import users_collection
from auth.password_utils import hash_password


def register_user(name, email, password):

    existing_user = users_collection.find_one(
        {"email": email}
    )

    if existing_user:
        return False

    user_data = {
        "name": name,
        "email": email,
        "password": hash_password(password)
    }

    users_collection.insert_one(user_data)

    return True