"""Validation of language inputs."""
import re
from .language import Variable, Atom, Rule, BLANK
from .language import (
    get_atom_variables,
    iter_atom_attributes,
    iter_rule_atoms
)


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
    if any(not isinstance(a, (int, str, Variable)) for a in iter_atom_attributes(atom)):
        raise InvalidStatement(f'Invalid predicate arguments: {atom}')


def validate_fact(atom: Atom) -> None:
    if any(not isinstance(a, (int, str)) for a in iter_atom_attributes(atom)):
        raise InvalidStatement(f'Invalid argument for fact: {atom}')


def validate_rule(rule: Rule) -> None:
    # validate atoms
    try:
        for a in iter_rule_atoms(rule):
            validate_atom(a)
    except InvalidStatement as e:
        raise InvalidStatement(f'Rule contains invalid atom: {rule}\n{e}')
    # All variables in head are bound in body
    head_vars = get_atom_variables(rule.head)
    if BLANK in head_vars:
        raise InvalidStatement(f'BLANK variable "_" in rule head: {rule}')
    body_vars = set().union(*(get_atom_variables(a) for a in iter_rule_atoms(rule, head=False, negative=False)))
    if head_vars.difference(body_vars):
        raise InvalidStatement(f'Unbound variable(s) in rule head: {rule}')
