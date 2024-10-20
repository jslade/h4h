from datetime import UTC, datetime
from decimal import Decimal

import structlog

from ..db import DB
from ..models.asic import Asic
from ..models.performance_sample import PerformanceSample
from .asic_service import get_asic_data, update_status

LOGGER = structlog.get_logger(__name__)


class SamplingService:
    async def sample_all_active(self, interval: int) -> None:
        for asic in Asic.all_active():
            await self.add_sample(asic, interval)

        DB.session.commit()

    async def add_sample(self, asic: Asic, interval: int) -> None:
        await update_status(asic)
        data = await get_asic_data(asic)

        sample = PerformanceSample(
            asic=asic,
            timestamp=datetime.now(tz=UTC),
            interval_secs=interval,
            is_online=asic.is_online,
            is_hashing=asic.is_hashing,
            is_stable=asic.is_stable,
            temp=data.temperature_avg,
            env_temp=data.env_temp,
            hash_rate=int(data.hashrate),
            power=int(data.wattage),
            power_limit=int(data.wattage_limit),
            power_per_th=data.efficiency,
            price_per_kwh=Decimal(0),  # TBD
        )

        DB.session.add(sample)
