from typing import TypeAlias
from functools import singledispatch
from attrs import define, fields
from .const import ComparisonOperator, BinaryOperator, UnaryOperator
from . import ast


AnyExpression: TypeAlias = 'Expression | int | str | tuple[AnyExpression, ...]'
Body: TypeAlias = 'Atom | Comparison | Not | tuple[Atom | Comparison | Not, ...]'
BodyAtom: TypeAlias = 'Atom | Comparison | Not'


@define(frozen=True, eq=False, order=False)
class Expression:
    def __eq__(self, other: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.equal, self, other)

    def __ne__(self, other: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.not_equal, self, other)

    def __lt__(self, other: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.less_than, self, other)

    def __le__(self, other: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.less_than_or_equal, self, other)

    def __gt__(self, other: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.greater_than, self, other)

    def __ge__(self, other: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.greater_than_or_equal, self, other)

    def __add__(self, other: 'Expression | int') -> 'Expression':
        return BinaryOperation(BinaryOperator.plus, self, other)

    def __radd__(self, other: 'Expression | int') -> 'Expression':
        return BinaryOperation(BinaryOperator.plus, other, self)

    def __sub__(self, other: 'Expression | int') -> 'Expression':
        return BinaryOperation(BinaryOperator.minus, self, other)

    def __rsub__(self, other: 'Expression | int') -> 'Expression':
        return BinaryOperation(BinaryOperator.minus, other, self)

    def __neg__(self) -> 'Expression':
        return UnaryOperation(UnaryOperator.minus, self)

    def isin(self, *values: AnyExpression) -> 'Comparison':
        return Comparison(ComparisonOperator.equal, self, Pool(values))

    def between(self, min_value: int, max_value: int) -> 'Comparison':
        return Comparison(ComparisonOperator.equal, self, Interval(min_value, max_value))


@define(frozen=True, eq=False, order=False)
class Pool(Expression):
    values: tuple[AnyExpression, ...]


@define(frozen=True, eq=False, order=False)
class Interval(Expression):
    min_value: int
    max_value: int


@define(frozen=True, eq=False, order=False)
class UnaryOperation(Expression):
    operator: UnaryOperator
    arg: Expression


@define(frozen=True, eq=False, order=False)
class BinaryOperation(Expression):
    operator: BinaryOperator
    left: AnyExpression
    right: AnyExpression


@define(frozen=True, eq=False, order=False)
class Comparison:
    operator: ComparisonOperator
    left: AnyExpression
    right: AnyExpression


@define(frozen=True, eq=False, order=False)
class Variable(Expression):
    """An input variable for building expressions and rules.

    Not hashable, for rule input only.
    """
    name: str


@define(frozen=True, slots=True)
class Atom:
    # need args/kwargs so that static type checker does not complain about subclass constructor
   def __init__(self, *args, **kwargs):
       super().__init__()

   def __le__(self, other: Body) -> 'Rule':
        if not isinstance(other, tuple):
            other = (other,)
        return Rule(self, other)


@define(frozen=True)
class Not:
    arg: Atom


@define(frozen=True)
class Rule:
    head: Atom | None
    body: tuple[BodyAtom, ...]


BLANK = Variable('_')


@singledispatch
def to_ast(obj) -> ast.ASTNode:
    raise TypeError(f'Cannot parse object of type {type(obj)}')


@to_ast.register
def _(obj: Variable):
    return ast.ASTVariable(obj.name)


@to_ast.register
def _(obj: Atom) -> ast.ASTNode:
    arguments = map(to_ast, (getattr(obj, a.name) for a in fields(obj)))
    return ast.ASTFunction(name=obj.__class__.__name__, arguments=tuple(arguments))


@to_ast.register
def _(obj: Rule) -> ast.ASTRule:
    head = to_ast(obj.head) if obj.head is not None else None
    body = map(to_ast, obj.body)
    return ast.ASTRule(head, tuple(body))


@to_ast.register
def _(obj: str | int) -> ast.ASTNode:
    return ast.ASTLiteral(obj)


@to_ast.register
def _(obj: Not) -> ast.ASTNode:
    return ast.ASTNot(to_ast(obj.arg))


@to_ast.register
def _(obj: BinaryOperation) -> ast.ASTNode:
    return ast.ASTBinaryOperation(
        name=obj.operator,
        left=to_ast(obj.left),
        right=to_ast(obj.right)
    )


@to_ast.register
def _(obj: Comparison) -> ast.ASTNode:
    return ast.ASTComparison(
        name=obj.operator,
        left=to_ast(obj.left),
        right=to_ast(obj.right)
    )


@to_ast.register
def _(obj: Pool) -> ast.ASTNode:
    return ast.ASTPool(tuple(map(to_ast, obj.values)))


@to_ast.register
def _(obj: Interval) -> ast.ASTNode:
    return ast.ASTInterval(to_ast(obj.min_value), to_ast(obj.max_value))


@to_ast.register
def _(obj: tuple) -> ast.ASTNode:
    return ast.ASTTuple(tuple(map(to_ast, obj)))


@to_ast.register
def _(obj: UnaryOperation) -> ast.ASTNode:
    return ast.ASTUnaryOperation(obj.operator, to_ast(obj.arg))
