import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional, Self

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB, DbSession

if TYPE_CHECKING:
    from .user import User


class Session(DB.Model):
    """Session model for persistent authentication"""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        DB.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("users.id"), nullable=False, index=True
    )
    user: Mapped["User"] = relationship("User")

    user_agent: Mapped[Optional[str]] = mapped_column(DB.String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(DB.String(45), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DB.DateTime, nullable=False, default=lambda: datetime.now(tz=UTC)
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DB.DateTime, nullable=False, default=lambda: datetime.now(tz=UTC)
    )

    @classmethod
    def create_session(
        cls,
        user: "User",
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        db_session: Optional[DbSession] = None,
    ) -> Self:
        """Create a new session for a user"""
        db_session = db_session or DB.session
        session = cls(
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db_session.add(session)
        db_session.commit()
        return session

    @classmethod
    def get_by_id(
        cls, session_id: str, db_session: Optional[DbSession] = None
    ) -> Optional[Self]:
        """Get a session by its ID"""
        db_session = db_session or DB.session
        stmt = select(cls).where(cls.id == session_id)
        return db_session.scalar(stmt)

    def update_last_used(self, db_session: Optional[DbSession] = None) -> None:
        """Update the last_used_at timestamp"""
        db_session = db_session or DB.session
        self.last_used_at = datetime.now(tz=UTC)
        db_session.commit()

    def delete(self, db_session: Optional[DbSession] = None) -> None:
        """Delete this session"""
        db_session = db_session or DB.session
        db_session.delete(self)
        db_session.commit()
