import pytest
from aspish import Solver, predicate, var, not_
from aspish.validators import InvalidStatement


class Test_basic_usage:
    def test_binary_relation_closure(self):
        sol = Solver()
        path = predicate('path', ('x', 'y'))
        edge = predicate('edge', ('x', 'y'))
        X, Y, Z = map(var, 'XYZ')
        sol.add(edge(1, 2))
        sol.add(edge(2, 3))
        sol.add(path(X, Y) <= edge(X, Y))
        sol.add(path(X, Y) <= (edge(X, Z), path(Z, Y)))
        assert sol.solve()
        actual = sol.get(path)
        expected = {path(1, 2), path(2, 3), path(1, 3)}
        assert set(actual) == expected

    def test_negation(self):
        sol = Solver()
        a = predicate('a', ('x',))
        sol.add(a(1))
        sol.add(a(2) <= not_(a(1)))
        sol.add(a(3) <= not_(a(2)))
        assert sol.solve()
        actual = sol.get(a)
        expected = {a(1), a(3)}
        assert set(actual) == expected

    def test_arithmetic_examples(self):
        """Clingo guide examples."""
        sol = Solver()
        left = predicate('left', ('val',))
        right = predicate('right', ('val',))
        result = predicate('result', ('name', 'val'))
        L, R = map(var, 'LR')
        sol.add(
            left(7),
            right(2)
        )
        sol.add(
            result('plus', L + R) <= (left(L), right(R)),
            result('minus', L - R) <= (left(L), right(R)),
        )
        sol.solve()
        actual = {r for r in sol.get(result)}
        assert actual == {
            result('plus', 9),
            result('minus', 5),
        }

class Test_Solver_Interface:
    def test_add_allows_one_or_more_statements(self):
        sol = Solver()
        a = predicate('a', ('x',))
        sol.add(
            a(1),
            a(2),
            a(3) <= a(2)
        ).solve()
        assert set(sol.get(a)) == {a(1), a(2), a(3)}

    def test_solve_model_predicate_filter(self):
        sol = Solver()
        a = predicate('a', ('x',))
        b = predicate('b', ('x',))
        sol.add(a(1), b(2))
        sol.solve()
        assert len(sol.raw_model) == 2
        for predicates in (b, [b]):
            sol.solve(predicates=predicates)
            assert len(sol.raw_model) == 1
            assert len(sol.get(b)) == 1
            assert len(sol.get(a)) == 0


class Test_input_validation:
    def test_invalid_fact(self):
        sol = Solver()
        a = predicate('a', ('x',))
        with pytest.raises(InvalidStatement):
            sol.add(a(None))
