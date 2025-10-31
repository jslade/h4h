from typing import Optional, Self

from passlib.context import CryptContext
from sqlalchemy.orm import Mapped, mapped_column

from ..db import DB, DbSession
from .mixins import PKId, UniquelyNamed

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(DB.Model, PKId, UniquelyNamed):
    """User model for authentication"""

    __tablename__ = "users"

    # username is provided by UniquelyNamed mixin
    password_hash: Mapped[str] = mapped_column(DB.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        """Hash and set the password"""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hash"""
        return pwd_context.verify(password, self.password_hash)

    @classmethod
    def authenticate(
        cls, username: str, password: str, db_session: Optional[DbSession] = None
    ) -> Optional[Self]:
        """Authenticate a user by username and password"""
        user = cls.with_name(username, db_session)
        if user and user.verify_password(password):
            return user
        return None
