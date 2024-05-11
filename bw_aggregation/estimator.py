from dataclasses import dataclass
from time import time

from bw2calc import LCA
from bw2data import prepare_lca_inputs, Database

from .calculator import AggregationCalculator
from .override import AggregationContext


@dataclass
class Speedup:
    database_name: str
    time_with_aggregation: float
    time_without_aggregation: float
    time_difference_absolute: float
    time_difference_relative: float


class CalculationDifferenceEstimator:
    def __init__(self, database_name: str):
        self.name = database_name
        self.db = Database(database_name)

    def difference(self) -> Speedup:
        without = self.calculate_without_speedup()
        with_ = self.calculate_with_speedup()
        return Speedup(
            database_name=self.name,
            time_difference_relative=with_ / without,
            time_difference_absolute=with_ - without,
            time_with_aggregation=with_,
            time_without_aggregation=without,
        )

    def calculate_with_speedup(self):
        from .main import AggregatedDatabase

        process = self.db.random()

        with AggregationContext({self.name: False}):
            fu, data_objs, _ = prepare_lca_inputs({process: 1})
            data_objs[-1] = AggregatedDatabase(self.name).process_aggregated(
                in_memory=True
            )

            start = time()
            lca = LCA(fu, data_objs=data_objs)
            lca.lci()
            end = time()

        return end - start

    def calculate_without_speedup(self):
        process = self.db.random()

        with AggregationContext({self.name: False}):
            fu, data_objs, _ = prepare_lca_inputs({process: 1})

            start = time()
            lca = LCA(fu, data_objs=data_objs)
            lca.lci()
            end = time()

        return end - start
