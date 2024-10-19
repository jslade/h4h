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
    from .performance_sample import PerformanceSample


class Asic(DB.Model, PKId, UniquelyNamed):
    __tablename__ = "asics"

    address: Mapped[str] = mapped_column(DB.String(40), nullable=False, index=True)
    password: Mapped[str] = mapped_column(DB.String(40), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        DB.Boolean, nullable=False, server_default="true", index=True
    )
    profile_id: Mapped[int] = mapped_column(
        DB.Integer, DB.ForeignKey("asic_profiles.id"), nullable=True
    )
    profile: Mapped[Optional["AsicProfile"]] = relationship("AsicProfile")

    samples: Mapped[list["PerformanceSample"]] = relationship(
        "PerformanceSample", back_populates="asic"
    )

    async def get_miner(self: Self) -> pyasic.AnyMiner:
        LOGGER.info(
            "get_miner",
            id=self.id,
            name=self.name,
            address=self.address,
            password=self.password,
        )
        try:
            if self._miner:
                return self._miner
        except AttributeError:
            setattr(self, "_miner", None)

        self._miner = await pyasic.get_miner(self.address)
        return self._miner

    @classmethod
    def all_active(cls, db_session: Optional[DbSession] = None) -> list[Self]:
        db_session = db_session or DB.session
        stmt = select(cls).order_by(cls.name)
        return db_session.scalars(stmt)
