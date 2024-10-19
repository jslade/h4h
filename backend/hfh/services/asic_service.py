from ..models.asic import Asic
from pyasic import AnyMiner
from pyasic.data import MinerData


import structlog

LOGGER = structlog.get_logger(__name__)


async def get_asic_data(asic: Asic) -> MinerData:
    m: AnyMiner = await asic.get_miner()
    d: MinerData = await m.get_data()
    return d


async def get_asic_data_extended(asic: Asic) -> MinerData:
    m: AnyMiner = await asic.get_miner()
    api = m.api

    d = {}

    for cmd in [
        "status",
        "summary",
        "get_psu",
        "get_miner_info",
        "devdetails",
        "devs",
        "get_error_code",
    ]:
        try:
            func = getattr(api, cmd)
            result = await func()
            d[cmd] = result
        except Exception as ex:
            d[cmd] = {"error": str(ex)}
            LOGGER.exception(
                "command failed",
                asic=asic.name,
                cmd=cmd,
                ex=ex,
            )

    return d
