from aspish import predicate, var
from aspish.language import (
    Rule,
    Variable,
    Expression,
    OperatorName,
    BinaryOperator,
    to_ast,
)
from aspish import ast


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


class Test_Variable:
    def test_eq(self):
        actual = var('X') == var('Y')
        assert isinstance(actual, BinaryOperator)
        assert actual.operator == OperatorName.equal
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
        pred = predicate('a', ('x',))
        assert to_ast(pred(123)) == ast.ASTFunction(name='a', arguments=(ast.ASTLiteral(123),))

    def test_Rule(self):
        pred = predicate('a', ('x',))
        actual = to_ast(pred(1) <= pred(2))
        expected = ast.ASTRule(
            head=ast.ASTFunction(name='a', arguments=(ast.ASTLiteral(1),)),
            body=(
                ast.ASTFunction(
                    name='a',
                    arguments=(ast.ASTLiteral(2),)
                ),
            )
        )
        assert actual == expected

    def test_BinaryOperator(self):
        assert to_ast(var('X') == 1) == ast.ASTBinaryOperator(
            name=OperatorName.equal,
            left=ast.ASTVariable('X'),
            right=ast.ASTLiteral(1)
        )
