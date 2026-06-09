import pytest
from aspish.functions import VariableSequence
from aspish.validators import InvalidStatement


class Test_VariableSequence:
    """vars is not thread-safe, create a new instance for each test."""
    def test_subsequent_calls_return_new_variables(self):
        vars = VariableSequence()
        res = []
        res.extend(vars(2))
        res.extend(vars(2))
        assert len({x.name for x in res}) == len(res)

    def test_reset_resets_sequence_counter(self):
        vars = VariableSequence()
        x1 = vars(1)[0]
        vars.reset()
        x2 = vars(1)[0]
        assert x1.name == x2.name

    def test_variable_names_start_with_prefix(self):
        vars = VariableSequence('Abc')
        x1, x2 = vars(2)
        assert x1.name.startswith('Abc')
        assert x2.name.startswith('Abc')

    def test_raised_if_invalid_prefix(self):
        with pytest.raises(InvalidStatement):
            VariableSequence('x')
