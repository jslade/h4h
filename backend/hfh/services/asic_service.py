from datetime import UTC, datetime
import structlog
from pyasic import AnyMiner
from pyasic.data import MinerData
from pyasic.data.error_codes import MinerErrorData

from ..db import DB
from ..models.asic import Asic, AsicStatus
from ..utils.data import getitem

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

    await update_status(asic)


async def set_power_limit(asic: Asic, power_limit: int) -> None:
    LOGGER.info("set_power_limit", asic=asic.name, power_limit=power_limit)
    miner: AnyMiner = await asic.get_miner()
    await miner.api.adjust_power_limit(power_limit)

    await update_status(asic)


async def update_status(asic: Asic) -> AsicStatus:
    prev_status = AsicStatus.for_asic(asic)
    LOGGER.debug("updating status", asic=asic.name, status=prev_status)

    asic.is_online = False
    asic.is_hashing = False
    asic.is_stable = False

    try:
        d = await get_asic_data(asic)
        asic.is_online = True
        asic.is_hashing = d.is_mining
        if asic.is_hashing:
            miner: AnyMiner = await asic.get_miner()
            summary_response = await miner.api.summary()
            upfreq_complete = getitem(
                summary_response, ("SUMMARY", [0], "Upfreq Complete")
            )
            asic.is_stable = upfreq_complete == 1

    except Exception as ex:
        LOGGER.info("asic appears to be offline", asic=asic.name, ex=ex)

    asic.updated_at = datetime.now(tz=asic.timezone)

    status = AsicStatus.for_asic(asic)

    if status != prev_status:
        LOGGER.info(
            "updated status", asic=asic.name, status=status, prev_status=prev_status
        )
        asic.changed_at = asic.updated_at

    return status


async def update_status_of_all_active() -> None:
    all_active = Asic.all_active()
    LOGGER.info("Updating status of all active", count=len(all_active))
    for asic in all_active:
        await update_status(asic)
    DB.session.commit()
