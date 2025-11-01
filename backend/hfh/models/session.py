from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import PKId

if TYPE_CHECKING:
    from .user import User


class Session(DB.Model, PKId):
    """Session model for persistent authentication"""

    __tablename__ = "sessions"

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
