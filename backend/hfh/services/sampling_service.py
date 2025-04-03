from decimal import Decimal
from typing import Optional

import structlog

from ..db import DB
from ..models.asic import Asic
from ..models.performance_sample import PerformanceSample
from .asic_service import get_asic_data, update_status
from .schedule_service import ScheduleService

LOGGER = structlog.get_logger(__name__)


class SamplingService:
    def __init__(self, schedule_service: Optional[ScheduleService] = None) -> None:
        self.schedule_service = schedule_service or ScheduleService()

    async def sample_all_active(self, interval: int) -> None:
        LOGGER.info("sampling all active asics")
        for asic in Asic.all_active():
            try:
                await self.add_sample(asic, interval)
                DB.session.commit()
            except Exception as ex:
                LOGGER.exception(
                    "Failed to sample asic",
                    asic=asic.name,
                    exception=ex,
                )
                DB.session.rollback()

    async def add_sample(self, asic: Asic, interval: int) -> None:
        await update_status(asic)
        data = await get_asic_data(asic)

        moment = asic.local_time()
        temp = data.env_temp

        current_schedule_interval = self.schedule_service.get_current_interval(
            asic,
            moment=moment,
            temp=temp,
        )
        current_price_per_kwh = (
            current_schedule_interval.price_per_kwh if current_schedule_interval else None
        )

        sample = PerformanceSample(
            asic=asic,
            timestamp=moment,
            interval_secs=interval,
            is_online=asic.is_online,
            is_hashing=asic.is_hashing,
            is_stable=asic.is_stable,
            temp=data.temperature_avg,
            env_temp=data.env_temp,
            hash_rate=int(data.hashrate or 0),
            power=int(data.wattage or 0),
            power_limit=int(data.wattage_limit or 0),
            power_per_th=int(data.efficiency or 0),
            price_per_kwh=current_price_per_kwh or Decimal(0),
        )

        DB.session.add(sample)
