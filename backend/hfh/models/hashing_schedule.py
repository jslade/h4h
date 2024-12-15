from datetime import timezone
from functools import cached_property
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

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
        "HashingInterval",
        back_populates="schedule",
        order_by="HashingInterval.is_active, HashingInterval.order, HashingInterval.name",
    )

    @cached_property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name) if self.timezone_name else ZoneInfo("UTC")
