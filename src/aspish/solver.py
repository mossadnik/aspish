from typing import Sequence, Optional, cast
import clingo
from clingo.symbol import SymbolType, Symbol
from .translation import translate, deserialize, show, join_statements
from .language import Atom, Rule, get_predicate_signature
from .validators import validate_rule, validate_fact


class Solver:
    """Create and solve a logic program."""
    def __init__(self):
        self._ctl = clingo.Control()
        self._statements = []
        self._solved = False
        self._raw_model = None

    def add(self, *statements) -> 'Solver':
        for s in statements:
            if isinstance(s, Rule):
                validate_rule(s)
            elif isinstance(s, Atom):
                validate_fact(s)
        self._statements.extend(statements)
        return self

    def solve(
            self,
            predicates: Optional[type[Atom] | Sequence[type[Atom]]] = None
    ) -> bool:
        self._ctl.add('base', [], join_statements(translate(s) for s in self._statements))
        filter_predicates = predicates is not None
        if filter_predicates:
            if isinstance(predicates, type):
                predicates = [predicates]
            self._ctl.add('base', [], join_statements(show(p) for p in predicates))
        self._ctl.ground()
        with self._ctl.solve(yield_=True) as handle:
            model = handle.model()
            if not model:
                return False
            self._raw_model = model.symbols(atoms=not filter_predicates, shown=filter_predicates)
            return True

    @property
    def raw_model(self) -> Sequence[Symbol]:
        if self._raw_model is None:
            raise AttributeError('Need to call solve before getting model results.')
        return self._raw_model

    def get(self, predicate: type[Atom]) -> list[Atom]:
        predicates = {get_predicate_signature(predicate): predicate}
        return [
            cast(Atom, deserialize(symbol, predicates))
            for symbol in self.raw_model
            if symbol.type == SymbolType.Function
            and (symbol.name, len(symbol.arguments)) in predicates
        ]
