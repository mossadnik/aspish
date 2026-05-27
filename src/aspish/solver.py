from typing import Sequence, Optional, cast, Iterable
import itertools as it
import clingo
from clingo.symbol import SymbolType, Symbol
from .translation import translate, deserialize, show, join_statements
from .language import Atom, Rule, to_ast
from .validators import validate_fact, get_predicate_signature


class Solver:
    """Create and solve a logic program."""

    def __init__(self):
        self._ctl = clingo.Control()
        self._facts = []
        self._statements = []
        self._solved = False
        self._raw_model = None

    def add(self, *statements) -> 'Solver':
        """Add one or more rules or facts."""
        for s in statements:
            if isinstance(s, Rule):
                self._statements.append(to_ast(s))
            elif isinstance(s, Atom):
                validate_fact(s)
                self._facts.append(s)
        return self

    def solve(
            self,
            predicates: Optional[type[Atom] | Iterable[type[Atom]]] = None
    ) -> bool:
        """Try to solve the logic program.

        Args:
            predicates:
                Optional list of output predicates of interest. For performance only, useful
                if there are many intermediary results that need not be queried.

        Returns:
            A bool that indicates whether the program has been solved successfully.
        """
        self._ctl.add('base', [], join_statements(translate(s) for s in it.chain(self._facts, self._statements)))
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
        """Returns the raw output of the solver.

        Usually it is easier to use Solver.get instead.

        Raises:
            AttributeError:
                If there is not model available because either the program has not been solved
                or the program is unsatisfiable.
        """
        if self._raw_model is None:
            raise AttributeError('Need to call solve before getting model results.')
        return self._raw_model

    def get(self, predicate: type[Atom]) -> list[Atom]:
        """Get all instances of the specified type from the solver model.

        Raises:
          AttributeError:
            If there is not model available because either the program has not been solved
            or the program is unsatisfiable.
        """
        predicates = {get_predicate_signature(predicate): predicate}
        return [
            cast(Atom, deserialize(symbol, predicates))
            for symbol in self.raw_model
            if symbol.type == SymbolType.Function
            and (symbol.name, len(symbol.arguments)) in predicates
        ]
