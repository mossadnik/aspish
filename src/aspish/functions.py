from typing import Iterable
from attrs import make_class, field
from .language import (
    Variable,
    Atom,
    Rule,
    BLANK,
    Not,
    BodyAtom,
    Body,
    Expression,
    Choice
)
from .validators import validate_predicate_name, validate_variable_name


def var(name: str) -> Variable:
    validate_variable_name(name)
    return Variable(name)


class VariableFactory:
    def __init__(self):
        self.idx = 1
        self.prefix = 'X'

    def __call__(self, num: int) -> tuple[Variable, ...]:
        """Create num new variables with names X1, X2, ...

        The variable counter is stored so that subsequent calls will always
        produce new variable names.

        Note that the implementation is not thread-safe.
        """
        res = []
        for i in range(num):
            res.append(Variable(f'{self.prefix}{self.idx + i}'))
        self.idx += num
        return tuple(res)

    def reset(self) -> None:
        """Reset the variable counter to one."""
        self.idx = 1


vars = VariableFactory()


def predicate(name: str, attributes: Iterable[str] | None = None) -> type[Atom]:
    validate_predicate_name(name)
    if attributes is None:
        attributes = ()
    return make_class(
        name,
        {
            a: field(
                type=int | str | Expression | tuple[int | str | Expression, ...],
                default=BLANK,
            )
            for a in attributes
        },
        bases=(Atom,),
        frozen=True,
        slots=True,
        order=False
    )


def not_(arg: Atom) -> Not:
    return Not(arg)


def constraint(*body: BodyAtom) -> Rule:
    """A constraint is a rule that must not hold."""
    return Rule(head=None, body=body)


def choose(head: Atom, body: Body, at_least: int = 0, at_most: int | None = None) -> Choice:
    if not isinstance(body, tuple):
        body = (body,)
    return Choice(head, body, at_least, at_most)
