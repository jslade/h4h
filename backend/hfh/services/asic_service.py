
from ..models.asic import Asic
from pyasic.data import MinerData

async def get_asic_data(asic: Asic) -> MinerData:
    m = await asic.get_miner()
    d: MinerData = await m.get_data()
    return d


