from typing import Generator
from enum import StrEnum
from attrs import define, fields, field


def as_ast(value: 'int | str | Expression') -> 'int | str | Expression | ASTVariable':
    if isinstance(value, Variable):
        return ASTVariable(value.name)
    return value


class OperatorName(StrEnum):
    equal = '='
    not_equal = '!='
    less_than = '<'
    less_than_or_equal = '<='
    greater_than = '>'
    greater_than_or_equal = '>='


@define(frozen=True, eq=False, order=False)
class Expression:
    @property
    def children(self) -> Generator:
        yield from ()

    def __eq__(self, other: 'Expression | int | str') -> 'Expression':
        return BinaryOperator(OperatorName.equal, self, other)

    def __ne__(self, other: 'Expression | int | str') -> 'Expression':
        return BinaryOperator(OperatorName.not_equal, self, other)

    def __lt__(self, other: 'Expression | int | str') -> 'Expression':
        return BinaryOperator(OperatorName.less_than, self, other)

    def __le__(self, other: 'Expression | int | str') -> 'Expression':
        return BinaryOperator(OperatorName.less_than_or_equal, self, other)

    def __gt__(self, other: 'Expression | int | str') -> 'Expression':
        return BinaryOperator(OperatorName.greater_than, self, other)

    def __ge__(self, other: 'Expression | int | str') -> 'Expression':
        return BinaryOperator(OperatorName.greater_than_or_equal, self, other)


@define(frozen=True, eq=False, order=False)
class BinaryOperator(Expression):
    operator: OperatorName
    left: 'Expression | int | str | ASTVariable' = field(converter=as_ast)
    right: 'Expression | int | str | ASTVariable' = field(converter=as_ast)

    @property
    def children(self) -> Generator:
        yield self.left
        yield self.right

@define(frozen=True, eq=False, order=False)
class Variable(Expression):
    """An input variable for building expressions and rules.

    Not hashable, for rule input only.
    """
    name: str


@define(frozen=True, slots=True)
class ASTVariable:
    """Internal hashable representation of Variable without dunder methods."""
    name: str


@define(frozen=True, slots=True)
class Atom:
    # need args/kwargs so that static type checker does not complain about subclass constructor
   def __init__(self, *args, **kwargs):
       super().__init__()

   def __le__(self, other: 'Atom | Not | tuple[Atom | Not | Expression, ...]') -> 'Rule':
        if not isinstance(other, tuple):
            other = (other,)
        return Rule(self, other)


@define(frozen=True)
class Not:
    arg: Atom


@define(frozen=True)
class Rule:
    head: Atom
    body: tuple[Atom | Not | Expression, ...]


BLANK = Variable('_')


def get_predicate_signature(atom: type[Atom]):
    return (atom.__name__, len(fields(atom)))


def iter_atom_attributes(atom: Atom) -> Generator:
    for f in fields(atom):
        yield getattr(atom, f.name)


def get_atom_variables(atom: Atom) -> set[ASTVariable]:
    res = set()
    for a in iter_atom_attributes(atom):
        if isinstance(a, Atom):
            res.update(get_atom_variables(a))
        elif isinstance(a, ASTVariable):
            res.add(a)
    return res


def iter_rule_atoms(rule: Rule, head: bool = True, negative: bool = True) -> Generator[Atom, None, None]:
    if head:
        yield rule.head
    for obj in rule.body:
        if isinstance(obj, Atom):
            yield obj
        elif negative and isinstance(obj, Not):
            yield obj.arg
