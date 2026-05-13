"""Translation of Python language objects into clingo source code."""

from typing import Iterable
from functools import singledispatch
from clingo.symbol import Symbol, SymbolType
from .language import Variable, Atom, Rule, Not, get_predicate_signature, iter_atom_attributes
from . import utils as ut


@singledispatch
def translate(obj) -> str:
    raise NotImplementedError(f'Cannot translate object of type {type(obj)}')


@translate.register
def _(obj: Variable) -> str:
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
def _(obj: str) -> str:
    return f'"{obj.translate(STRING_ESCAPE)}"'


@translate.register
def _(obj: int) -> str:
    return str(obj)


@translate.register
def _(obj: Rule) -> str:
    head = translate(obj.head)
    body = map(translate, obj.body)
    return f'{head} :- {ut.csv(body)}'


@translate.register
def _(obj: Not) -> str:
    return f'not {translate(obj.arg)}'


def show(obj: type[Atom]) -> str:
    name, arity = get_predicate_signature(obj)
    return f'#show {name}/{arity}'


def join_statements(statements: Iterable[str]) -> str:
    return '\n'.join(f'{s}.' for s in statements) + '\n'


class DeserializationError(ValueError):
    pass


def deserialize(value: Symbol, predicates: dict[tuple[str, int], type[Atom]]):
    if value.type == SymbolType.Function:
        try:
            pred = predicates[(value.name, len(value.arguments))]
        except KeyError:
            raise DeserializationError(f'Cannot deserialize predicate f{value.name}/{len(value.arguments)}')
        return pred(*[deserialize(arg, predicates) for arg in value.arguments])
    elif value.type == SymbolType.String:
        return value.string.replace('\\t', '\t')
    elif value.type == SymbolType.Number:
        return value.number
    else:
        raise DeserializationError(f'Cannot deserialize value {value}: Unknown type.')
