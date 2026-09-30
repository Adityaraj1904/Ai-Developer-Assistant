from auth import login
from database import get_user


def main():
    username = "admin"
    password = "admin123"

    result = login(username, password)

    print(result)

    if result == "Login successful":
        user = get_user(username)
        print("User:", user)


if __name__ == "__main__":
    main()