import operator
import pytest
from aspish.validators import (
    InvalidStatement,
    validate_predicate_name,
    validate_variable_name,
    validate_atom,
    validate_rule,
    validate_fact,
    validate_expression,
    get_atom_variables,
)
from aspish import predicate, var, not_, BLANK
from aspish.language import to_ast


class Test_validate_predicate_name:
    @pytest.mark.parametrize('name', ['a', 'a1', 'a_b', 'aB', '_a', '__a'])
    def test_valid_names(self, name):
        assert validate_predicate_name(name) is None

    @pytest.mark.parametrize('name', ['A', '_A', '__A', 'a b'])
    def test_invalid_names(self, name):
        with pytest.raises(InvalidStatement):
            validate_predicate_name(name)


class Test_validate_variable_name:
    @pytest.mark.parametrize('name', ['A', '_', '_A', '__A', 'Abc_Def', '_Abc_123'])
    def test_accepts(self, name):
        assert validate_variable_name(name) is None

    @pytest.mark.parametrize('name', ['a', '_a', '__', '_1', '1', 'A B'])
    def test_rejects(self, name):
        with pytest.raises(InvalidStatement):
            validate_variable_name(name)


class Test_validate_predicate:
    @pytest.mark.parametrize('value', [1.2, None])
    def test_rejects(self, value):
        a = predicate('a', ('x',))
        with pytest.raises(InvalidStatement):
            validate_atom(a(value))

    @pytest.mark.parametrize('value', [1, 'a', var('X')])
    def test_accepts(self, value):
        a = predicate('a', ('x',))
        assert validate_atom(a(value)) is None


class Test_validate_rule:
    def test_accepts(self):
        a = predicate('a', ('x',))
        assert validate_rule(a(1) <= a(2)) is None

    def test_raises_if_head_variable_not_bound(self):
        a = predicate('a', ('x',))
        X, Y = map(var, 'XY')
        with pytest.raises(InvalidStatement):
            validate_rule(a(X) <= a(Y))

    def test_raises_if_head_contains_BLANK(self):
        a = predicate('a', ('x',))
        with pytest.raises(InvalidStatement):
            validate_rule(a(BLANK) <= a(BLANK))

    def test_raises_if_head_variable_not_bound_to_positive_body_atom(self):
        a = predicate('a', ('x',))
        X, Y = map(var, 'XY')
        with pytest.raises(InvalidStatement):
            validate_rule(a(X) <= (a(Y), not_(a(X))))

    def test_raises_if_any_atom_is_invalid(self):
        a = predicate('a', ('x',))
        with pytest.raises(InvalidStatement):
            validate_rule(a(None) <= a(1))
        with pytest.raises(InvalidStatement):
            validate_rule(a(1) <= a(None))
        with pytest.raises(InvalidStatement):
            validate_rule(a(1) <= (a(2), not_(a(None))))

    def test_accepts_variables_bound_through_expression(self):
        a = predicate('a', ('x',))
        X, Y = map(var, 'XY')
        assert validate_rule(a(X) <= (a(Y), X == Y)) is None

    def test_rejects_variables_bound_through_unsafe_expression(self):
        a = predicate('a', ('x',))
        X, Y = map(var, 'XY')
        with pytest.raises(InvalidStatement):
            validate_rule(a(X) <= (a(Y), X != Y))

    def test_raises_if_body_expression_invalid(self):
        a = predicate('a', ('x',))
        X, Y = map(var, 'XY')
        with pytest.raises(InvalidStatement):
            validate_rule(a(1) <= (X == (Y == 1), a(X), a(Y)))


class Test_validate_fact:
    @pytest.mark.parametrize('value', [1, 'a'])
    def test_accepts(self, value):
        a = predicate('a', ('x',))
        assert validate_fact(a(value)) is None

    @pytest.mark.parametrize('value', [None, 1.1, var('X')])
    def test_rejects(self, value):
        a = predicate('a', ('x',))
        with pytest.raises(InvalidStatement):
            validate_fact(a(value))


class Test_validate_expression:
    @pytest.mark.parametrize('op', [operator.eq, operator.ne, operator.lt, operator.le, operator.gt, operator.ge])
    def test_boolean_operators_must_be_expression_roots(self, op):
        X, Y, Z = map(var, 'XYZ')
        expr = op(X, Y) == Z
        with pytest.raises(InvalidStatement):
            validate_expression(expr)


class Test_get_predicate_variables:
    def test_returns_set_of_variable_names(self):
        a = predicate('a', ('x',))
        assert get_atom_variables(a(var('X'))) == {'X',}
