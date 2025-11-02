from datetime import UTC, datetime, timezone
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Self

import pyasic
import structlog
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB, DbSession
from .mixins import PKId, UniquelyNamed

LOGGER = structlog.get_logger(__name__)

if TYPE_CHECKING:
    from .asic_profile import AsicProfile
    from .hashing_interval import HashingInterval
    from .performance_sample import PerformanceSample


class Asic(DB.Model, PKId, UniquelyNamed):
    __tablename__ = "asics"

    address: Mapped[str] = mapped_column(DB.String(40), nullable=False, index=True)
    password: Mapped[str] = mapped_column(DB.String(40), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        DB.Boolean, nullable=False, server_default="true", index=True
    )
    is_online: Mapped[bool] = mapped_column(
        DB.Boolean, nullable=False, server_default="false", index=True
    )
    is_hashing: Mapped[bool] = mapped_column(
        DB.Boolean, nullable=False, server_default="false", index=True
    )
    is_stable: Mapped[bool] = mapped_column(
        DB.Boolean, nullable=False, server_default="false", index=True
    )

    profile_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("asic_profiles.id"), nullable=True
    )
    profile: Mapped[Optional["AsicProfile"]] = relationship("AsicProfile")

    override_interval_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("hashing_intervals.id"), nullable=True
    )
    override_interval: Mapped[Optional["HashingInterval"]] = relationship(
        "HashingInterval"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DB.DateTime, nullable=True, onupdate=datetime.now(tz=UTC)
    )
    changed_at: Mapped[datetime] = mapped_column(DB.DateTime, nullable=True)

    samples: Mapped[list["PerformanceSample"]] = relationship(
        "PerformanceSample",
        back_populates="asic",
        order_by="PerformanceSample.timestamp",
    )

    def local_time(self, dt: Optional[datetime] = None) -> datetime:
        if dt is None:
            dt = datetime.now(tz=self.timezone)

        if not dt.tzinfo:
            dt = dt.replace(tzinfo=UTC)

        return dt.astimezone(self.timezone)

    @cached_property
    def timezone(self) -> timezone:
        if self.profile and self.profile.schedule:
            return self.profile.schedule.timezone
        return UTC  # TODO: should have a global config?

    async def get_miner(self: Self) -> pyasic.AnyMiner:
        LOGGER.debug(
            "get_miner",
            id=self.id,
            name=self.name,
            address=self.address,
        )
        try:
            if self._miner:
                return self._miner
        except AttributeError:
            setattr(self, "_miner", None)

        self._miner = await pyasic.get_miner(self.address)
        if self._miner and self.password:
            self._miner.pwd = self.password
        return self._miner

    @property
    def latest_sample(self) -> Optional["PerformanceSample"]:
        from .performance_sample import PerformanceSample

        return PerformanceSample.latest_for(self)

    def latest_sample_before_interval(
        self, interval: "HashingInterval"
    ) -> Optional["PerformanceSample"]:
        from .performance_sample import PerformanceSample

        return PerformanceSample.latest_for(
            self,
            before_interval=interval,
        )

    @classmethod
    def all_active(cls, db_session: Optional[DbSession] = None) -> list[Self]:
        db_session = db_session or DB.session
        stmt = select(cls).order_by(cls.name).filter_by(is_active=True)
        return [a for a in db_session.scalars(stmt)]


class AsicStatus(str, Enum):
    offline = "offline"
    hashing = "hashing"
    transitioning = "transitioning"
    paused = "paused"
    error = "error"

    @staticmethod
    def for_asic(asic: Asic) -> Self:
        if asic.is_hashing:
            if asic.is_stable:
                return AsicStatus.hashing
            else:
                return AsicStatus.transitioning
        else:
            if asic.is_online:
                return AsicStatus.paused
            else:
                return AsicStatus.offline
