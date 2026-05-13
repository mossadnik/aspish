from typing import Iterable
from dataclasses import make_dataclass, field
from .language import Variable, Atom, BLANK, Not
from .validators import validate_predicate_name, validate_variable_name


def var(name: str) -> Variable:
    validate_variable_name(name)
    return Variable(name)


def predicate(name: str, attributes: Iterable[str]) -> type[Atom]:
    validate_predicate_name(name)
    return make_dataclass(
        name,
        [
            (a, int | str | Variable, field(default=BLANK))
            for a in attributes
        ],
        bases=(Atom,),
        frozen=True,
        slots=True
    )


def not_(arg: Atom):
    return Not(arg)
