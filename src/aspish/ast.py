from typing import Generator
from dataclasses import dataclass
from .const import ComparisonOperator, BinaryOperator, UnaryOperator


@dataclass(frozen=True, slots=True)
class ASTNode:
    @property
    def children(self) -> Generator['ASTNode', None, None]:
        yield from ()


@dataclass(frozen=True, slots=True)
class ASTVariable(ASTNode):
    """Internal hashable representation of Variable without dunder methods."""
    name: str


@dataclass(frozen=True, slots=True)
class ASTLiteral(ASTNode):
    value: int | str


@dataclass(frozen=True, slots=True)
class ASTFunction(ASTNode):
    name: str
    arguments: tuple[ASTNode, ...]
    source_cls: type

    @property
    def arity(self) -> int:
        return len(self.arguments)

    @property
    def signature(self) -> tuple[str, int]:
        return (self.name, self.arity)

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield from self.arguments


@dataclass(frozen=True, slots=True)
class ASTRule(ASTNode):
    head: ASTNode | None
    body: tuple[ASTNode, ...]

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        if self.head is not None:
            yield self.head
        yield from self.body


@dataclass(frozen=True, slots=True)
class ASTComparison(ASTNode):
    name: ComparisonOperator
    left: ASTNode
    right: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.left
        yield self.right


@dataclass(frozen=True, slots=True)
class ASTBinaryOperation(ASTNode):
    name: BinaryOperator
    left: ASTNode
    right: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.left
        yield self.right


@dataclass(frozen=True, slots=True)
class ASTNot(ASTNode):
    arg: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.arg


@dataclass(frozen=True, slots=True)
class ASTPool(ASTNode):
    values: tuple[ASTNode, ...]

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield from self.values


@dataclass(frozen=True, slots=True)
class ASTTuple(ASTNode):
    values: tuple[ASTNode, ...]

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield from self.values


@dataclass(frozen=True, slots=True)
class ASTChoice(ASTNode):
    head: ASTNode
    body: tuple[ASTNode, ...]
    at_least: int
    at_most: int | None

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.head
        yield from self.body


@dataclass(frozen=True, slots=True)
class ASTInterval(ASTNode):
    min_value: ASTNode
    max_value: ASTNode


@dataclass(frozen=True, slots=True)
class ASTUnaryOperation(ASTNode):
    operator: UnaryOperator
    arg: ASTNode

    @property
    def children(self) -> Generator[ASTNode, None, None]:
        yield self.arg


class ASTVisitor:
    def visit(self, node: ASTNode) -> None:
        node_type = type(node).__name__
        visit_func = getattr(self, f'visit_{node_type}', None)
        expand = True
        if visit_func is not None:
            expand = visit_func(node) or True
        if expand:
            for child in node.children:
                self.visit(child)
        leave_func = getattr(self, f'leave_{node_type}', None)
        if leave_func is not None:
            leave_func(node)


class UsedFunctionClasses(ASTVisitor):
    def __init__(self):
        self.functions = set()

    def visit_ASTFunction(self, node: ASTFunction) -> bool:
        self.functions.add(node.source_cls)
        return True
