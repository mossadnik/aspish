import clingo
from clingo.symbol import SymbolType
from .translation import translate, deserialize
from .language import Function, Atom


class Solver:
    """Create and solve a logic program.d"""
    def __init__(self):
        self._ctl = clingo.Control()
        self._statements = []
        self._solved = False

    def add(self, statement) -> 'Solver':
        self._solved = False
        self._statements.append(statement)
        return self

    def solve(self) -> bool:
        self._ctl.add('base', [], '\n'.join([translate(s) + '.' for s in self._statements]))
        self._ctl.ground()
        with self._ctl.solve(yield_=True) as handle:
            model = handle.model()
            if not model:
                return False
            self._answer = model.symbols(atoms=True)
            self._solved = True
            return True

    def get(self, func: Function):
        if not self._solved:
            raise AttributeError('Need to call solve before getting model results.')
        functions = {(func.name, func.arity): func}
        res = (
            deserialize(symbol, functions)
            for symbol in self._answer
            if symbol.type == SymbolType.Function
            and symbol.name == func.name
            and len(symbol.arguments) == func.arity
        )
        return [
            dict(zip(func.attributes, atom.attributes))
            for atom in res
            if isinstance(atom, Atom)
        ]
