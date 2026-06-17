import pytest
from aspish import Solver, function_, var, not_, constraint, choose, tuple_
from aspish.validators import InvalidStatement


class Test_basic_usage:
    def test_binary_relation_closure(self):
        sol = Solver()
        path = function_('path', ('x', 'y'))
        edge = function_('edge', ('x', 'y'))
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
        a = function_('a', ('x',))
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
        left = function_('left', ('val',))
        right = function_('right', ('val',))
        result = function_('result', ('name', 'val'))
        L, R = map(var, 'LR')
        sol.add(
            left(7),
            right(2)
        )
        sol.add(
            result('plus', L + R) <= (left(L), right(R)),
            result('minus', L - R) <= (left(L), right(R)),
            result('uminus', -R) <= right(R),
        )
        sol.solve()
        actual = {r for r in sol.get(result)}
        assert actual == {
            result('plus', 9),
            result('minus', 5),
            result('uminus', -2),
        }

    def test_isin(self):
        sol = Solver()
        a = function_('a', ('x',))
        X = var('X')
        sol.add(a(X) <= X.isin(1, 2, 'x'))
        sol.solve()
        assert set(sol.get(a)) == {a(1), a(2), a('x')}

    def test_returns_False_if_unsat(self):
        sol = Solver()
        a = function_('a', ('x',))
        sol.add(
            a(1),
            constraint(a(1))
        )
        assert not sol.solve()

    def test_tuple_input_and_output(self):
        solver = Solver()
        X, Y = map(var, 'XY')
        a = function_('a', ('x',))
        solver.add(a(tuple_(X, Y)) <= (X == 1, Y.between(2, 3)))
        solver.solve()
        assert set(solver.get(a)) == {a((1, 2)), a((1, 3))}


class Test_Solver_Interface:
    def test_add_allows_one_or_more_statements(self):
        sol = Solver()
        a = function_('a', ('x',))
        sol.add(
            a(1),
            a(2),
            a(3) <= a(2)
        ).solve()
        assert set(sol.get(a)) == {a(1), a(2), a(3)}

    def test_solve_model_predicate_filter(self):
        sol = Solver()
        a = function_('a', ('x',))
        b = function_('b', ('x',))
        sol.add(a(1), b(2))
        sol.solve()
        assert len(sol.raw_model) == 2
        for predicates in (b, [b]):
            sol.solve(predicates=predicates)
            assert len(sol.raw_model) == 1
            assert len(sol.get(b)) == 1
            assert len(sol.get(a)) == 0

    def test_deserializes_nested_functions(self):
        sol = Solver()
        a = function_('a', ('x',))
        b = function_('b', ('x',))
        sol.add(a(b(1)))
        assert sol.solve()
        assert sol.get(a) == [a(b(1))]

    def test_solve_choice(self):
        """Choose three distinct numbers from 1..3"""
        sol = Solver()
        a = function_('a', ('x',))
        b = function_('b', ('x',))
        X, Y, Z = map(var, 'XYZ')
        sol.add(
            a(1),
            choose(b(X), X.between(1, 3), at_least=1, at_most=1),
            constraint(a(X), a(Y), b(Z), X + Y != Z)
        )
        assert sol.solve()
        assert sol.get(b) == [b(2)]

class Test_input_validation:
    def test_invalid_fact(self):
        sol = Solver()
        a = function_('a', ('x',))
        with pytest.raises(InvalidStatement):
            sol.add(a(None))
