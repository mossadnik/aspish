"""Validation of language inputs."""
import re
from .language import ASTVariable, Atom, Rule, Expression, BinaryOperator, OperatorName, BLANK
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
    if any(not isinstance(a, (int, str, ASTVariable)) for a in iter_atom_attributes(atom)):
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
    if ASTVariable(BLANK.name) in head_vars:
        raise InvalidStatement(f'BLANK variable "_" in rule head: {rule}')
    bound_vars = set().union(*(get_atom_variables(a) for a in iter_rule_atoms(rule, head=False, negative=False)))
    for expr in rule.body:
        if not isinstance(expr, BinaryOperator) or expr.operator != OperatorName.equal:
            continue
        if isinstance(expr.left, ASTVariable) and (expr.right in bound_vars or isinstance(expr.right, (int, str))):
            bound_vars.add(expr.left)
        if isinstance(expr.right, ASTVariable) and (expr.left in bound_vars or isinstance(expr.left, (int, str))):
            bound_vars.add(expr.right)

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


def validate_expression(expr: Expression | ASTVariable | str | int):
    if not isinstance(expr, Expression):
        return
    if any(isinstance(a, BinaryOperator) and a.operator in BOOLEAN_OPERATORS for a in expr.children):
        raise InvalidStatement(f'Boolean operators not at top level of expression: {expr}')
