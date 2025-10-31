from typing import Optional

from ..models.user import User
from ..services.auth_service import AuthService


def get_current_user() -> Optional[User]:
    """
    Get the current authenticated user from session cookie or Authorization header.

    Checks for:
    1. h4h_session cookie
    2. Authorization: Bearer <session_id> header

    Returns the User if authenticated, None otherwise.
    """
    return AuthService.get_current_user()
