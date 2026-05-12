from aspish import predicate, var
from aspish.language import (
    Rule,
    get_atom_variables,
)


class Test_Rule_syntax:
    def test_with_single_body_atom(self):
        rel = predicate('a', ('a',))
        actual = rel(1) <= rel(2)
        assert isinstance(actual, Rule)
        assert actual.head == rel(1)
        assert actual.body == (rel(2),)

    def test_with_multiple_body_atom(self):
        rel = predicate('a', ('a',))
        actual = rel(1) <= (rel(2), rel(3))
        assert isinstance(actual, Rule)
        assert actual.head == rel(1)
        assert actual.body == (rel(2), rel(3))


class Test_get_predicate_variables:
    def test_returns_set_of_variables(self):
        a = predicate('a', ('x',))
        assert get_atom_variables(a(var('X'))) == {var('X'),}
