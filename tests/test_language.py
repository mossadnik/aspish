import pytest
from aspish import function_, var
from aspish.const import ComparisonOperator, BinaryOperator
from aspish.language import (
    Rule,
    Variable,
    Comparison,
    to_ast,
)
from aspish import ast



class Test_Atom_hashability:
    def test_facts_are_hashable(self):
        """Facts can only contain hashable types."""
        a = function_('a', ('x', 'y'))
        a1 = a(123, 'abc')
        a2 = a(123, 'abc')
        a3 = a('abc', 123)
        assert {a1, a2, a3} == {a1, a3}


    def test_atoms_with_expressions_are_not_hashable(self):
        """Expressions are not hashable due to overriding `==`."""
        a = function_('a', ('x', 'y'))
        X = var('X')
        with pytest.raises(TypeError):
            hash(a(1, X))


class Test_Rule_syntax:
    def test_with_single_body_atom(self):
        rel = function_('a', ('a',))
        actual = rel(1) <= rel(2)
        assert isinstance(actual, Rule)
        assert actual.head == rel(1)
        assert actual.body == (rel(2),)

    def test_with_multiple_body_atom(self):
        rel = function_('a', ('a',))
        actual = rel(1) <= (rel(2), rel(3))
        assert isinstance(actual, Rule)
        assert actual.head == rel(1)
        assert actual.body == (rel(2), rel(3))


class Test_Variable:
    def test_eq(self):
        actual = var('X') == var('Y')
        assert isinstance(actual, Comparison)
        assert actual.operator == ComparisonOperator.equal
        assert isinstance(actual.left, Variable)
        assert actual.left.name == 'X'
        assert isinstance(actual.right, Variable)
        assert actual.right.name == 'Y'


class Test_to_ast:
    def test_Variable(self):
        assert to_ast(var('X')) == ast.ASTVariable('X')

    def test_Literal(self):
        assert to_ast(123) == ast.ASTLiteral(123)
        assert to_ast('abc') == ast.ASTLiteral('abc')

    def test_Function(self):
        pred = function_('a', ('x',))
        assert to_ast(pred(123)) == ast.ASTFunction(
            name='a',
            arguments=(ast.ASTLiteral(123),),
            source_cls=pred
        )

    def test_Rule(self):
        pred = function_('a', ('x',))
        actual = to_ast(pred(1) <= pred(2))
        expected = ast.ASTRule(
            head=ast.ASTFunction(
                name='a',
                arguments=(ast.ASTLiteral(1),),
                source_cls=pred
            ),
            body=(
                ast.ASTFunction(
                    name='a',
                    arguments=(ast.ASTLiteral(2),),
                    source_cls=pred
                ),
            )
        )
        assert actual == expected

    def test_Comparison(self):
        assert to_ast(var('X') == 1) == ast.ASTComparison(
            name=ComparisonOperator.equal,
            left=ast.ASTVariable('X'),
            right=ast.ASTLiteral(1)
        )

    def test_BinaryOperation(self):
        assert to_ast(var('X') + 1) == ast.ASTBinaryOperation(
            name=BinaryOperator.plus,
            left=ast.ASTVariable('X'),
            right=ast.ASTLiteral(1)
        )

    def test_BinaryOperation_right(self):
        assert to_ast(1 - var('X')) == ast.ASTBinaryOperation(
            name=BinaryOperator.minus,
            left=ast.ASTLiteral(1),
            right=ast.ASTVariable('X')
        )
