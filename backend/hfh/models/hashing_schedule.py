from typing import TYPE_CHECKING

import structlog
from sqlalchemy.orm import Mapped, relationship

from ..db import DB
from .mixins import OptionallyNamed, PKId

LOGGER = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from .hashing_interval import HashingInterval


class HashingSchedule(DB.Model, PKId, OptionallyNamed):
    __tablename__ = "hashing_schedules"

    intervals: Mapped[list["HashingInterval"]] = relationship(
        "HashingInterval", back_populates="schedule"
    )
