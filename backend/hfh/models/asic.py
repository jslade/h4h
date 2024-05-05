import pyasic

from typing import Optional, Self
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from ..db import DB, DbSession

class Asic(DB.Model):
    id: Mapped[int] = mapped_column(DB.Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(DB.String(40), nullable=False, index=True)
    address: Mapped[str] = mapped_column(DB.String(40), nullable=False, index=True)
    password: Mapped[str] = mapped_column(DB.String(40), nullable=False)

    @classmethod
    def with_name(cls, name: str, db_session: Optional[DbSession] = None) -> Optional["Asic"]:
        db_session = db_session or DB.session
        stmt = select(cls).where(cls.name == name)
        return db_session.scalar(stmt)
    

    async def get_miner(self: Self) -> pyasic.AnyMiner:
        try:
            if self._miner:
                return self._miner
        except AttributeError:
            setattr(self, '_miner', None)
        
        self._miner = await pyasic.get_miner(self.address)
        self._miner.pwd = self.password

        return self._miner
    