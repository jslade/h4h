from typing import Optional

from flask import request

from ..models.session import Session
from ..models.user import User


def get_current_user() -> Optional[User]:
    """
    Get the current authenticated user from session cookie or Authorization header.

    Checks for:
    1. h4h_session cookie
    2. Authorization: Bearer <session_id> header

    Returns the User if authenticated, None otherwise.
    """
    session_id: Optional[str] = None

    # Check for session cookie
    session_id = request.cookies.get("h4h_session")

    # If no cookie, check for Authorization header
    if not session_id:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_id = auth_header[7:]  # Remove "Bearer " prefix

    if not session_id:
        return None

    # Get the session
    session = Session.get_by_id(session_id)
    if not session:
        return None

    # Update last used timestamp
    session.update_last_used()

    return session.user
