users = {
    "admin": {
        "name": "Admin User",
        "email": "admin@example.com"
    },
    "aditya": {
        "name": "Aditya",
        "email": "aditya@example.com"
    }
}


def get_user(username):
    """Get user information from the database."""

    return users.get(username)


def list_users():
    """Return all users."""

    return list(users.keys())