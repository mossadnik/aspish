import string
import pytest
import clingo
import operator
from aspish.translation import translate, deserialize
from aspish.language import to_ast
from aspish.ast import ASTVariable
from aspish import not_, predicate, var


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
        assert translate(ASTVariable('X')) == 'X'

    def test_atom(self):
        rel = predicate('a', ('a', 'b'))
        atom = rel(1, 'b')
        assert translate(atom) == 'a(1, "b")'

    def test_rule(self):
        rel = predicate('a', ('a','b'))
        X = var('X')
        rule = rel(X, 1) <= rel(X, 2)
        assert translate(to_ast(rule)) == 'a(X, 1) :- a(X, 2)'

    def test_not_exists(self):
        rel = predicate('a', ('a',))
        assert translate(to_ast(not_(rel(1)))) == 'not a(1)'

    @pytest.mark.parametrize('op, expected', [
        [operator.eq, '='],
        [operator.ne, '!='],
        [operator.lt, '<'],
        [operator.le, '<='],
        [operator.gt, '>'],
        [operator.ge, '>='],
    ])
    def test_binary_operator(self, op, expected):
        X, Y = map(var, 'XY')
        assert translate(to_ast(op(X, Y))) == f'X {expected} Y'
