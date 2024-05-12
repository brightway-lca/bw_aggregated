# bw_aggregation

[![PyPI](https://img.shields.io/pypi/v/bw_aggregation.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bw_aggregation.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bw_aggregation)][pypi status]
[![License](https://img.shields.io/pypi/l/bw_aggregation)][license]

[![Read the documentation at https://bw_aggregation.readthedocs.io/](https://img.shields.io/readthedocs/bw_aggregation/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/bw_aggregation/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/bw_aggregation/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/bw_aggregation/
[read the docs]: https://bw_aggregation.readthedocs.io/
[tests]: https://github.com/brightway-lca/bw_aggregation/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/bw_aggregation
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _bw_aggregation_ via [pip] from [PyPI]:

```console
$ pip install bw_aggregation
```

It is also available via `conda` or `mamba` on the channel `cmutel`.

## Theory

This library allows you to trade space for time by pre-computing some inventory results. Each Brightway `Database` can be aggregated - i.e. we can calculate the *cumulative biosphere flows* needed for each process in that flow. We then store these values separately, to be used instead of the normal technosphere supply chain entries. This is faster as we don't need to solve the linear proble `Ax=b` for that database subgraph.

As the supply chain data is removed, we can't do calculations which would use that supply chain data. That means we can't do:

* Uncertainty analysis (no values in the technosphere array to sample from)
* Graph traversal (the graph is cutoff for each process)
* Regionalized LCIA (every biosphere flow would be matched to the location of the aggregated process)
* Temporal LCA (no temporal supply chain data available)
* Contribution analysis (no supply chain data to get contributions from)

As these downsides are significant, this library keeps *both the unit process and aggregated data*, and allows you to choose which to use during each calculation.

## Usage

Start by getting an estimate on how much faster an aggregated calculation would be with:

```python
import bw_aggregated as bwa
bwa.AggregatedDatabase.estimate_speedup("<database label>")
```

That will return something like:

```python
Speedup(
    database_name='ecoinvent-3.10-cutoff', 
    time_with_aggregation=4.297600030899048, 
    time_without_aggregation=2.22904896736145, 
    time_difference_absolute=2.0685510635375977, 
    time_difference_relative=1.9279971386120622
)
```

The times reported include `LCA` object creation, data loading, matrix construcion, and inventory calculations.

As you can see, creating aggregated activities to avoid solving linear systems will not always lead to faster calculations, as the linear algebra libraries we use are pretty fast, and loading lots of data into the biosphere can take a lot of time. Please check on potential speedups before deciding to aggregate background databases.

If you want to convert that database, you can with:

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

To create a new `Database` as aggregated from the beginning, use:

```python
bd.Database('<name>', backend='aggregated')
```

You can then write data with `.write(some_data)`, and the aggregated datapackage will be generated automatically. However, individual changes to nodes or edges won't trigger a recalculation of the aggregated results - that needs to be done manually, see below.

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

Aggregated database results are checked at calculation time to make sure they are still valid. If the aggregated results are out of date, an `ObsoleteAggregatedDatapackage` error will be raised. You can then refresh the aggregation result cache with:

```python
bd.Database("<database label>").refresh()
```

We don't do that for you automatically as it is usually quite computationally expensive.

You can build inventories such that two aggregated databases mutually reference each other. If both are obsolete, trying to refresh one will raise an error that the other is obsolete. In this case, you can refresh all obsolete aggregated databases with:

```python
bwa.AggregatedDatabase.refresh_all()
```

## Implementation

This library gets the possibility of using both aggregated and unit process data by overriding the `.datapackage` method, and loading one or two different datapackages depending on the current context. This approach is compatiable with both manual loading of datapackages, and with the `bw2data` function `prepare_lca_inputs`. The `.datapackage` method of an `AggregatedDatabase` is roughly:

```
if global_context is True:
    load_aggregated()
elif local_context(this_database) is True:
    load_aggregated()
elif this_database.prefer_aggregated is True:
    load_aggregated()
else:
    load_unit_process()
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_bw_aggregation_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://bw_aggregation.readthedocs.io/en/latest/usage.html
[License]: https://github.com/brightway-lca/bw_aggregation/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/bw_aggregation/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/bw_aggregation/issues
