from typing import Self

from pydantic import BaseModel

from ..models.asic import Asic, AsicStatus


class AsicSummaryDto(BaseModel):
    name: str
    status: str

    @classmethod
    def from_asic(cls, asic: Asic) -> Self:
        return AsicSummaryDto(name=asic.name, status=AsicStatus.for_asic(asic))


class AsicsSummaryDto(BaseModel):
    asics: list[AsicSummaryDto]
