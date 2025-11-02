from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Self

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import PKId

LOGGER = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from .asic import Asic
    from .hashing_interval import HashingInterval


class PerformanceSample(DB.Model, PKId):
    """Records the performance characteristics of an asic at a specific time"""

    __tablename__ = "performance_samples"

    hashing_interval_id: Mapped[int | None] = mapped_column(
        DB.Integer,
        DB.ForeignKey("hashing_intervals.id"),
        nullable=True,
        index=True,
    )
    hashing_interval: Mapped[Optional["HashingInterval"]] = relationship(
        "HashingInterval"
    )

    timestamp: Mapped[datetime] = mapped_column(DB.DateTime, nullable=False, index=True)
    interval_secs: Mapped[int] = mapped_column(DB.Integer, nullable=False)

    is_online: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)
    is_hashing: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)
    is_stable: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)
    hash_rate: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    power: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    power_limit: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    power_per_th: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    temp: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    env_temp: Mapped[int] = mapped_column(DB.Integer, nullable=False)
    price_per_kwh: Mapped[Decimal] = mapped_column(DB.Numeric(scale=3, precision=6))

    # With this scaling factor:
    # - convert power in W to kW  --> 0.001
    # - convert price_per_kwh in $/kwh to $/kws --> 1/3600
    HASH_COST_SCALE = Decimal("0.001") / Decimal(3600)

    @property
    def cost_per_sec(self) -> Decimal:
        """Cost per second in $ / s"""
        return self.power * self.price_per_kwh * self.HASH_COST_SCALE

    @property
    def cost_per_hr(self) -> Decimal:
        return self.cost_per_sec * Decimal(3600)

    @property
    def cost_per_th(self) -> Decimal:
        """Cost per TH $ / TH"""
        return self.cost_per_sec / self.hash_rate if self.hash_rate else Decimal(0)

    @property
    def hash_cost(self) -> Decimal:
        """Cost for the sample period"""
        return self.cost_per_sec * Decimal(self.interval_secs)

    asic_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("asics.id"), nullable=False, index=True
    )
    asic: Mapped["Asic"] = relationship("Asic", back_populates="samples")

    @classmethod
    def latest_for(
        cls,
        asic: "Asic",
        *,
        before_interval: Optional["HashingInterval"] = None,
    ) -> Optional[Self]:
        query = cls.query.filter(cls.asic_id == asic.id)
        if before_interval:
            query = query.filter(cls.hashing_interval_id != before_interval.id)
        return query.order_by(cls.timestamp.desc()).first()
