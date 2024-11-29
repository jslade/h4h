from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from typing import Optional
import structlog
from pyasic import AnyMiner
from pyasic.data import MinerData
from pyasic.data.error_codes import MinerErrorData


from ..db import DB
from ..models.asic import Asic, AsicStatus
from ..models.hashing_interval import HashingInterval
from ..models.performance_limit import PerformanceLimit
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


async def set_hashing(asic: Asic, hashing: bool, duration: Optional[int] = None) -> None:
    LOGGER.info("set_hashing", asic=asic.name, hashing=hashing)
    miner: AnyMiner = await asic.get_miner()
    if hashing:
        await miner.resume_mining()
    else:
        await miner.stop_mining()

    if duration is not None:
        await set_override(asic, hashing=hashing, hours=duration)

    await update_status(asic)


async def set_override(
    asic: Asic,
    *,
    hashing: Optional[bool] = None,
    hours: Optional[int] = None,
    days: Optional[int] = None,
    power_limit: Optional[int] = None,
) -> None:
    LOGGER.info(
        "set_override",
        asic=asic.name,
        hashing=hashing,
        hours=hours,
        days=days,
        power_limit=power_limit,
    )

    from .schedule_service import ScheduleService

    service = ScheduleService()
    moment = datetime.now(tz=asic.timezone)
    current_interval = service.get_current_interval(asic, moment, ignore_override=True)

    if hashing is None:
        hashing = current_interval.is_hashing_at(moment) if current_interval else True

    # Start and end days
    date_start_mmdd = moment.strftime("%m/%d")

    if days is None or days < 1:
        days = 1
    date_end_mmdd = (moment + timedelta(days=days)).strftime("%m/%d")

    # Start an end times
    current_interval_end = (
        current_interval.next_end_time(moment) if current_interval else None
    )
    daytime_start_hhmm = moment.strftime("%H:%M")

    if hours is None or hours < 1:
        if days == 1:
            if current_interval:
                current_interval_end_hour = current_interval_end.hour
                hours = current_interval_end_hour - moment.hour
                if hours < 2:
                    hours = 2

    if hours:
        daytime_end = moment + timedelta(hours=hours)
    else:
        daytime_end = datetime.combine(moment.date(), time(0, 0), tzinfo=moment.tzinfo)
    daytime_end_hhmm = daytime_end.strftime("%H:%M")

    performance_limit: Optional[PerformanceLimit] = None
    if power_limit is not None:
        performance_limit = PerformanceLimit(power_limit=power_limit)

    override = HashingInterval(
        hashing_enabled=hashing,
        date_start_mmdd=date_start_mmdd,
        date_end_mmdd=date_end_mmdd,
        daytime_start_hhmm=daytime_start_hhmm,
        daytime_end_hhmm=daytime_end_hhmm,
        weekdays_active="*",
        price_per_kwh=Decimal(0),  # TBD,
        performance_limit=performance_limit,
    )

    DB.session.add(override)
    asic.override_interval = override
    DB.session.commit()


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
            if upfreq_complete is not None:
                asic.is_stable = upfreq_complete == 1
            else:
                hashing_stable = getitem(
                    summary_response, ("SUMMARY", [0], "Hash Stable")
                )
                if hashing_stable is not None:
                    asic.is_stable = hashing_stable

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
