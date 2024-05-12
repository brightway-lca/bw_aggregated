import sys

import pytest

from bw_aggregation import AggregatedDatabase, Speedup


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Windows `time` function has too low resolution",
)
def test_speedup_estimate(background):
    speedup = AggregatedDatabase.estimate_speedup("a")
    assert isinstance(speedup, Speedup)
    assert speedup.time_difference_relative < 1
