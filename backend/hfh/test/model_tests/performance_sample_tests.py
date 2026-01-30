import re
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

import hfh.models.all
from hfh.models.performance_sample import PerformanceSample


class TestPerformanceSample:
    def _make_sample(
        self,
        ts: datetime,
        hash_rate: int = 0,
        power: int = 0,
        is_stable: bool = True,
        is_hashing: bool = True,
    ) -> PerformanceSample:
        return PerformanceSample(
            timestamp=ts,
            hash_rate=hash_rate,
            power=power,
            is_stable=is_stable,
            is_hashing=is_hashing,
        )

    def test_coalesce_returns_aggregated_sample(self):
        now = datetime.utcnow()
        s1 = self._make_sample(now - timedelta(seconds=2), hash_rate=10)
        s2 = self._make_sample(now - timedelta(seconds=1), hash_rate=20)
        s3 = self._make_sample(now, hash_rate=40)
        samples = [s1, s2, s3]

        result = PerformanceSample.coalesce(samples)
        assert result is not None
        assert len(result) == 1
        sc = result[0]
        assert isinstance(sc, PerformanceSample)

        assert sc.timestamp == s1.timestamp
        assert sc.hash_rate == Decimal(70) / Decimal(3)  # average of 10,20,40

    def test_graph_returns_series_matching_samples(self):
        now = datetime.utcnow()
        samples = [
            self._make_sample(now - timedelta(minutes=2), hash_rate=10, power=30, ),
            self._make_sample(now - timedelta(minutes=1), hash_rate=20, power=40, is_stable=False),
            self._make_sample(now, hash_rate=30, power=50),
        ]

        graph = PerformanceSample.graph(samples, attr="hash_rate")
        PerformanceSample.print(samples, attr="hash_rate")
        assert len(graph) == len(samples)
        assert re.match(r"^.+:\*{10} 10", graph[0])
        assert re.match(r"^.+:\*{20} 20", graph[1])
        assert re.match(r"^.+:\*{30} 30", graph[2])

        graph = PerformanceSample.graph(samples, attr="power")
        PerformanceSample.print(samples, attr="power")
        assert len(graph) == len(samples)
        assert re.match(r"^.+:\*{30} 30", graph[0])
        assert re.match(r"^.+:\*{40} 40", graph[1])
        assert re.match(r"^.+:\*{50} 50", graph[2])

        graph = PerformanceSample.graph(samples, attr="power")
        PerformanceSample.print(samples, attr="power")
        assert len(graph) == len(samples)
        assert re.match(r"^.+:\*{30} 30", graph[0])
        assert re.match(r"^.+:\*{40} 40", graph[1])
        assert re.match(r"^.+:\*{50} 50", graph[2])

        graph = PerformanceSample.graph(samples, attr="is_stable")
        PerformanceSample.print(samples, attr="is_stable")
        assert len(graph) == len(samples)
        assert re.match(r"^.+: True", graph[0])
        assert re.match(r"^.+: False", graph[1])
        assert re.match(r"^.+: True", graph[2])
        