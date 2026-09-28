from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from common.codes import ErrorCode, FieldCode
from common.errors import ValidationError


class Currency(IntEnum):
    EUR = 978
    USD = 840
    GBP = 826


@dataclass(frozen=True)
class Money:
    minor_units: int
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.minor_units, int):
            raise ValidationError(ErrorCode.INVALID_AMOUNT.value, FieldCode.AMOUNT.value)

    def add(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.minor_units + other.minor_units, self.currency)

    def subtract(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.minor_units - other.minor_units, self.currency)

    def scale(self, factor: int) -> "Money":
        return Money(self.minor_units * factor, self.currency)

    def is_negative(self) -> bool:
        return self.minor_units < 0

    def is_zero(self) -> bool:
        return self.minor_units == 0

    def _same_currency(self, other: "Money") -> None:
        if self.currency is not other.currency:
            raise ValidationError(ErrorCode.INVALID_AMOUNT.value, FieldCode.CURRENCY.value)


def zero(currency: Currency) -> Money:
    return Money(0, currency)
