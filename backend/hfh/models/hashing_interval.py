from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Optional

import structlog
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import DB
from .mixins import OptionallyNamed, PKId

if TYPE_CHECKING:
    from .hashing_schedule import HashingSchedule
    from .performance_limit import PerformanceLimit

LOGGER = structlog.get_logger(__name__)


class HashingInterval(DB.Model, PKId, OptionallyNamed):
    __tablename__ = "hashing_intervals"

    daytime_start_hhmm: Mapped[str] = mapped_column(DB.String, nullable=False)
    daytime_end_hhmm: Mapped[str] = mapped_column(DB.String, nullable=False)

    date_start_mmdd: Mapped[str] = mapped_column(DB.String, nullable=False)
    date_end_mmdd: Mapped[str] = mapped_column(DB.String, nullable=False)

    weekdays_active: Mapped[str] = mapped_column(DB.String, nullable=False)
    hashing_enabled: Mapped[bool] = mapped_column(DB.Boolean, nullable=False)

    price_per_kwh: Mapped[Decimal] = mapped_column(DB.Numeric(scale=3, precision=6))

    schedule_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("hashing_schedules.id"), nullable=True
    )
    schedule: Mapped[list["HashingSchedule"]] = relationship(
        "HashingSchedule", back_populates="intervals"
    )

    performance_limit_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("performance_limits.id"), nullable=True
    )
    performance_limit: Mapped[Optional["PerformanceLimit"]] = relationship(
        "PerformanceLimit", back_populates="intervals"
    )

    @cached_property
    def daytime_start(self) -> time:
        dt = datetime.strptime(self.daytime_start_hhmm, "%H:%M")
        return dt.time()

    @cached_property
    def daytime_end(self) -> time:
        if self.daytime_end_hhmm == "00:00":
            return time(23, 59, 59, 999999)
        dt = datetime.strptime(self.daytime_end_hhmm, "%H:%M")
        return dt.time()

    @cached_property
    def date_start(self) -> date:
        year = date.today().year
        dt = datetime.strptime(f"{year}/{self.date_start_mmdd}", "%Y/%m/%d")
        return dt.date()

    @cached_property
    def date_end(self) -> date:
        year = date.today().year
        dt = datetime.strptime(f"{year}/{self.date_end_mmdd}", f"%Y/%m/%d")
        d = dt.date()
        if d <= self.date_start:
            d = d.replace(year=year + 1)
        return d

    def is_active_at(self, moment: datetime) -> bool:
        t = moment.time()
        if t < self.daytime_start or t > self.daytime_end:
            return False

        return True

    def is_hashing_at(self, moment: datetime) -> bool:
        return self.hashing_enabled and self.is_active_at(moment)
