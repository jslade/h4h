import pyasic
import structlog

from typing import Optional, Self
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from ..db import DB, DbSession

LOGGER = structlog.get_logger(__name__)

class Asic(DB.Model):
    id: Mapped[int] = mapped_column(DB.Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(DB.String(40), nullable=False, index=True)
    address: Mapped[str] = mapped_column(DB.String(40), nullable=False, index=True)
    password: Mapped[str] = mapped_column(DB.String(40), nullable=False)

    async def get_miner(self: Self) -> pyasic.AnyMiner:
        LOGGER.info(
            f"get_miner",
            id=self.id,
            name=self.name,
            address=self.address,
            password=self.password
        )
        try:
            if self._miner:
                return self._miner
        except AttributeError:
            setattr(self, '_miner', None)
        
        self._miner = await pyasic.get_miner(self.address)
        return self._miner
    
    @classmethod
    def with_name(cls, name: str, db_session: Optional[DbSession] = None) -> Optional["Asic"]:
        db_session = db_session or DB.session
        stmt = select(cls).where(cls.name == name)
        return db_session.scalar(stmt)
    
    @classmethod
    def all_active(cls, db_session: Optional[DbSession] = None) -> list[Self]:
        db_session = db_session or DB.session
        stmt = select(cls).order_by(cls.name)
        return db_session.scalars(stmt)
