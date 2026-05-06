import pytest
from aspish.language import (
    new_function,
    not_,
    Atom,
    var,
    Rule,
    BLANK,
    InvalidStatement
)


class Test_Relation:
    @pytest.mark.parametrize('name', ['a', 'a1', 'a_b', 'aB', '_a', '__a'])
    def test_valid_names(self, name):
        rel = new_function(name, ())
        assert rel.name == name

    @pytest.mark.parametrize('name', ['A', '_A', '__A', 'a b'])
    def test_invalid_names(self, name):
        with pytest.raises(InvalidStatement):
            new_function(name, ())

    def test_arity_is_len_of_attributes(self):
        rel = new_function('name', ('a', 'b', 'c'))
        assert rel.arity == 3

    def test_raise_if_called_with_too_many_arguments(self):
        rel = new_function('name', ('a', 'b'))
        with pytest.raises(TypeError):
            rel(1, 2, 3)

    def test_raise_if_duplicate_arguments(self):
        rel = new_function('name', ('a', 'b'))
        with pytest.raises(TypeError):
            rel(1, a=2)

    def test_returns_Atom_with_relation(self):
        rel = new_function('name', ('a', 'b'))
        actual = rel(1, 2)
        assert isinstance(actual, Atom)
        assert actual.function_ == rel

    def test_default_to_blank(self):
        rel = new_function('name', ('a', 'b'))
        actual = rel()
        assert all(a == BLANK for a in actual.attributes)


class Test_Variable_validation:
    @pytest.mark.parametrize('name', ['A', '_', '_A', '__A', 'Abc_Def', '_Abc_123'])
    def test_valid_variable_names(self, name):
        v = var(name)
        assert v.name == name

    @pytest.mark.parametrize('name', ['a', '_a', '__', '_1', '1', 'A B'])
    def test_invalid_variable_names(self, name):
        with pytest.raises(InvalidStatement):
            var(name)


class Test_Atom_validation:
    @pytest.mark.parametrize('value', [1.2, None])
    def test_raises_if_invalid_attribute_value(self, value):
        rel = new_function('a', ('x',))
        with pytest.raises(InvalidStatement):
            rel(value)


class Test_Rule_syntax:
    def test_with_single_body_atom(self):
        rel = new_function('a', ('a',))
        actual = rel(1) <= rel(2)
        assert isinstance(actual, Rule)
        assert actual.head == rel(1)
        assert actual.body == (rel(2),)

    def test_with_multiple_body_atom(self):
        rel = new_function('a', ('a',))
        actual = rel(1) <= (rel(2), rel(3))
        assert isinstance(actual, Rule)
        assert actual.head == rel(1)
        assert actual.body == (rel(2), rel(3))


class Test_Rule_validation:
    def test_raises_if_head_variable_not_bound(self):
        a = new_function('a', ('x',))
        X, Y = map(var, 'XY')
        with pytest.raises(InvalidStatement):
            _ = a(X) <= a(Y)

    def test_raises_if_head_contains_BLANK(self):
        a = new_function('a', ('x',))
        with pytest.raises(InvalidStatement):
            _ = a(BLANK) <= a(BLANK)

    def test_raises_if_head_variable_not_bound_to_positive_body_atom(self):
        a = new_function('a', ('x',))
        X, Y = map(var, 'XY')
        with pytest.raises(InvalidStatement):
            _ = a(X) <= (a(Y), not_(a(X)))