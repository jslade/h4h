
from ..models.asic import Asic

async def get_asic_data(asic: Asic) -> dict:
    m = await asic.get_miner()
    d = await m.get_data()
    return d.as_dict()


