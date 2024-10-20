from datetime import datetime
from typing import Self

from pydantic import BaseModel

from ..models.asic import Asic, AsicStatus


class AsicSummaryDto(BaseModel):
    name: str
    status: str
    updated_at: datetime
    changed_at: datetime

    @classmethod
    def from_asic(cls, asic: Asic) -> Self:
        return AsicSummaryDto(
            name=asic.name,
            status=AsicStatus.for_asic(asic),
            updated_at=asic.updated_at.astimezone(asic.timezone),
            changed_at=(asic.changed_at or asic.updated_at).astimezone(asic.timezone),
        )


class AsicsSummaryDto(BaseModel):
    asics: list[AsicSummaryDto]
