import os
from typing import Any

from flask import make_response, request

from ..app import APP
from ..services.auth_service import AuthService


@APP.route("/api/login", methods=["POST"])
def login() -> tuple[dict[str, Any], int]:
    """
    Login endpoint that verifies credentials and creates a session.

    Expects JSON body with:
    - username: str
    - password: str

    Returns:
    - 200: User info and sets session cookie
    - 401: Invalid credentials
    - 400: Missing required fields
    """
    data = request.get_json()
    if not data:
        return {"error": "Request body must be JSON"}, 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "username and password are required"}, 400

    # Authenticate user and create session
    user_agent = request.headers.get("User-Agent")
    ip_address = request.remote_addr
    session = AuthService.login(username, password, user_agent, ip_address)

    if not session:
        return {"error": "Invalid username or password"}, 401

    # Prepare response
    response_data = {
        "id": session.user.id,
        "username": session.user.name,
    }

    response = make_response(response_data, 200)

    # Set cookie
    # Cookie expires in ~10 years (315360000 seconds)
    is_production = os.getenv("FLASK_ENV") == "production"
    response.set_cookie(
        "h4h_session",
        str(session.id),
        max_age=315360000,
        httponly=True,
        secure=is_production,
        samesite="Lax",
    )

    return response


@APP.route("/api/logout", methods=["POST"])
def logout() -> tuple[dict[str, Any], int]:
    """
    Logout endpoint that deletes the session and clears the cookie.

    Returns:
    - 200: Successfully logged out
    - 401: Not authenticated
    """
    user = AuthService.get_current_user()
    if not user:
        return {"error": "Not authenticated"}, 401

    # Logout (delete session)
    AuthService.logout()

    # Prepare response
    response = make_response({"message": "Logged out successfully"}, 200)

    # Clear cookie
    response.set_cookie(
        "h4h_session",
        "",
        max_age=0,
        httponly=True,
        secure=os.getenv("FLASK_ENV") == "production",
        samesite="Lax",
    )

    return response
