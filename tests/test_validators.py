import pytest
from aspish.validators import (
    InvalidStatement,
    validate_predicate_name,
    validate_variable_name,
    validate_atom,
    validate_rule,
)
from aspish import predicate, var, not_, BLANK


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
    def test_raises_if_invalid_attribute_value(self, value):
        a = predicate('a', ('x',))
        with pytest.raises(InvalidStatement):
            validate_atom(a(value))


class Test_validate_rule:
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
