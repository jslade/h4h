import structlog
from pyasic import AnyMiner
from pyasic.data import MinerData
from pyasic.data.error_codes import MinerErrorData

from ..models.asic import Asic

LOGGER = structlog.get_logger(__name__)


async def get_asic_data(asic: Asic) -> MinerData:
    m: AnyMiner = await asic.get_miner()
    d: MinerData = await m.get_data()
    return d


async def get_asic_errors(asic: Asic) -> MinerErrorData:
    m: AnyMiner = await asic.get_miner()
    d: MinerErrorData = await m.get_errors()
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


async def set_hashing(asic: Asic, hashing: bool) -> None:
    LOGGER.info("set_hashing", asic=asic.name, hashing=hashing)
    miner: AnyMiner = await asic.get_miner()
    if hashing:
        await miner.resume_mining()
    else:
        await miner.stop_mining()


async def set_power_limit(asic: Asic, power_limit: int) -> None:
    LOGGER.info("set_power_limit", asic=asic.name, power_limit=power_limit)
    miner: AnyMiner = await asic.get_miner()
    await miner.api.adjust_power_limit(power_limit)
