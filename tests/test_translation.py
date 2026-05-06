import string
import pytest
import clingo
from aspish.translation import translate, deserialize
from aspish.language import new_function, Rule, Variable, not_


class Test_translate:
    def test_string_printable_characters(self):
        """Some characters in the ASCII range need separate serde due to escaping in clingo.

        Test full roundtrip to ensure all printable ASCII characters are handled.
        """
        for c in string.printable:
            roundtrip = deserialize(clingo.parse_term(translate(c)), {})
            assert roundtrip == c

    def test_string_unicode(self):
        for c in 'АСПИШ':
            roundtrip = deserialize(clingo.parse_term(translate(c)), {})
            assert roundtrip == c

    @pytest.mark.parametrize('value, expected', [
        (1, '1'),
        (-1, '-1')
    ])
    def test_int(self, value, expected):
        assert translate(value) == expected

    def test_variable(self):
        assert translate(Variable('X')) == 'X'

    def test_atom(self):
        rel = new_function('a', ('a', 'b'))
        atom = rel(1, 'b')
        assert translate(atom) == 'a(1, "b")'

    def test_rule(self):
        rel = new_function('a', ('a','b'))
        X = Variable('X')
        rule = Rule(rel(X, 1), (rel(X, 2),))
        assert translate(rule) == 'a(X, 1) :- a(X, 2)'

    def test_not_exists(self):
        rel = new_function('a', ('a',))
        assert translate(not_(rel(1))) == 'not a(1)'
