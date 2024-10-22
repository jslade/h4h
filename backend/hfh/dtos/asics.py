from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel

from ..models.asic import Asic, AsicStatus


class AsicSummaryDto(BaseModel):
    name: str
    status: str
    updated_at: datetime
    changed_at: datetime
    sampled_at: Optional[datetime]
    hash_rate: Optional[int]
    power: Optional[int]
    power_limit: Optional[int]
    power_per_th: Optional[int]
    temp: Optional[int]
    env_temp: Optional[int]

    @classmethod
    def from_asic(cls, asic: Asic) -> Self:
        sample = asic.samples[-1] if asic.samples else None

        return AsicSummaryDto(
            name=asic.name,
            status=AsicStatus.for_asic(asic),
            updated_at=asic.updated_at.astimezone(asic.timezone),
            changed_at=(asic.changed_at or asic.updated_at).astimezone(asic.timezone),
            sampled_at=sample.timestamp.astimezone(asic.timezone) if sample else None,
            hash_rate=sample.hash_rate if sample else None,
            power=sample.power if sample else None,
            power_limit=sample.power_limit if sample else None,
            power_per_th=sample.power_per_th if sample else None,
            temp=sample.temp if sample else None,
            env_temp=sample.env_temp if sample else None,
        )


class AsicsSummaryDto(BaseModel):
    asics: list[AsicSummaryDto]
