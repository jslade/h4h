from datetime import UTC, datetime
from typing import Optional

import structlog

from ..db import DB
from ..models.asic import Asic, AsicStatus
from ..models.hashing_interval import HashingInterval
from ..models.hashing_schedule import HashingSchedule
from .asic_service import get_asic_data, set_hashing, set_power_limit

LOGGER = structlog.get_logger(__name__)


class ScheduleService:
    async def update_all_active(self) -> None:
        for asic in Asic.all_active():
            await self.update(asic)
            DB.session.commit()

    async def update(self, asic: Asic) -> None:
        if not asic.is_online:
            LOGGER.info("Ignoring offline", asic=asic.name)

        LOGGER.info(
            "Updating asic operation", asic=asic.name, status=AsicStatus.for_asic(asic)
        )

        moment = datetime.now(tz=UTC)
        current_interval = self.get_current_interval(asic, moment)

        if self.should_be_hashing(asic, current_interval, moment):
            LOGGER.info("Asic should be hashing", asic=asic.name)
            await self.ensure_is_hashing(asic)
            await self.ensure_power_limit(asic, current_interval)
        else:
            LOGGER.info("Asic should not be hashing", asic=asic.name)
            await self.ensure_not_hashing(asic)

    def get_current_interval(
        self, asic: Asic, moment: datetime
    ) -> Optional[HashingInterval]:
        schedule: Optional[HashingSchedule] = (
            asic.profile.schedule if asic.profile and asic.profile.schedule else None
        )
        if not schedule:
            return None

        interval: HashingInterval
        for interval in schedule.intervals:
            if interval.is_active_at(moment):
                return interval

        return None

    def should_be_hashing(
        self, asic: Asic, current_interval: Optional[HashingInterval], moment: datetime
    ) -> bool:
        if current_interval:
            return current_interval.is_hashing_at(moment)
        else:
            return asic.is_hashing

    async def ensure_is_hashing(self, asic: Asic) -> None:
        if not asic.is_hashing:
            await set_hashing(asic, True)

    async def ensure_power_limit(
        self, asic: Asic, interval: Optional[HashingInterval]
    ) -> None:
        if not (interval and interval.performance_limit):
            return

        expected_power_limit = interval.performance_limit.power_limit
        try:
            last_sample = asic.samples[-1]
            current_power_limit = last_sample.power_limit
        except Exception:
            data = await get_asic_data(asic)
            current_power_limit = data.wattage_limit

        if current_power_limit != expected_power_limit:
            await set_power_limit(asic, expected_power_limit)

    async def ensure_not_hashing(self, asic: Asic) -> None:
        if asic.is_hashing:
            await set_hashing(asic, False)
