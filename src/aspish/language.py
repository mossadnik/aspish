from typing import Generator
from dataclasses import dataclass, fields


@dataclass(frozen=True, slots=True)
class Predicate:
   def __le__(self, other: 'Predicate | Not | tuple[Predicate | Not, ...]') -> 'Rule':
        if not isinstance(other, tuple):
            other = (other,)
        return Rule(self, other)


@dataclass(frozen=True)
class Not:
    arg: Predicate


@dataclass(frozen=True)
class Variable:
    """A variable used for matching in rules."""
    name: str


@dataclass(frozen=True)
class Rule:
    head: Predicate
    body: tuple[Predicate | Not, ...]


BLANK = Variable('_')


def get_predicate_signature(pred: type[Predicate]):
    return (pred.__name__, len(pred.__dataclass_fields__))


def iter_atom_attributes(atom: Predicate) -> Generator:
    for f in fields(atom):
        yield getattr(atom, f.name)


def get_atom_variables(atom: Predicate) -> set[Variable]:
    res = set()
    for a in iter_atom_attributes(atom):
        if isinstance(a, Predicate):
            res.update(get_atom_variables(a))
        elif isinstance(a, Variable):
            res.add(a)
    return res
