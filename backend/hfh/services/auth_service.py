from datetime import UTC, datetime
from typing import Optional

from flask import request
from passlib.context import CryptContext

from ..db import DB, DbSession
from ..models.session import Session
from ..models.user import User

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(password, password_hash)

    @staticmethod
    def set_user_password(user: User, password: str) -> None:
        """Set a user's password"""
        user.password_hash = AuthService.hash_password(password)

    @staticmethod
    def authenticate_user(
        username: str, password: str, db_session: Optional[DbSession] = None
    ) -> Optional[User]:
        """Authenticate a user by username and password"""
        user = User.with_name(username, db_session)
        if user and AuthService.verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    def create_session(
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        db_session: Optional[DbSession] = None,
    ) -> Session:
        """Create a new session for a user"""
        db_session = db_session or DB.session
        session = Session(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db_session.add(session)
        db_session.commit()
        return session

    @staticmethod
    def login(
        username: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        db_session: Optional[DbSession] = None,
    ) -> Optional[Session]:
        """
        Authenticate user and create a session.

        Returns the session if authentication successful, None otherwise.
        """
        user = AuthService.authenticate_user(username, password, db_session)
        if not user:
            return None
        return AuthService.create_session(user, user_agent, ip_address, db_session)

    @staticmethod
    def get_session_by_id(
        session_id: int, db_session: Optional[DbSession] = None
    ) -> Optional[Session]:
        """Get a session by its ID"""
        return Session.with_id(session_id)

    @staticmethod
    def update_session_last_used(
        session: Session, db_session: Optional[DbSession] = None
    ) -> None:
        """Update the last_used_at timestamp of a session"""
        db_session = db_session or DB.session
        session.last_used_at = datetime.now(tz=UTC)
        db_session.commit()

    @staticmethod
    def delete_session(session: Session, db_session: Optional[DbSession] = None) -> None:
        """Delete a session"""
        db_session = db_session or DB.session
        db_session.delete(session)
        db_session.commit()

    @staticmethod
    def get_current_user() -> Optional[User]:
        """
        Get the current authenticated user from session cookie or Authorization header.

        Checks for:
        1. h4h_session cookie
        2. Authorization: Bearer <session_id> header

        Returns the User if authenticated, None otherwise.
        """
        session_id_str: Optional[str] = None

        # Check for session cookie
        session_id_str = request.cookies.get("h4h_session")

        # If no cookie, check for Authorization header
        if not session_id_str:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                session_id_str = auth_header[7:]  # Remove "Bearer " prefix

        if not session_id_str:
            return None

        # Convert to integer
        try:
            session_id = int(session_id_str)
        except ValueError:
            return None

        # Get the session
        session = AuthService.get_session_by_id(session_id)
        if not session:
            return None

        # Update last used timestamp
        AuthService.update_session_last_used(session)

        return session.user
