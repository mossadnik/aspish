"""Validation of language inputs."""

from typing import Generator
import re
from functools import singledispatch
from attrs import fields
from .language import (
    Atom,
    Not,
    Rule,
    Variable,
    Expression,
    BinaryOperator,
    OperatorName,
    BLANK,
)
from . import ast


def get_predicate_signature(atom: type[Atom]):
    return (atom.__name__, len(fields(atom)))


def iter_atom_attributes(atom: Atom):
    for f in fields(atom):
        yield getattr(atom, f.name)

def get_atom_variables(atom: Atom) -> set[str]:
    res = set()
    for a in iter_atom_attributes(atom):
        if isinstance(a, Atom):
            res.update(get_atom_variables(a))
        elif isinstance(a, Variable):
            res.add(a.name)
    return res


def iter_rule_atoms(rule: Rule, head: bool = True, negative: bool = True) -> Generator[Atom, None, None]:
    if head:
        yield rule.head
    for obj in rule.body:
        if isinstance(obj, Atom):
            yield obj
        elif negative and isinstance(obj, Not):
            yield obj.arg


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
        for expr in rule.body:
            if isinstance(expr, Expression):
                validate_expression(expr)
    except InvalidStatement as e:
        raise InvalidStatement(f'Rule contains invalid atom or expression: {rule}\n{e}')
    # All variables in head are bound in body
    head_vars = get_atom_variables(rule.head)
    if BLANK.name in head_vars:
        raise InvalidStatement(f'BLANK variable "_" in rule head: {rule}')
    bound_vars = set().union(*(get_atom_variables(a) for a in iter_rule_atoms(rule, head=False, negative=False)))
    for expr in rule.body:
        if not isinstance(expr, BinaryOperator) or expr.operator != OperatorName.equal:
            continue
        left_bound = not isinstance(expr.left, Variable) or expr.left.name in bound_vars
        right_bound = not isinstance(expr.right, Variable) or expr.right.name in bound_vars
        if isinstance(expr.left, Variable) and right_bound:
            bound_vars.add(expr.left.name)
        if isinstance(expr.right, Variable) and left_bound:
            bound_vars.add(expr.right.name)

    if head_vars.difference(bound_vars):
        raise InvalidStatement(f'Unbound variable(s) in rule head: {rule}')


BOOLEAN_OPERATORS = {
    OperatorName.equal,
    OperatorName.not_equal,
    OperatorName.less_than,
    OperatorName.less_than_or_equal,
    OperatorName.greater_than,
    OperatorName.greater_than_or_equal
}


def validate_expression(expr: Expression | Variable | str | int):
    if not isinstance(expr, Expression):
        return
    if any(isinstance(a, BinaryOperator) and a.operator in BOOLEAN_OPERATORS for a in expr.children):
        raise InvalidStatement(f'Boolean operators not at top level of expression: {expr}')
