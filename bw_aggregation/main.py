import warnings

import tqdm
from bw2calc import LCA, PYPARDISO
from bw2data.backends import SQLiteBackend
from bw_processing import (
    Datapackage,
    clean_datapackage_name,
    create_datapackage,
    load_datapackage,
    safe_filename,
)


class AggregatedDatabase(SQLiteBackend):
    """A class which maintains two processed datapackages, and can use the aggregated datapackage
    for quicker calculations.

    An aggregated database only stores the *cumulative biosphere flows* of each unit process
    instead of its actual supply chain. Because it stores less information, it can't do graph
    traversal, Monte Carlo, or show any information on the processes in the supply chain causing
    impacts.

    Calculating aggregated emissions for every process in a database can be expensive. Therefore,
    this library in only useful for large background databases which do not change frequently.

    You can get an estimate of the speed increase possible for a given database with
    `AggregatedDatabase.estimate_speedup('<database name>')`.

    To create a new aggregated database, use `bw2data.DatabaseChooser('<name>', backend='aggregated')`.
    To convert an existing database, use `AggregatedDatabase.convert_existing()`.

    You can still do normal calculations with an aggregated database. To set the default
    calculation method to use the aggregated values, call `db.use_aggregated()` (where `db` is an
    instance of `AggregatedDatabase`). To set the default to use unit processes, call
    `db.use_aggregated(False)`.

    Stores configuration and log data in the `Database` metadata dictionary in the following keys:

    * `aggregation_calculation_time`: float. Time to last calculate aggregation in seconds.
    * `aggregation_calculation_timestamp`: TBD
    * `aggregation_use_in_calculation`: bool. Use the aggregated datapackage in calculations.

    """

    @staticmethod
    def estimate_speedup(database_name: str) -> float:
        """Estimate how much quicker calculations could be when using aggregated emissions.

        Prints to `stdout` and return a float, the ratio of calculation speed with aggregation
        to speed without aggregation."""
        pass

    @staticmethod
    def convert_existing(database_name: str) -> None:
        """Convert a unit process database to an aggregated database."""
        pass

    def use_aggregated(default: bool = True) -> None:
        """Set default calculation to use (or not use) the aggregated emissions."""
        if default not in {True, False}:
            raise ValueError(f"`default` must be a boolean; got '{default}'")
        self.metadata["aggregation_use_in_calculation"] = default

    def filepath_aggregated(self):
        if self.metadata.get("dirty"):
            self.process_aggregated()
        return self.dirpath_processed() / self.filename_aggregated()

    def filename_aggregated(self):
        return clean_datapackage_name(self.filename + "aggregated.zip")

    def calculate_aggregated_emissions(self):
        pass
