from decimal import Decimal
from typing import Optional, Self

from pydantic import AwareDatetime, BaseModel

from ..models.asic import Asic, AsicStatus
from ..services.schedule_service import ScheduleService


class AsicSummaryDto(BaseModel):
    name: str
    status: str
    updated_at: AwareDatetime
    changed_at: AwareDatetime
    sampled_at: Optional[AwareDatetime]
    interval_name: Optional[str]
    interval_until: Optional[AwareDatetime]
    hash_rate: Optional[int]
    power: Optional[int]
    power_limit: Optional[int]
    power_per_th: Optional[int]
    temp: Optional[int]
    env_temp: Optional[int]

    @classmethod
    def from_asic(cls, asic: Asic) -> Self:
        sample = asic.latest_sample

        updated_at = asic.local_time(asic.updated_at)
        changed_at = asic.local_time((asic.changed_at or asic.updated_at))
        sampled_at = asic.local_time(sample.timestamp) if sample else None

        scheduler = ScheduleService()
        moment = asic.local_time()
        interval = scheduler.get_current_interval(
            asic, moment=moment, temp=sample.env_temp if sample else None
        )

        return AsicSummaryDto(
            name=asic.name,
            status=AsicStatus.for_asic(asic),
            updated_at=updated_at,
            changed_at=changed_at,
            sampled_at=sampled_at,
            interval_name=(interval.name or "null") if interval else None,
            interval_until=interval.next_end_time(moment) if interval else None,
            hash_rate=sample.hash_rate if sample else None,
            power=sample.power if sample else None,
            power_limit=sample.power_limit if sample else None,
            power_per_th=sample.power_per_th if sample else None,
            temp=sample.temp if sample else None,
            env_temp=sample.env_temp if sample else None,
        )


class AsicsSummaryDto(BaseModel):
    asics: list[AsicSummaryDto]


class AsicsListDto(BaseModel):
    asics: list[str]
