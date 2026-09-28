"""A small success/failure container used instead of raising across layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

from common.enums import Outcome

T = TypeVar(chr(84))
U = TypeVar(chr(85))
E = TypeVar(chr(69))


@dataclass(frozen=True)
class Result(Generic[T, E]):
    """Outcome of an operation: either a value or an error.

    Build instances through :func:`ok` and :func:`err` rather than calling the
    constructor directly.

    Attributes:
        outcome: Discriminant telling which side is populated.
        value: Payload of a successful result, ``None`` otherwise.
        error: Payload of a failed result, ``None`` otherwise.
    """

    outcome: Outcome
    value: Optional[T] = None
    error: Optional[E] = None

    def is_ok(self) -> bool:
        """Tell whether the result holds a value.

        Returns:
            ``True`` when the outcome is ``SUCCESS``.
        """
        return self.outcome is Outcome.SUCCESS

    def is_err(self) -> bool:
        """Tell whether the result holds an error.

        Returns:
            ``True`` when the outcome is ``FAILURE``.
        """
        return self.outcome is Outcome.FAILURE

    def map(self, fn: Callable[[T], U]) -> "Result[U, E]":
        """Transform the value of a successful result.

        Args:
            fn: Function applied to the value. It is not called on a failure.

        Returns:
            A successful result holding ``fn(value)``, or the original error
            unchanged.
        """
        if self.is_ok():
            return ok(fn(self.value))
        return err(self.error)

    def bind(self, fn: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """Chain another result-returning operation.

        Args:
            fn: Function applied to the value, itself returning a
                :class:`Result`. It is not called on a failure.

        Returns:
            The result returned by ``fn``, or the original error unchanged.
        """
        if self.is_ok():
            return fn(self.value)
        return err(self.error)

    def unwrap(self) -> T:
        """Return the value, or raise the stored error.

        Returns:
            The value of a successful result.

        Raises:
            BaseException: The stored error itself when the result is a
                failure; a :class:`TypeError` is raised instead if that error
                is not an exception.
        """
        if self.is_ok():
            return self.value
        raise self.error

    def unwrap_or(self, fallback: T) -> T:
        """Return the value, or a default when the result is a failure.

        Args:
            fallback: Value returned for a failed result.

        Returns:
            The value of a successful result, ``fallback`` otherwise.
        """
        if self.is_ok():
            return self.value
        return fallback


def ok(value: T) -> Result[T, E]:
    """Build a successful result.

    Args:
        value: Payload of the result.

    Returns:
        A :class:`Result` whose outcome is ``SUCCESS``.
    """
    return Result(outcome=Outcome.SUCCESS, value=value, error=None)


def err(error: E) -> Result[T, E]:
    """Build a failed result.

    Args:
        error: Error payload, usually a
            :class:`~common.errors.DomainError`.

    Returns:
        A :class:`Result` whose outcome is ``FAILURE``.
    """
    return Result(outcome=Outcome.FAILURE, value=None, error=error)
