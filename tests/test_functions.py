from aspish.functions import VariableSequence


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
