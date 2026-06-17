import pytest
from aspish.validators import (
    InvalidStatement,
    validate_function_name,
    validate_variable_name,
    validate_fact,
)
from aspish import function_, var


class Test_validate_predicate_name:
    @pytest.mark.parametrize('name', ['a', 'a1', 'a_b', 'aB', '_a', '__a'])
    def test_valid_names(self, name):
        assert validate_function_name(name) is None

    @pytest.mark.parametrize('name', ['A', '_A', '__A', 'a b'])
    def test_invalid_names(self, name):
        with pytest.raises(InvalidStatement):
            validate_function_name(name)


class Test_validate_variable_name:
    @pytest.mark.parametrize('name', ['A', '_', '_A', '__A', 'Abc_Def', '_Abc_123'])
    def test_accepts(self, name):
        assert validate_variable_name(name) is None

    @pytest.mark.parametrize('name', ['a', '_a', '__', '_1', '1', 'A B'])
    def test_rejects(self, name):
        with pytest.raises(InvalidStatement):
            validate_variable_name(name)


class Test_validate_fact:
    @pytest.mark.parametrize('value', [1, 'a'])
    def test_accepts(self, value):
        a = function_('a', ('x',))
        assert validate_fact(a(value)) == {a,}

    def test_accepts_nested_functions(self):
        a = function_('a', ('x',))
        b = function_('b', ('x',))
        assert validate_fact(a(b(1))) == {a, b}

    @pytest.mark.parametrize('value', [None, 1.1, var('X')])
    def test_rejects(self, value):
        a = function_('a', ('x',))
        with pytest.raises(InvalidStatement):
            validate_fact(a(value))
