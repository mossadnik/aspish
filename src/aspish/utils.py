from typing import Iterable


def csv(values: Iterable[str]) -> str:
    return ', '.join(values)
