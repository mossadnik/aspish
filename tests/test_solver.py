import aspish as asp
from aspish.language import predicate



def assert_equal_list_of_dict(this: list[dict], that: list[dict]):
    def to_tuples(data: list[dict]) -> list[tuple]:
        return sorted([
            tuple(sorted(row.items()))
            for row in data
        ])
    assert to_tuples(this) == to_tuples(that)


class Test_basic_usage:
    def test_binary_relation_closure(self):
        sol = asp.Solver()
        path = predicate('path', ('x', 'y'))
        edge = predicate('edge', ('x', 'y'))
        X, Y, Z = map(asp.var, 'XYZ')
        sol.add(edge(1, 2))
        sol.add(edge(2, 3))
        sol.add(path(X, Y) <= edge(X, Y))
        sol.add(path(X, Y) <= (edge(X, Z), path(Z, Y)))
        assert sol.solve()
        assert len(sol._answer) == 5
        actual = sol.get(path)
        expected = [{'x': 1, 'y': 2}, {'x': 2, 'y': 3}, {'x': 1, 'y': 3}]
        assert_equal_list_of_dict(actual, expected)

    def test_negation(self):
        sol = asp.Solver()
        rel = predicate('a', ('x',))
        sol.add(rel(1))
        sol.add(rel(2) <= asp.not_(rel(1)))
        sol.add(rel(3) <= asp.not_(rel(2)))
        assert sol.solve()
        actual = sol.get(rel)
        expected = [
            {'x': 1},
            {'x': 3}
        ]
        assert_equal_list_of_dict(actual, expected)


class Test_Solver_Interface:
    def test_add_allows_one_or_more_statements(self):
        sol = asp.Solver()
        a = predicate('a', ('x',))
        sol.add(
            a(1),
            a(2),
            a(3) <= a(2)
        ).solve()
        assert_equal_list_of_dict(sol.get(a), [{'x': i + 1} for i in range(3)])
