from typing import Generator
from dataclasses import dataclass, fields


@dataclass(frozen=True, slots=True)
class Atom:
    # need args/kwargs so that static type checker does not complain about subclass constructor
   def __init__(self, *args, **kwargs):
       super().__init__()

   def __le__(self, other: 'Atom | Not | tuple[Atom | Not, ...]') -> 'Rule':
        if not isinstance(other, tuple):
            other = (other,)
        return Rule(self, other)


@dataclass(frozen=True)
class Not:
    arg: Atom


@dataclass(frozen=True)
class Variable:
    """A variable used for matching in rules."""
    name: str


@dataclass(frozen=True)
class Rule:
    head: Atom
    body: tuple[Atom | Not, ...]


BLANK = Variable('_')


def get_predicate_signature(atom: type[Atom]):
    return (atom.__name__, len(atom.__dataclass_fields__))


def iter_atom_attributes(atom: Atom) -> Generator:
    for f in fields(atom):
        yield getattr(atom, f.name)


def get_atom_variables(atom: Atom) -> set[Variable]:
    res = set()
    for a in iter_atom_attributes(atom):
        if isinstance(a, Atom):
            res.update(get_atom_variables(a))
        elif isinstance(a, Variable):
            res.add(a)
    return res
