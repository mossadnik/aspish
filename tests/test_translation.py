import string
import pytest
import clingo
import operator
from aspish.translation import translate, deserialize
from aspish.language import to_ast
from aspish.ast import ASTVariable
from aspish import not_, predicate, var


def translates_to(expr, text: str) -> None:
    assert translate(to_ast(expr)) == text


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
        [operator.add, '+'],
        [operator.sub, '-'],
    ])
    def test_binary_operator(self, op, expected):
        X, Y = map(var, 'XY')
        assert translate(to_ast(op(X, Y))) == f'X {expected} Y'
        assert translate(to_ast(op(X, 1))) == f'X {expected} 1'

    @pytest.mark.parametrize('op, expected', [
        [operator.eq, 'X = 1'],
        [operator.ne, 'X != 1'],
        [operator.lt, 'X > 1'],
        [operator.le, 'X >= 1'],
        [operator.gt, 'X < 1'],
        [operator.ge, 'X <= 1'],
        [operator.add, '1 + X'],
        [operator.sub, '1 - X'],
    ])
    def test_binary_operator_right(self, op, expected):
        X = var('X')
        assert translate(to_ast(op(1, X))) == expected

    def test_unary_minus(self):
        X = var('X')
        assert translate(to_ast(X)) == '-X'

    def test_variable_isin(self):
        X, Y = map(var, 'XY')
        assert translate(to_ast(X.isin(1, Y, 'a'))) == 'X = (1;Y;"a")'


class Test_arithmetic_parens:
    """Tests that parens are added in arithmetic where needed."""
    def test_unary_minus_on_binary_operator(self):
        X = var('X')
        assert translate(to_ast(-(X + 1))) == '-(X + 1)'

    def test_unary_minus_on_comparison(self):
        X, Y = map(var, 'XY')
        translates_to(-X == Y, '-X = Y')
