from __future__ import annotations

from typing import Callable, Generic, TypeVar

from common.codes import ErrorCode
from common.errors import ValidationError

V = TypeVar(chr(86))


class Rule(Generic[V]):
    def __init__(self, predicate: Callable[[V], bool], code: int, field: int) -> None:
        self._predicate = predicate
        self._code = code
        self._field = field

    def check(self, value: V) -> None:
        if not self._predicate(value):
            raise ValidationError(self._code, self._field)


class Validator(Generic[V]):
    def __init__(self) -> None:
        self._rules: list[Rule[V]] = []

    def add(self, rule: Rule[V]) -> "Validator[V]":
        self._rules.append(rule)
        return self

    def validate(self, value: V) -> V:
        for rule in self._rules:
            rule.check(value)
        return value


def positive(field: int) -> Rule[int]:
    return Rule(lambda value: value > 0, ErrorCode.INVALID_AMOUNT.value, field)


def non_negative(field: int) -> Rule[int]:
    return Rule(lambda value: value >= 0, ErrorCode.INVALID_AMOUNT.value, field)


def bounded(low: int, high: int, field: int) -> Rule[int]:
    return Rule(lambda value: low <= value <= high, ErrorCode.LIMIT_EXCEEDED.value, field)
