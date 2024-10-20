from datetime import timezone
from functools import cached_property
from typing import TYPE_CHECKING

import pytz
import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import OptionallyNamed, PKId

LOGGER = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from .hashing_interval import HashingInterval


class HashingSchedule(DB.Model, PKId, OptionallyNamed):
    __tablename__ = "hashing_schedules"

    timezone_name: Mapped[str] = mapped_column(DB.String, nullable=True)

    intervals: Mapped[list["HashingInterval"]] = relationship(
        "HashingInterval", back_populates="schedule"
    )

    @cached_property
    def timezone(self) -> timezone:
        return pytz.timezone(self.timezone_name) if self.timezone_name else pytz.UTC
