"""Translation of Python language objects into clingo source code."""

from typing import Iterable
from functools import singledispatch
from clingo.symbol import Symbol, SymbolType
from .ast import (
    ASTBinaryOperation,
    ASTComparison,
    ASTVariable,
    ASTLiteral,
    ASTFunction,
    ASTInterval,
    ASTNot,
    ASTPool,
    ASTRule,
    ASTUnaryOperation,
)
from .language import Atom
from .validators import (
    get_predicate_signature,
    iter_atom_attributes
)
from . import utils as ut


@singledispatch
def translate(obj) -> str:
    raise NotImplementedError(f'Cannot translate object of type {type(obj)}')


@translate.register
def _(obj: ASTVariable) -> str:
    return obj.name


@translate.register
def _(obj: Atom) -> str:
    args = map(translate, iter_atom_attributes(obj))
    return f'{obj.__class__.__name__}({ut.csv(args)})'


STRING_ESCAPE = {
    ord(k): v
    for k, v in {
        '\t': '\\\\t',
        '"': '\\"',
        '\n': '\\n',
        '\\': '\\\\',
    }.items()
}


@translate.register
def _(obj: ASTLiteral) -> str:
    return translate(obj.value)

@translate.register
def _(obj: str) -> str:
    return f'"{obj.translate(STRING_ESCAPE)}"'


@translate.register
def _(obj: int) -> str:
    return str(obj)


@translate.register
def _(obj: ASTFunction) -> str:
    args = map(translate, obj.arguments)
    return f'{obj.name}({ut.csv(args)})'


@translate.register
def _(obj: ASTRule) -> str:
    if obj.head is not None:
        head = translate(obj.head) + ' '
    else:
        head = ''
    body = map(translate, obj.body)
    return f'{head}:- {ut.csv(body)}'


@translate.register
def _(obj: ASTNot) -> str:
    return f'not {translate(obj.arg)}'


@translate.register
def _(obj: ASTComparison | ASTBinaryOperation) -> str:
    left = translate(obj.left)
    right = translate(obj.right)
    return f'{left} {obj.name} {right}'


@translate.register
def _(obj: ASTPool) -> str:
    values = ";".join(map(translate, obj.values))
    return f'({values})'


@translate.register
def _(obj: ASTInterval) -> str:
    min_value = translate(obj.min_value)
    max_value = translate(obj.max_value)
    return f'{min_value}..{max_value}'


@translate.register
def _(obj: ASTUnaryOperation) -> str:
    arg = translate(obj.arg)
    if isinstance(obj.arg, ASTBinaryOperation):
        arg = f'({arg})'
    return f'{obj.operator}{arg}'


def show(obj: type[Atom]) -> str:
    name, arity = get_predicate_signature(obj)
    return f'#show {name}/{arity}'


def join_statements(statements: Iterable[str]) -> str:
    return '\n'.join(f'{s}.' for s in statements) + '\n'


class DeserializationError(ValueError):
    pass


def deserialize(value: Symbol, predicates: dict[tuple[str, int], type[Atom]]):
    value_type = value.type
    if value_type == SymbolType.Function:
        arguments = value.arguments
        try:
            pred = predicates[(value.name, len(arguments))]
        except KeyError:
            raise DeserializationError(f'Cannot deserialize predicate f{value.name}/{len(arguments)}')
        return pred(*[deserialize(arg, predicates) for arg in arguments])
    elif value_type == SymbolType.String:
        return value.string.replace('\\t', '\t')
    elif value_type == SymbolType.Number:
        return value.number
    else:
        raise DeserializationError(f'Cannot deserialize value {value}: Unknown type.')
