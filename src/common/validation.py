"""Composable validation rules raising :class:`ValidationError` on failure."""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

from common.codes import ErrorCode
from common.errors import ValidationError

V = TypeVar(chr(86))


class Rule(Generic[V]):
    """Single validation predicate bound to an error code and a field code."""

    def __init__(self, predicate: Callable[[V], bool], code: int, field: int) -> None:
        """Create the rule.

        Args:
            predicate: Callable returning ``True`` when the value is accepted.
            code: Numeric :class:`~common.codes.ErrorCode` value reported on
                failure.
            field: Numeric :class:`~common.codes.FieldCode` value reported on
                failure.
        """
        self._predicate = predicate
        self._code = code
        self._field = field

    def check(self, value: V) -> None:
        """Apply the predicate to a value.

        Args:
            value: Value to check.

        Raises:
            ValidationError: With the configured code and field when the
                predicate returns a falsy value.
        """
        if not self._predicate(value):
            raise ValidationError(self._code, self._field)


class Validator(Generic[V]):
    """Ordered collection of rules applied to the same value."""

    def __init__(self) -> None:
        """Create a validator holding no rule."""
        self._rules: list[Rule[V]] = []

    def add(self, rule: Rule[V]) -> "Validator[V]":
        """Append a rule to the chain.

        Args:
            rule: Rule evaluated after the ones already registered.

        Returns:
            The validator itself, so calls can be chained.
        """
        self._rules.append(rule)
        return self

    def validate(self, value: V) -> V:
        """Run every rule, in registration order.

        Args:
            value: Value to validate.

        Returns:
            The value unchanged when all rules pass.

        Raises:
            ValidationError: Raised by the first rule that rejects the value.
        """
        for rule in self._rules:
            rule.check(value)
        return value


def positive(field: int) -> Rule[int]:
    """Build a rule accepting only strictly positive integers.

    Args:
        field: Numeric field code reported on failure.

    Returns:
        A rule failing with code ``INVALID_AMOUNT``.
    """
    return Rule(lambda value: value > 0, ErrorCode.INVALID_AMOUNT.value, field)


def non_negative(field: int) -> Rule[int]:
    """Build a rule accepting zero and positive integers.

    Args:
        field: Numeric field code reported on failure.

    Returns:
        A rule failing with code ``INVALID_AMOUNT``.
    """
    return Rule(lambda value: value >= 0, ErrorCode.INVALID_AMOUNT.value, field)


def bounded(low: int, high: int, field: int) -> Rule[int]:
    """Build a rule accepting integers inside an inclusive range.

    Args:
        low: Smallest accepted value.
        high: Largest accepted value.
        field: Numeric field code reported on failure.

    Returns:
        A rule failing with code ``LIMIT_EXCEEDED``.
    """
    return Rule(lambda value: low <= value <= high, ErrorCode.LIMIT_EXCEEDED.value, field)
