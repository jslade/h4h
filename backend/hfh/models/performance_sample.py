from datetime import datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal, Optional, Self

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

    @classmethod
    def in_range(
        cls,
        asic: "Asic",
        start_time: datetime,
        end_time: Optional[datetime] = None,
    ) -> list[Self]:
        query = cls.query.filter(
            cls.asic_id == asic.id,
            cls.timestamp >= start_time,
        )
        if end_time:
            query = query.filter(cls.timestamp <= end_time)
        return query.order_by(cls.timestamp.asc()).all()

    @classmethod
    def coalesce(
        cls,
        samples: list["PerformanceSample"],
        calc: Literal["average", "max", "min", "sum"] = "average",
        interval_minutes: int = 60, # default group by 60 minutes
    ) -> list["PerformanceSample"]:
        """Coalesce samples into larger intervals by averaging the values"""
        if not samples:
            return []

        coalesced: list["PerformanceSample"] = []
        # first bucket
        bucket: list["PerformanceSample"] = []
        bucket_start: datetime = samples[0].timestamp
        bucket_end: datetime = bucket_start + timedelta(minutes=interval_minutes)

        for sample in samples:
            if sample.timestamp >= bucket_end:
                # time for a new bucket
                if bucket:
                    coalesced.append(cls._coalesce_bucket(bucket, bucket_start, calc, interval_minutes))
                    bucket = []
                bucket_start = sample.timestamp
                bucket_end = bucket_start + timedelta(minutes=interval_minutes)

            bucket.append(sample)

        if bucket:
            coalesced.append(cls._coalesce_bucket(bucket, bucket_start, calc, interval_minutes))

        return coalesced

    @classmethod
    def _coalesce_bucket(
        cls,
        bucket: list["PerformanceSample"],
        bucket_start: datetime,
        calc: Literal["average", "max", "min", "sum"],
        interval_minutes: int,
    ) -> "PerformanceSample":
        count = len(bucket)
        if count == 0:
            raise ValueError("Bucket must contain at least one sample")

        def agg(field: str) -> int | float | Decimal | bool | None:
            values = [getattr(sample, field) for sample in bucket]
            if calc == "average":
                if isinstance(values[0], int | float | Decimal):
                    return sum(values) / Decimal(count)
                else:
                    value_counts = dict()
                    for v in values:
                        value_counts[v] = value_counts.get(v, 0) + 1
                    return max(value_counts.items(), key=lambda item: item[1])[0]
            elif calc == "max":
                return max(values)
            elif calc == "min":
                return min(values)
            elif calc == "sum":
                if isinstance(values[0], int | float | Decimal):
                    return sum(values) / Decimal(count)
                else:
                    return max(values)
            else:
                raise ValueError(f"Unknown calculate method: {calc}")

        sample = PerformanceSample(
            timestamp=bucket_start,
            interval_secs=interval_minutes * 60,
            is_online=bool(agg("is_online")),
            is_hashing=bool(agg("is_hashing")),
            is_stable=bool(agg("is_stable")),
            hash_rate=agg("hash_rate"),
            power=agg("power"),
            power_limit=agg("power_limit"),
            power_per_th=agg("power_per_th"),
            temp=agg("temp"),
            env_temp=agg("env_temp"),
            price_per_kwh=agg("price_per_kwh"),
        )

        return sample

    @classmethod
    def graph(
        cls,
        samples: list["PerformanceSample"],
        *,
        attr: str,
        max_width: int = 60,
    ) -> list[str]:
        """
        Return a bar graph from the given samples, using "*" to indicate the value (plus a label)
        """
        rows: list[tuple[datetime, int | float | Decimal | bool | None]] = []
        for sample in samples:
            value: int | float | Decimal | bool | None = getattr(sample, attr, None)
            rows.append((sample.timestamp, value))

        max_value = max(v for _, v in rows if v is not None) if rows else None
        if isinstance(max_value, int | float | Decimal):
            if max_width > max_value: 
                max_width = int(max_value)

        graph: list[str] = []
        for timestamp, value in rows:
            if isinstance(value, int | float | Decimal) and value > 0:
                n_stars = int(max_width * (1.0 * value / max_value)) if max_value else 0
                stars = "*" * n_stars
            else:
                stars = ""
            row = f"{timestamp}:{stars} {value}" if value is not None else f"{attr}: N/A"
            graph.append(row)

        return graph

    @classmethod
    def print(
        cls,
        samples: list["PerformanceSample"],
        *,
        attr: str,
        max_width: int = 60,
    ) -> None:
        graph = cls.graph(samples, attr=attr, max_width=max_width)
        print("\n".join(graph))
        