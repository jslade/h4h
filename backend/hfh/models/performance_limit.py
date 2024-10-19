from typing import TYPE_CHECKING

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import OptionallyNamed, PKId

LOGGER = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from .hashing_interval import HashingInterval


class PerformanceLimit(DB.Model, PKId, OptionallyNamed):
    """ "Defines a target set of attributes for an asic"""

    __tablename__ = "performance_limits"

    # The power limit the machine should be set to
    power_limit: Mapped[int] = mapped_column(DB.Integer, nullable=True)

    # The maximum power uage (kWh) the machine may use in a given interval
    daily_power_budget: Mapped[int] = mapped_column(DB.Integer, nullable=True)
    weekly_power_budget: Mapped[int] = mapped_column(DB.Integer, nullable=True)
    monthly_power_budget: Mapped[int] = mapped_column(DB.Integer, nullable=True)

    intervals: Mapped[list["HashingInterval"]] = relationship(
        "HashingInterval", back_populates="performance_limit"
    )
