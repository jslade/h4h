


from typing import Optional, Self
from pydantic import BaseModel
from enum import Enum

from hfh.models.asic import Asic

class AsicStatus(str, Enum):
    offline = "offline"
    hashing = "hashing"
    paused = "paused"
    error = "error"

class AsicSummaryDto(BaseModel):
    name: str
    status: str

    @classmethod
    def from_asic(cls, asic: Asic) -> Self:
        return AsicSummaryDto(
            name=asic.name,
            status=AsicStatus.offline.value
        )

class AsicsSummaryDto(BaseModel):
    asics: list[AsicSummaryDto]
