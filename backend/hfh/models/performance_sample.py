from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import PKId

LOGGER = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from .asic import Asic


class PerformanceSample(DB.Model, PKId):
    """Records the performance characteristics of an asic at a specific time"""

    __tablename__ = "performance_samples"

    timestamp: Mapped[datetime] = mapped_column(DB.DateTime, nullable=False, index=True)
    interval_secs: Mapped[int] = mapped_column(DB.Integer, nullable=False)

    is_online: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)
    is_hashing: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)
    is_stable: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)
    power: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    power_per_th: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    temp: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    env_temp: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    price_per_kwh: Mapped[Decimal] = mapped_column(DB.Numeric(scale=3, precision=6))

    asic_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("asics.id"), nullable=False, index=True
    )
    asic: Mapped["Asic"] = relationship("Asic", back_populates="samples")
