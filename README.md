# ASPish - Answer Set Programming for Python


ASPish is a library that aims to provide some parts of [ASP (Anser Set Programming)](https://en.wikipedia.org/wiki/Answer_set_programming) in a Python-friendly way. All the heavy lifting is done by [clingo](https://github.com/potassco/clingo), a mature implementation of ASP. This library merely provides an interface that allows for a more streamlined usage from Python than the official Python bindings.

ASP can be approximately viewed as the combination of query language that extends datalog, and a satisfiability solver. Both are integrated into a single coherent language which makes ASP particularly convenient when dealing with relational data.

Currently, this project is in early stages and focuses primarily on the query language part.


## Basic Usage

```python
from aspish import Solver, predicate, var

# declarations
edge = predicate('edge', ('x', 'y'))
path = predicate('path', ('x', 'y'))

solver = Solver()
X, Y, Z = map(var, 'XYZ')

# add facts
solver.add(
    edge(1, 2),
    edge(2, 3)
)

# add rules
solver.add(
    path(X, Y) <= edge(X, Y),
    path(X, Y) <= (
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
