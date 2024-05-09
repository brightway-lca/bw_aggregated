"""bw_aggregation."""

__all__ = (
    "__version__",
    "AggregatedDatabase",
    "AggregationContext",
    # Add functions and variables you want exposed in `bw_aggregation.` namespace here
)

__version__ = "0.0.1"


from bw2data.database import DATABASE_BACKEND_MAPPING

from .main import AggregatedDatabase
from .override import AggregationContext

DATABASE_BACKEND_MAPPING["aggregated"] = AggregatedDatabase
