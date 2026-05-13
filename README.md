# ASPish - Answer Set Programming for Python

> aspish is an adjective meaning relating to, resembling, or having the qualities of an [asp](https://en.wikipedia.org/wiki/Asp_(snake))

ASPish is a library that aims to resemble [ASP (Anser Set Programming)](https://en.wikipedia.org/wiki/Answer_set_programming) in a Python-friendly way.


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
