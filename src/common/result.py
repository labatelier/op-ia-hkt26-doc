from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

from common.enums import Outcome

T = TypeVar(chr(84))
U = TypeVar(chr(85))
E = TypeVar(chr(69))


@dataclass(frozen=True)
class Result(Generic[T, E]):
    outcome: Outcome
    value: Optional[T] = None
    error: Optional[E] = None

    def is_ok(self) -> bool:
        return self.outcome is Outcome.SUCCESS

    def is_err(self) -> bool:
        return self.outcome is Outcome.FAILURE

    def map(self, fn: Callable[[T], U]) -> "Result[U, E]":
        if self.is_ok():
            return ok(fn(self.value))
        return err(self.error)

    def bind(self, fn: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        if self.is_ok():
            return fn(self.value)
        return err(self.error)

    def unwrap(self) -> T:
        if self.is_ok():
            return self.value
        raise self.error

    def unwrap_or(self, fallback: T) -> T:
        if self.is_ok():
            return self.value
        return fallback


def ok(value: T) -> Result[T, E]:
    return Result(outcome=Outcome.SUCCESS, value=value, error=None)


def err(error: E) -> Result[T, E]:
    return Result(outcome=Outcome.FAILURE, value=None, error=error)
