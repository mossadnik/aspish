"""Validation of language inputs."""
import re
from dataclasses import astuple
from .language import Variable, Atom, Rule, BLANK
from .language import get_atom_variables


PAT_VARIABLE_NAME = re.compile(r'_*(?:[A-Z]\w*)$')
PAT_PREDICATE_NAME = re.compile(r'_*[a-z]\w*$')


class InvalidStatement(ValueError):
    pass


def validate_variable_name(name: str) -> None:
    if name == '_':
        return None
    if not PAT_VARIABLE_NAME.match(name):
        raise InvalidStatement(f'Invalid variable name: {name}')


def validate_predicate_name(name: str) -> None:
    if not PAT_PREDICATE_NAME.match(name):
        raise InvalidStatement(f'Invalid predicate name: {name}')


def validate_atom(atom: Atom) -> None:
    if any(not isinstance(a, (int, str, Variable)) for a in astuple(atom)):
        raise InvalidStatement(f'Invalid predicate arguments: {atom}')


def validate_rule(rule: Rule) -> None:
    # All variables in head are bound in body
    head_vars = get_atom_variables(rule.head)
    if BLANK in head_vars:
        raise InvalidStatement(f'BLANK variable "_" in rule head: {rule}')
    # body variables for positive atoms only
    body_vars = set().union(*(get_atom_variables(a) for a in rule.body if isinstance(a, Atom)))
    if head_vars.difference(body_vars):
        raise InvalidStatement(f'Unbound variable(s) in rule head: {rule}')
