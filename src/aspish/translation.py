"""Translation of Python language objects into clingo source code."""

from functools import singledispatch
from clingo.symbol import Symbol, SymbolType
from .language import Variable, Atom, Rule, Not, Function
from . import utils as ut


@singledispatch
def translate(obj) -> str:
    raise NotImplementedError(f'Cannot translate object of type {type(obj)}')


@translate.register
def _(obj: Variable) -> str:
    return obj.name


@translate.register
def _(obj: Atom) -> str:
    args = map(translate, obj.attributes)
    return f'{obj.function_.name}({ut.csv(args)})'


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


class DeserializationError(ValueError):
    pass


def deserialize(value: Symbol, functions: dict[tuple[str, int], Function]):
    if value.type == SymbolType.Function:
        try:
            func = functions[(value.name, len(value.arguments))]
        except KeyError:
            raise DeserializationError(f'Cannot deserialize function f{value.name}/{len(value.arguments)}')
        return func(*[deserialize(arg, functions) for arg in value.arguments])
    elif value.type == SymbolType.Number:
        return value.number
    elif value.type == SymbolType.String:
        return value.string.replace('\\t', '\t')
    else:
        raise DeserializationError(f'Cannot deserialize value {value}: Unknown type.')
