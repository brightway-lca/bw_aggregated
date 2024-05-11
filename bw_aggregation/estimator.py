from dataclasses import dataclass

from bw2calc import LCA

from .calculation import AggregationCalculator


@dataclass
class Speedup:
    ratio: float
    time_with_aggregation: float
    time_without_aggregation: float


class CalculationDifferenceEstimator:
    def __init__(self, database_name: str):
        pass

    def difference(self) -> Speedup:
        without = self.calculate_without_speedup()
        with_ = self.calculate_with_speedup()
        return Speedup()
