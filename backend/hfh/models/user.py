from sqlalchemy.orm import Mapped, mapped_column

from ..db import DB
from .mixins import PKId, UniquelyNamed


class User(DB.Model, PKId, UniquelyNamed):
    """User model for authentication"""

    __tablename__ = "users"

    # username is provided by UniquelyNamed mixin
    password_hash: Mapped[str] = mapped_column(DB.String(255), nullable=False)
