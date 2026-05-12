from typing import Sequence, Optional
import clingo
from clingo.symbol import SymbolType, Symbol
from .translation import translate, deserialize, show, join_statements
from .language import Predicate, Atom


class Solver:
    """Create and solve a logic program.d"""
    def __init__(self):
        self._ctl = clingo.Control()
        self._statements = []
        self._solved = False
        self._raw_model = None

    def add(self, *statements) -> 'Solver':
        self._statements.extend(statements)
        return self

    def solve(
            self,
            predicates: Optional[Predicate | Sequence[Predicate]] = None
    ) -> bool:
        self._ctl.add('base', [], join_statements(translate(s) for s in self._statements))
        filter_predicates = predicates is not None
        if filter_predicates:
            if isinstance(predicates, Predicate):
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

    def get(self, predicate: Predicate):
        predicates = {(predicate.name, predicate.arity): predicate}
        res = (
            deserialize(symbol, predicates)
            for symbol in self.raw_model
            if symbol.type == SymbolType.Function
            and (symbol.name, len(symbol.arguments)) in predicates
        )
        attribute_names = predicate.attributes
        return [
            dict(zip(attribute_names, atom.attributes))
            for atom in res
            if isinstance(atom, Atom)
        ]
