from datetime import datetime

import pytest
import pytz

from hfh.models.performance_limit import PerformanceLimit
from hfh.models.hashing_interval import HashingInterval
from hfh.models.hashing_schedule import HashingSchedule


MTN = pytz.timezone("US/Mountain")


class TestHashIntervalActiveWindow:
    @pytest.fixture
    def schedule(self) -> HashingSchedule:
        return HashingSchedule(name="fixture", timezone_name="US/Mountain")

    @pytest.fixture
    def morning(self, schedule: HashingSchedule) -> HashingInterval:
        return HashingInterval(
            schedule=schedule,
            daytime_start_hhmm="00:00",
            daytime_end_hhmm="14:00",
            date_start_mmdd="10/01",
            date_end_mmdd="06/01",
            hashing_enabled=True,
            performance_limit=PerformanceLimit(power_limit=2000),
            weekdays_active="MoTuWeTh",
        )

    @pytest.fixture
    def afternoon(self, schedule: HashingSchedule) -> HashingInterval:
        return HashingInterval(
            schedule=schedule,
            daytime_start_hhmm="14:00",
            daytime_end_hhmm="19:00",
            date_start_mmdd="10/01",
            date_end_mmdd="06/01",
            hashing_enabled=False,
            performance_limit=PerformanceLimit(power_limit=2000),
            weekdays_active="MonTuWeTh",
        )

    @pytest.fixture
    def evening(self, schedule: HashingSchedule) -> HashingInterval:
        return HashingInterval(
            schedule=schedule,
            daytime_start_hhmm="19:00",
            daytime_end_hhmm="00:00",
            date_start_mmdd="10/01",
            date_end_mmdd="06/01",
            hashing_enabled=False,
            performance_limit=PerformanceLimit(power_limit=2000),
            weekdays_active="*",
        )

    @pytest.fixture
    def weekend(self, schedule: HashingSchedule) -> HashingInterval:
        return HashingInterval(
            schedule=schedule,
            daytime_start_hhmm="00:00",
            daytime_end_hhmm="00:00",
            date_start_mmdd="10/01",
            date_end_mmdd="06/01",
            hashing_enabled=False,
            performance_limit=PerformanceLimit(power_limit=2000),
            weekdays_active="SaSu",
        )

    @pytest.mark.parametrize(
        (
            "moment",
            "morning_expected",
            "afternoon_expected",
            "evening_expected",
            "weekend_expected",
        ),
        [
            (datetime(2024, 10, 21, 9, 0, tzinfo=MTN), True, False, False, False),
            (datetime(2024, 10, 21, 14, 0, tzinfo=MTN), False, True, False, False),
            (datetime(2024, 10, 21, 19, 0, tzinfo=MTN), False, False, True, False),
            (datetime(2024, 10, 20, 9, 0, tzinfo=MTN), False, False, False, True),
            (datetime(2024, 10, 20, 14, 0, tzinfo=MTN), False, False, False, True),
            (datetime(2024, 10, 20, 19, 0, tzinfo=MTN), False, False, True, True),
            (datetime(2024, 10, 19, 19, 0, tzinfo=MTN), False, False, True, True),
            (datetime(2024, 9, 1, 9, 0, tzinfo=MTN), False, False, False, False),
            (datetime(2024, 9, 2, 9, 0, tzinfo=MTN), False, False, False, False),
            (datetime(2024, 12, 31, 15, 22, tzinfo=MTN), False, True, False, False),
            (datetime(2025, 5, 30, 23, 59, 59, tzinfo=MTN), False, False, True, False),
            (datetime(2025, 6, 1, 23, 59, 59, tzinfo=MTN), False, False, True, True),
            (datetime(2025, 6, 2, 0, 0, 0, tzinfo=MTN), False, False, False, False),
        ],
    )
    def test_is_active_at(
        self,
        morning: HashingInterval,
        afternoon: HashingInterval,
        evening: HashingInterval,
        weekend: HashingInterval,
        moment: datetime,
        morning_expected: bool,
        afternoon_expected: bool,
        evening_expected: bool,
        weekend_expected: bool,
    ) -> None:
        assert morning.is_active_at(moment) == morning_expected
        assert afternoon.is_active_at(moment) == afternoon_expected
        assert evening.is_active_at(moment) == evening_expected
        assert weekend.is_active_at(moment) == weekend_expected
