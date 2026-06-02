from enum import StrEnum


class ComparisonOperator(StrEnum):
    equal = '='
    not_equal = '!='
    less_than = '<'
    less_than_or_equal = '<='
    greater_than = '>'
    greater_than_or_equal = '>='


class BinaryOperator(StrEnum):
    plus = '+'
    minus = '-'


class UnaryOperator(StrEnum):
    minus = '-'
