from datetime import datetime, timedelta
from typing import Optional

import structlog

from ..db import DB
from ..models.asic import Asic, AsicStatus
from ..models.hashing_interval import HashingInterval
from ..models.hashing_schedule import HashingSchedule
from ..models.scenario import Scenario
from .asic_service import get_asic_data, set_hashing, set_power_limit

LOGGER = structlog.get_logger(__name__)


class ScheduleService:
    async def update_all_active(self) -> None:
        LOGGER.info("updating all active asics according to schedule")
        for asic in Asic.all_active():
            try:
                await self.update(asic)
                DB.session.commit()
            except Exception as ex:
                LOGGER.exception(
                    "Failed to update asic",
                    asic=asic.name,
                    exception=ex,
                )
                DB.session.rollback()

    async def update(self, asic: Asic) -> None:
        if not asic.is_online:
            LOGGER.debug("Ignoring offline", asic=asic.name)
            return

        moment = asic.local_time()
        sample = asic.latest_sample
        temp = sample.env_temp if sample else None

        LOGGER.debug(
            "Updating asic operation by schedule constraints",
            asic=asic.name,
            status=AsicStatus.for_asic(asic),
            moment=moment,
            temp=temp,
        )

        current_interval = self.get_current_interval(
            asic,
            moment=moment,
            temp=temp,
        )
        if current_interval:
            LOGGER.debug(
                "current_interval",
                asic=asic.name,
                moment=moment,
                profile=asic.profile.name or asic.profile.id if asic.profile else None,
                schedule=current_interval.schedule.name or current_interval.schedule.id
                if current_interval.schedule
                else "(override)",
                interval=current_interval.name or current_interval.id,
                hashing=current_interval.hashing_enabled,
                time_start=current_interval.daytime_start,
                time_end=current_interval.daytime_end,
                power_limit=current_interval.performance_limit.power_limit
                if current_interval.performance_limit
                else None,
                until=current_interval.next_end_time(moment),
            )
        else:
            LOGGER.debug(
                "no current_interval",
                asic=asic.name,
                profile=asic.profile.name or asic.profile.id if asic.profile else None,
                schedule=asic.profile.schedule.name or asic.profile.schedule.id
                if asic.profile and asic.profile.schedule
                else None,
            )

        if self.should_be_hashing(asic, current_interval, moment):
            LOGGER.debug("should be hashing", asic=asic.name)
            await self.ensure_is_hashing(asic, moment=moment)
        else:
            LOGGER.debug("should not be hashing", asic=asic.name)
            await self.ensure_not_hashing(asic)
        await self.ensure_power_limit(asic, current_interval)

    def can_change_hashing(self, asic: Asic, moment: datetime) -> bool:
        """
        Determine if we can change the hashing state of the ASIC based on its current status.
        """
        status = AsicStatus.for_asic(asic)
        if status in (AsicStatus.error, AsicStatus.offline):
            return True

        changed_at = asic.local_time(
            asic.changed_at if asic.changed_at else datetime(2020, 1, 1)
        )
        since_changed = moment - changed_at
        if since_changed < timedelta(minutes=30):
            LOGGER.debug(
                "Too soon since last change to hashing state",
                asic=asic.name,
                since_changed=since_changed,
            )
            return False

        return True

    def get_current_interval(
        self,
        asic: Asic,
        moment: datetime,
        temp: Optional[int] = None,
        ignore_override: Optional[bool] = False,
    ) -> Optional[HashingInterval]:
        scenario = Scenario(
            moment=moment,
            temp=temp,
        )

        if not ignore_override:
            if override := asic.override_interval:
                if override.is_active_under(scenario):
                    LOGGER.info(
                        "Using override interval for now",
                        asic=asic.name,
                        until=override.next_end_time(moment),
                    )
                    return override

        schedule: Optional[HashingSchedule] = (
            asic.profile.schedule if asic.profile and asic.profile.schedule else None
        )
        if not schedule:
            return None

        interval: HashingInterval
        for interval in schedule.intervals:
            if interval.is_active_under(scenario):
                return interval

        return None

    def should_be_hashing(
        self, asic: Asic, current_interval: Optional[HashingInterval], moment: datetime
    ) -> bool:
        if current_interval:
            return current_interval.is_hashing_at(moment)
        else:
            return asic.is_hashing

    async def ensure_is_hashing(self, asic: Asic, moment: datetime) -> None:
        if not asic.is_hashing:
            LOGGER.info("Asic should be hashing but isn't", asic=asic.name)

            if not self.can_change_hashing(asic, moment=moment):
                LOGGER.info("Ignoring unstable or transitioning asic", asic=asic.name)
                return

            await set_hashing(asic, True)

    async def ensure_power_limit(
        self, asic: Asic, interval: Optional[HashingInterval]
    ) -> None:
        if not (interval and interval.performance_limit):
            LOGGER.debug(
                "Asic has no perf limit for current interval",
                asic=asic.name,
                interval=interval if interval else None,
            )
            return

        expected_power_limit = interval.performance_limit.power_limit
        try:
            last_sample = asic.latest_sample
            current_power_limit = last_sample.power_limit if last_sample else None
        except Exception:
            data = await get_asic_data(asic)
            current_power_limit = data.wattage_limit

        LOGGER.info(
            "Asic expected power_limit",
            asic=asic.name,
            current=current_power_limit,
            expected=expected_power_limit,
            interval=interval,
        )

        if current_power_limit != expected_power_limit:
            LOGGER.info(
                "Asic power_limit is not as expected",
                asic=asic.name,
                current=current_power_limit,
                expected=expected_power_limit,
            )
            await set_power_limit(asic, expected_power_limit)

    async def ensure_not_hashing(self, asic: Asic) -> None:
        if asic.is_hashing:
            LOGGER.info("Asic should not be hashing but is", asic=asic.name)
            await set_hashing(asic, False)
