import sys

from bw_aggregation import AggregatedDatabase, Speedup


def test_speedup_estimate(background):
    speedup = AggregatedDatabase.estimate_speedup("a")
    assert isinstance(speedup, Speedup)
    if not sys.platform.startswith("win"):
        assert speedup.time_difference_relative < 1
