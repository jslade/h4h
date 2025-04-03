from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Scenario:
    """
    A class to represent a scenario for possible hashing
    """

    moment: datetime
    temp: Optional[int] = None  # deg C

    @property
    def temp_f(self) -> Optional[int]:
        if self.temp is None:
            return None
        return int((self.temp * 9 / 5) + 32)
