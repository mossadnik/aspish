"""Validation of language inputs."""

import re
from dataclasses import fields
from .language import (
    Function,
)


def get_predicate_signature(func: type[Function]):
    return (func.__name__, len(fields(func)))


def iter_atom_attributes(func: Function):
    for f in fields(func):
        yield getattr(func, f.name)


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


def validate_fact(func: Function) -> set[type[Function]]:
    res = {type(func),}
    for a in iter_atom_attributes(func):
        if isinstance(a, Function):
            res.update(validate_fact(a))
        elif not isinstance(a, (int, str)):
            raise InvalidStatement(f'Invalid argument for fact: {func}')
    return res
