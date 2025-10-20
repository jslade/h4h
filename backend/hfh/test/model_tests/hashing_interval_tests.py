from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

import pytest

from hfh.models.hashing_interval import HashingInterval
from hfh.models.hashing_schedule import HashingSchedule
from hfh.models.performance_limit import PerformanceLimit

MTN = ZoneInfo("US/Mountain")


class TestHashIntervalActiveWindow:
    @pytest.fixture
    def schedule(self) -> HashingSchedule:
        return HashingSchedule(name="fixture", timezone_name="America/Denver")

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
            is_active=True,
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
            is_active=True,
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
            is_active=True,
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
            is_active=True,
        )

    @pytest.fixture
    def allday_everyday(self, schedule: HashingSchedule) -> HashingInterval:
        return HashingInterval(
            schedule=schedule,
            daytime_start_hhmm="00:00",
            daytime_end_hhmm="00:00",
            date_start_mmdd="01/01",
            date_end_mmdd="01/01",
            hashing_enabled=True,
            weekdays_active="*",
            is_active=True,
        )

    @pytest.fixture
    def override(self, schedule: HashingSchedule) -> HashingInterval:
        return HashingInterval(
            schedule=schedule,
            daytime_start_hhmm="21:00",
            daytime_end_hhmm="12:34",
            date_start_mmdd="05/14",
            date_end_mmdd="05/15",
            hashing_enabled=True,
            weekdays_active="*",
            is_active=True,
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

    @pytest.mark.parametrize(
        (
            "moment",
            "expected",
        ),
        [
            (datetime(2025, 5, 14, 9, 0, tzinfo=MTN), False),
            (datetime(2025, 5, 14, 23, 0, tzinfo=MTN), True),
            (datetime(2025, 5, 15, 0, 0, tzinfo=MTN), True),
            (datetime(2025, 5, 15, 12, 35, tzinfo=MTN), False),
            (datetime(2025, 5, 15, 23, 0, tzinfo=MTN), False),
        ],
    )
    def test_is_active_at_override(
        self,
        override: HashingInterval,
        moment: datetime,
        expected: bool,
    ) -> None:
        assert override.is_active_at(moment) == expected

    def test_is_all_day(
        self,
        morning: HashingInterval,
        afternoon: HashingInterval,
        evening: HashingInterval,
        weekend: HashingInterval,
    ) -> None:
        assert morning.is_all_day is False
        assert afternoon.is_all_day is False
        assert evening.is_all_day is False
        assert weekend.is_all_day is True

    def test_is_active(self, allday_everyday: HashingInterval) -> None:
        assert allday_everyday.is_active is True
        now = datetime.now(tz=MTN)
        assert allday_everyday.is_active_at(now) is True
        allday_everyday.is_active = False
        assert allday_everyday.is_active_at(now) is False

    @pytest.mark.parametrize(
        "temp, temp_min, temp_max, expected",
        [
            (
                50,
                None,
                None,
                True,
            ),
            (
                50,
                40,
                None,
                True,
            ),
            (
                50,
                None,
                60,
                True,
            ),
            (
                50,
                60,
                None,
                False,
            ),
            (
                50,
                40,
                60,
                True,
            ),
            (
                50,
                55,
                60,
                False,
            ),
        ],
    )
    def test_is_active_temp(
        self,
        allday_everyday: HashingInterval,
        temp: int,
        temp_min: Optional[int],
        temp_max: Optional[int],
        expected: bool,
    ) -> None:
        allday_everyday.temp_min = temp_min
        allday_everyday.temp_max = temp_max

        assert allday_everyday.is_active_at_temp(temp) is expected
