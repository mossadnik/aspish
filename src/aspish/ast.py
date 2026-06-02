from typing import Generator
from attrs import define
from .const import ComparisonOperator, BinaryOperator, UnaryOperator


@define(frozen=True, slots=True)
class ASTNode:
    @property
    def children(self) -> Generator['ASTNode', None, None]:
        yield from ()


@define(frozen=True, slots=True)
class ASTVariable(ASTNode):
    """Internal hashable representation of Variable without dunder methods."""
    name: str


@define(frozen=True, slots=True)
class ASTLiteral(ASTNode):
    value: int | str


@define(frozen=True, slots=True)
class ASTFunction(ASTNode):
    name: str
    arguments: tuple[ASTNode, ...]

    @property
    def arity(self) -> int:
        return len(self.arguments)

    @property
    def signature(self) -> tuple[str, int]:
        return (self.name, self.arity)

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield from self.arguments


@define(frozen=True, slots=True)
class ASTRule(ASTNode):
    head: ASTNode
    body: tuple[ASTNode, ...]

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.head
        yield from self.children


@define(frozen=True, slots=True)
class ASTComparison(ASTNode):
    name: ComparisonOperator
    left: ASTNode
    right: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.left
        yield self.right


@define(frozen=True, slots=True)
class ASTBinaryOperation(ASTNode):
    name: BinaryOperator
    left: ASTNode
    right: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.left
        yield self.right


@define(frozen=True, slots=True)
class ASTNot(ASTNode):
    arg: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.arg


@define(frozen=True, slots=True)
class ASTPool(ASTNode):
    values: tuple[ASTNode, ...]

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield from self.values


@define(frozen=True, slots=True)
class ASTInterval(ASTNode):
    min_value: ASTNode
    max_value: ASTNode


@define(frozen=True, slots=True)
class ASTUnaryOperation(ASTNode):
    operator: UnaryOperator
    arg: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.arg
