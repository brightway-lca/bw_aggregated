"""bw_aggregation."""

__all__ = (
    "__version__",
    "AggregatedDatabase",
    "AggregationContext",
    "ObsoleteAggregatedDatapackage",
)

__version__ = "0.0.1"


from bw2data.backends import Activity
from bw2data.subclass_mapping import (
    DATABASE_BACKEND_MAPPING,
    NODE_PROCESS_CLASS_MAPPING,
)

from .main import AggregatedDatabase, ObsoleteAggregatedDatapackage
from .override import AggregationContext

DATABASE_BACKEND_MAPPING["aggregated"] = AggregatedDatabase
NODE_PROCESS_CLASS_MAPPING["aggregated"] = Activity
