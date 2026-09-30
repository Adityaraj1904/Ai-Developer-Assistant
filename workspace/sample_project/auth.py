def login(username, password):
    """Authenticate a user."""

    if username == "admin" and password == "admin123":
        return "Login successful"

    return "Invalid username or password"


def logout(username):
    """Log out a user."""

    return f"{username} logged out successfully"