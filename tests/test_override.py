import bw2data
import pytest
from bw2data.tests import bw2test

from bw_aggregation.override import AggregationContext, aggregation_override


@bw2test
def test_context_manager_normal():
    assert aggregation_override.global_override is None
    assert aggregation_override.local_overrides == {}

    with AggregationContext(False):
        assert aggregation_override.global_override is False
        assert aggregation_override.local_overrides == {}

    assert aggregation_override.global_override is None
    assert aggregation_override.local_overrides == {}

    with AggregationContext(True):
        assert aggregation_override.global_override is True
        assert aggregation_override.local_overrides == {}

    assert aggregation_override.global_override is None
    assert aggregation_override.local_overrides == {}

    with AggregationContext(None):
        assert aggregation_override.global_override is None
        assert aggregation_override.local_overrides == {}

    assert aggregation_override.global_override is None
    assert aggregation_override.local_overrides == {}

    bw2data.Database("foo").write({})
    bw2data.Database("bar").write({})

    with AggregationContext({"foo": True, "bar": False}):
        assert aggregation_override.global_override is None
        assert aggregation_override.local_overrides == {"foo": True, "bar": False}

    assert aggregation_override.global_override is None
    assert aggregation_override.local_overrides == {}


def test_context_manager_wrong_input_type():
    with pytest.raises(ValueError):
        AggregationContext(4.2)


@bw2test
def test_override_input_type_checks():
    with pytest.raises(ValueError):
        aggregation_override.set_global_override("foo")

    with pytest.raises(ValueError):
        aggregation_override.set_local_overrides({"foo": True})

    bw2data.Database("foo").write({})

    with pytest.raises(ValueError):
        aggregation_override.set_local_overrides({"foo": "bar"})
