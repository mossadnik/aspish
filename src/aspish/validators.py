"""Validation of language inputs."""

import re
from dataclasses import fields
from .language import (
    Atom,
)


def get_predicate_signature(atom: type[Atom]):
    return (atom.__name__, len(fields(atom)))


def iter_atom_attributes(atom: Atom):
    for f in fields(atom):
        yield getattr(atom, f.name)


PAT_VARIABLE_NAME = re.compile(r'_*(?:[A-Z]\w*)$')
PAT_FUNCTION_NAME = re.compile(r'_*[a-z]\w*$')


class InvalidStatement(ValueError):
    pass


def validate_variable_name(name: str) -> None:
    if name == '_':
        return None
    if not PAT_VARIABLE_NAME.match(name):
        raise InvalidStatement(f'Invalid variable name: {name}')


def validate_function_name(name: str) -> None:
    if not PAT_FUNCTION_NAME.match(name):
        raise InvalidStatement(f'Invalid function name: {name}')


def validate_fact(atom: Atom) -> set[type[Atom]]:
    res = {type(atom),}
    for a in iter_atom_attributes(atom):
        if isinstance(a, Atom):
            res.update(validate_fact(a))
        elif not isinstance(a, (int, str)):
            raise InvalidStatement(f'Invalid argument for fact: {atom}')
    return res
