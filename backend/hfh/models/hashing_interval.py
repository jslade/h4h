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

    price_per_kwh: Mapped[Decimal] = mapped_column(
        DB.Numeric(scale=3, precision=6), nullable=True
    )

    order: Mapped[int] = mapped_column(DB.Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(
        DB.Boolean, default=True, server_default="true"
    )

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
        hr, mn = self.daytime_start_hhmm.split(":", 2)
        return time(int(hr), int(mn))

    @cached_property
    def daytime_end(self) -> time:
        if self.daytime_end_hhmm == "00:00":
            return time(23, 59, 59, 999999)
        else:
            hr, mn = self.daytime_end_hhmm.split(":", 2)
            return time(int(hr), int(mn))

    @cached_property
    def is_all_day(self) -> bool:
        return self.daytime_start_hhmm == "00:00" and self.daytime_end_hhmm == "00:00"

    def date_start(self, moment: datetime) -> date:
        tz = moment.tzinfo or (self.schedule.timezone if self.schedule else None)
        year = moment.year
        dt = datetime.strptime(f"{year}/{self.date_start_mmdd}", "%Y/%m/%d")
        if tz:
            dt = dt.replace(tzinfo=tz)

        if dt > moment:
            dt = dt.replace(year=year - 1)
        return dt.date()

    def date_end(self, moment: datetime) -> date:
        tz = moment.tzinfo or (self.schedule.timezone if self.schedule else None)
        year = moment.year
        dt = datetime.strptime(f"{year}/{self.date_end_mmdd}", f"%Y/%m/%d")
        if tz:
            dt = dt.replace(tzinfo=tz)

        d = dt.date()
        if d <= self.date_start(moment):
            d = d.replace(year=year + 1)
        return d

    def is_active_at(self, moment: datetime) -> bool:
        if not self.is_active:
            return False

        t = moment.time()
        d = moment.date()
        LOGGER.debug(
            "Interval.is_active_at",
            start=self.daytime_start,
            end=self.daytime_end,
            time=t,
            date=d,
            moment=moment,
        )

        if t < self.daytime_start or t >= self.daytime_end:
            LOGGER.debug(
                "Interval.is_active_at -- out of time window",
                moment=moment,
                daytime_start=self.daytime_start,
                daytime_end=self.daytime_end,
            )
            return False

        if d < self.date_start(moment) or d > self.date_end(moment):
            LOGGER.debug(
                "Interval.is_active_at -- out of date window",
                moment=moment,
                date_start=self.date_start(moment),
                date_end=self.date_end(moment),
            )
            return False

        if not (self.weekdays_active == "" or self.weekdays_active == "*"):
            weekday_name = self.WEEKDAY_NAME[d.weekday()]
            if weekday_name not in self.weekdays_active:
                LOGGER.debug("Interval.is_active_at -- not an active day")
                return False

        return True

    WEEKDAY_NAME = [
        "Mo",
        "Tu",
        "We",
        "Th",
        "Fr",
        "Sa",
        "Su",
    ]

    def is_hashing_at(self, moment: datetime) -> bool:
        return self.hashing_enabled and self.is_active_at(moment)

    def next_end_time(self, moment: datetime) -> datetime:
        if not self.is_active_at(moment):
            return moment

        d = moment.date()
        t = self.daytime_end

        if self.is_all_day:
            d = self.date_end

        return datetime.combine(date=d, time=t, tzinfo=moment.tzinfo)

    def __repr__(self) -> str:
        return (
            f"<Interval {self.id} \"{self.name}\" "
            f"{'ON' if self.hashing_enabled else 'OFF'} "
            f"{self.date_start_mmdd}-{self.date_end_mmdd} "
            f"{self.daytime_start_hhmm}-{self.daytime_end_hhmm} "
            f"{self.weekdays_active}{'' if self.is_active else ' [inactive]'}>"
        )
