# Usage

This library allows you to trade space for time by pre-computing some inventory results. Each Brightway `Database` can be aggregated - i.e. we can calculate the *cumulative biosphere flows* needed for each process in that flow. We then store these values separately, to be used instead of the normal technosphere supply chain entries. This is faster as we don't need to solve the linear proble `Ax=b` for that database subgraph.

As the supply chain data is removed, we can't do calculations which would use that supply chain data. That means we can't do:

* Uncertainty analysis (no values in the technosphere array to sample from)
* Graph traversal (the graph is cutoff for each process)
* Regionalized LCIA (every biosphere flow would be matched to the location of the aggregated process)
* Temporal LCA (no temporal supply chain data available)
* Contribution analysis (no supply chain data to get contributions from)

As these downsides are significant, this library keeps *both the unit process and aggregated data*, and allows you to choose which to use during each calculation.

## Estimating speedups

Start by getting an estimate on how much faster an aggregated calculation would be with:

```python
import bw_aggregated as bwa
bwa.AggregatedDatabase.estimate_speedup("<database label>")
```

That will return something like:

```python
Speedup(
    database_name='USEEIO-2.0',
    time_with_aggregation=0.06253910064697266,
    time_without_aggregation=0.026948928833007812,
    time_difference_absolute=0.035590171813964844,
    time_difference_relative=2.3206525585674855
)
```

The times reported include `LCA` object creation, data loading, matrix construcion, and inventory calculations.

As you can see, creating aggregated activities to avoid solving linear systems will not always lead to faster calculations, as the linear algebra libraries we use are pretty fast, and loading lots of data into the biosphere can take a lot of time. Please check on potential speedups before deciding to aggregate background databases.

## Conversion of existing databases

If you want to convert a database, you can with:

```python
bwa.AggregatedDatabase.convert_existing("<database label>")
```

From now on, calling `bw2data.Database("<database label>")` will return an instance of `AggregatedDatabase`. You can do everything you normally would with this database, including making changes.

> :warning: Any **existing `Database("<database label>")` reference is out of date**: You need to create new `Database` class instances.

The conversion command will also set the default to use the aggregated values during calculations. You can change the default back to using unit process data with:

```python
import bw2data as bd
bd.Database("<database label>").use_aggregated(False)
```

## Creation of new aggregated databases

To create a new `Database` as aggregated from the beginning, use:

```python
bd.Database('<name>', backend='aggregated')
```

You can then write data with `.write(some_data)`, and the aggregated datapackage will be generated automatically. However, individual changes to nodes or edges won't trigger a recalculation of the aggregated results - that needs to be done manually, see below.

## Controlling when aggregation is used

You can also use a context manager to control which aggregated databases use their aggregated values during a calculation. The context manager allows you to set things globally - for example, to force the use of aggregated values for all aggregated databases:

```python
import bw2calc as bc

with bwa.AggregationContext(True):
    lca = bc.LCA(my_functional_unit)
    lca.lci()
```

Passing in `False` will disable all use of aggregated values during the calculation. You can also be more fine grained by using a dictionary of database labels:

```python
with bwa.AggregationContext({"<database label>": True, "<another database label>": False}):
    lca = bc.LCA(my_functional_unit)
    lca.lci()
```

As above, `True` forces the use of aggregated values, `False` prohibits their use.

## Refreshing aggregated calculations

Aggregated database results are checked at calculation time to make sure they are still valid. If the aggregated results are out of date, an `ObsoleteAggregatedDatapackage` error will be raised. You can then refresh the aggregation result cache with:

```python
bd.Database("<database label>").refresh()
```

We don't do that for you automatically as it is usually quite computationally expensive.

You can build inventories such that two aggregated databases mutually reference each other. If both are obsolete, trying to refresh one will raise an error that the other is obsolete. In this case, you can refresh all obsolete aggregated databases with:

```python
bwa.AggregatedDatabase.refresh_all()