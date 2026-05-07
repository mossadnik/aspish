from typing import Iterable
import re
import inspect
from dataclasses import dataclass


PAT_VARIABLE_NAME = re.compile(r'_*(?:[A-Z]\w*)$')
PAT_PREDICATE_NAME = re.compile(r'_*[a-z]\w*$')


def validate_variable_name(name: str) -> bool:
    if name == '_':
        return True
    elif PAT_VARIABLE_NAME.match(name):
        return True
    return False


def validate_predicate_name(name: str) -> bool:
    return PAT_PREDICATE_NAME.match(name) is not None


def validate_atom(atom: 'Atom') -> bool:
    if any(not isinstance(a, (int, str, Variable)) for a in atom.attributes):
        return False
    return True


def _get_atom_variables(atom: 'Atom') ->'set[Variable]':
    res = set()
    for a in atom.attributes:
        if isinstance(a, Atom):
            res.update(_get_atom_variables(a))
        elif isinstance(a, Variable):
            res.add(a)
    return res


def validate_rule(rule: 'Rule') -> bool:
    # All variables in head are bound in body
    head_vars = _get_atom_variables(rule.head)
    if BLANK in head_vars:
        return False
    # body variables for positive atoms only
    body_vars = set().union(*(_get_atom_variables(a) for a in rule.body if isinstance(a, Atom)))
    if head_vars.difference(body_vars):
        return False
    return True


@dataclass(frozen=True)
class Predicate:
    """A Predicate represents class-level data for Atoms."""
    name: str
    signature: inspect.Signature

    def __post_init__(self):
        if not validate_predicate_name(self.name):
            raise InvalidStatement(f'Invalid predicate name: {self.name}')

    @property
    def arity(self) -> int:
        return len(self.signature.parameters)

    @property
    def attributes(self):
        return tuple(self.signature.parameters.keys())

    def __call__(self, *args, **kwargs) -> 'Atom':
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return Atom(self, bound.args)


@dataclass(frozen=True)
class Atom:
    """An Atom is an instance of a Predicate."""
    predicate_: Predicate
    attributes: tuple

    def __post_init__(self):
        if not validate_atom(self):
            raise InvalidStatement(f'Invalid statement {self}')

    def __le__(self, other: 'Atom | Not | tuple[Atom | Not, ...]') -> 'Rule':
        if not isinstance(other, tuple):
            other = (other,)
        return Rule(self, other)



@dataclass(frozen=True)
class Not:
    arg: Atom


class InvalidStatement(ValueError):
    pass


@dataclass(frozen=True)
class Variable:
    """A variable used for matching in rules."""
    name: str

    def __post_init__(self):
        if not validate_variable_name(self.name):
            raise InvalidStatement(f'Invalid variable name: {self.name}')


@dataclass(frozen=True)
class Rule:
    head: Atom
    body: tuple[Atom | Not, ...]

    def __post_init__(self):
        if not validate_rule(self):
            raise InvalidStatement(f'Invalid rule: {self}.')


def make_signature(names: Iterable[str]) -> inspect.Signature:
    params = []
    for name in names:
        param = inspect.Parameter(
            name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=BLANK
        )
        params.append(param)
    return inspect.Signature(params)


def predicate(name: str, attributes: Iterable[str]) -> 'Predicate':
    return Predicate(name, make_signature(attributes))


def not_(arg: Atom):
    return Not(arg)


def var(name: str) -> Variable:
    return Variable(name)


BLANK = Variable('_')
