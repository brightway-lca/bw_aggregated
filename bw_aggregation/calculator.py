from time import time

import numpy as np
from bw2calc import LCA, spsolve
from bw2data import databases, prepare_lca_inputs
from bw2data.database import DatabaseChooser
from bw_graph_tools import guess_production_exchanges
from matrix_utils import ArrayMapper
from scipy.sparse import csr_matrix

from .override import AggregationContext


class AggregationCalculator:
    def __init__(self, database_name: str):
        if database_name not in databases:
            raise ValueError(f"Unknown database {database_name}")
        self.db = DatabaseChooser(database_name)

        # Eating our own dogfood to calculate new cache values
        with AggregationContext({database_name: False}):
            indexed_demand, data_objs, _ = prepare_lca_inputs(
                {self.db.random(): 1}, remapping=False
            )

        self.lca = LCA(demand=indexed_demand, data_objs=data_objs)

    def calculate(self) -> None:
        self.lca.load_lci_data()

        # Only need to solve for the products from the processes in *this* database
        # Correspondence between processes and their reference products is not fixed.
        # We use `guess_production_exchanges` instead of assuming values on a diagonal
        prod_rows, prod_cols = guess_production_exchanges(self.lca.technosphere_mm)
        # Not very efficient; could be SQL query but that would break IOTable
        matrix_db_process_ids = np.array(
            [
                self.lca.dicts.activity[obj.id]
                for obj in self.db
                if obj.get("type", "process") == "process"
            ]
        )

        # Get boolean mask for the column indices of the processes in the database
        # we are looking at
        mask = np.isin(prod_cols, matrix_db_process_ids)

        # Construct demand array with dimensions (all processes, filtered processes)
        demand_array = np.zeros((self.lca.technosphere_matrix.shape[1], mask.sum()))

        # This breaks our normal mapping, which was from processes to *all* columns
        # So we need a separate mapping for the filtered columns
        am = ArrayMapper(array=prod_cols[mask])
        column_mapping = am.reverse_dict()
        self.reverse_filtered_column_mapping = {
            int(filtered_column_idx): self.lca.dicts.activity.reversed[
                column_mapping[filtered_column_idx]
            ]
            for filtered_column_idx in am.index_array[prod_cols[mask]]
        }
        # Only calculate for the products coming from the processes in our database
        demand_array[prod_rows[mask], am.index_array[prod_cols[mask]].astype(int)] = 1

        if calc_time := self.db.metadata.get("aggregation_calculation_time"):
            print(
                f"Starting inventory calculation. Took {calc_time:.1f} seconds last time."
            )
        else:
            print(
                "Starting inventory calculation. Please be patient, we have"
                + f" {len(self.db)} processes to calculate."
            )
        # Supply_array will be square, and transverse of technosphere matrix
        # i.e. dimensions are (processes, products)
        start = time()
        self.supply_array = spsolve(self.lca.technosphere_matrix, demand_array)
        self.db.metadata["aggregation_calculation_time"] = time() - start
        self.db._metadata.flush()

        # We don't diagonalize, but have wide supply array
        # Inventory dimension is (ecosphere flows, filtered processes)
        self.inventory = (
            self.lca.biosphere_matrix @ csr_matrix(self.supply_array)
        ).tocoo()

        # Construct mapping back to database IDs
        self.products = [
            self.lca.dicts.product.reversed[idx] for idx in prod_rows[mask]
        ]
        self.processes = [self.lca.dicts.activity.reversed[idx] for idx in am.array]

    @property
    def technosphere_iterator(self) -> dict:
        if not hasattr(self, "inventory"):
            raise ValueError("Must do calculation first")

        return (
            {"row": product, "col": process, "amount": 1}
            for product, process in zip(self.products, self.processes)
        )

    @property
    def biosphere_iterator(self) -> dict:
        if not hasattr(self, "inventory"):
            raise ValueError("Must do calculation first")

        return (
            {
                "row": self.lca.dicts.biosphere.reversed[row],
                "col": self.reverse_filtered_column_mapping[col],
                "amount": amount,
            }
            for row, col, amount in zip(
                self.inventory.row, self.inventory.col, self.inventory.data
            )
            if amount
        )
