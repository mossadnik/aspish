# ASPish - Answer Set Programming for Python


ASPish is a library that aims to provide some parts of [ASP (Answer Set Programming)](https://en.wikipedia.org/wiki/Answer_set_programming) in a Python-friendly way. All the heavy lifting is done by [clingo](https://github.com/potassco/clingo), a mature implementation of ASP. This library merely provides an interface that allows for a more streamlined usage from Python than the official Python bindings.

ASP can be approximately viewed as the combination of query language that extends datalog, and a satisfiability solver. Both are integrated into a single coherent language which makes ASP particularly convenient when dealing with relational data.

This project is in early stages and is not stable.

## Basic Usage

```python
from aspish import Solver, function_, var

# declarations
edge = function_('edge', ('x', 'y'))
path = function_('path', ('x', 'y'))

solver = Solver()
X, Y, Z = map(var, 'XYZ')

# add facts
solver.add(
    edge(1, 2),
    edge(2, 3)
)

# add rules
solver.add(
    path(X, Y) << edge(X, Y),
    path(X, Y) << (
        edge(X, Z),
        path(Z, Y)
    )
)

# run
solver.solve()
solver.get(path)

# returns
[path(x=1, y=2), path(x=2, y=3), path(x=1, y=3)]
```


### Integrating with external data

Usually the input data will not be entered directly. Instead, we pull facts from a source. Similarly, output data will be converted into a different format. Conversion into and out of aspish facts is not complicated when restricting to atomic attributes only, i.e. when not using nesting like `f(f(1), g(h(2)))`. Then an aspish function is equivalent to a table or dataframe with no nulls and no duplicates.

Here's a minimal example how we can get valid data out of a pyspark DataFrame:

```python
from pyspark.sql import DataFrame
from aspish import signature
from aspish.language import Function

def df2asp(df: DataFrame, func: type[Function]) -> list[Function]:
    sig = signature(func)
    clean = (
        df
        .select(*sig)
        dropna()
        .distinct()
    )
    return [func(**row.asDIct()) for row in clean.collect()]
```

And here's how to convert a collection of functions back to pyspark. We use the fact that all functions created with `apish.function_` are simple dataclasses which can be handled by pandas:

```python
from typing import Iterable
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from aspish.language import Function


def asp2df(data: Iterable[Function], spark: SparkSession) -> DataFrame:
    return spark.createDataFrame(pd.DataFrame(data))
```
