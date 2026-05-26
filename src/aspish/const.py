from enum import StrEnum


class OperatorName(StrEnum):
    equal = '='
    not_equal = '!='
    less_than = '<'
    less_than_or_equal = '<='
    greater_than = '>'
    greater_than_or_equal = '>='
