"""Currency-safe monetary amounts expressed in minor units."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from common.codes import ErrorCode, FieldCode
from common.errors import ValidationError


class Currency(IntEnum):
    """Supported currencies, valued with their ISO 4217 numeric code."""

    EUR = 978
    USD = 840
    GBP = 826


@dataclass(frozen=True)
class Money:
    """Immutable amount of money in a single currency.

    Amounts are stored as integer minor units (cents for ``EUR``), so no
    rounding error can creep in.

    Attributes:
        minor_units: Signed amount in minor units.
        currency: Currency of the amount.
    """

    minor_units: int
    currency: Currency

    def __post_init__(self) -> None:
        """Reject non-integer amounts.

        Raises:
            ValidationError: With code ``INVALID_AMOUNT`` and field ``AMOUNT``
                when ``minor_units`` is not an :class:`int`.
        """
        if not isinstance(self.minor_units, int):
            raise ValidationError(ErrorCode.INVALID_AMOUNT.value, FieldCode.AMOUNT.value)

    def add(self, other: "Money") -> "Money":
        """Add another amount of the same currency.

        Args:
            other: Amount to add.

        Returns:
            A new :class:`Money` holding the sum.

        Raises:
            ValidationError: With code ``INVALID_AMOUNT`` and field
                ``CURRENCY`` when the currencies differ.
        """
        self._same_currency(other)
        return Money(self.minor_units + other.minor_units, self.currency)

    def subtract(self, other: "Money") -> "Money":
        """Subtract another amount of the same currency.

        The result may be negative; no check is performed here.

        Args:
            other: Amount to subtract.

        Returns:
            A new :class:`Money` holding the difference.

        Raises:
            ValidationError: With code ``INVALID_AMOUNT`` and field
                ``CURRENCY`` when the currencies differ.
        """
        self._same_currency(other)
        return Money(self.minor_units - other.minor_units, self.currency)

    def scale(self, factor: int) -> "Money":
        """Multiply the amount by an integer factor.

        Args:
            factor: Multiplier applied to the minor units.

        Returns:
            A new :class:`Money` in the same currency.
        """
        return Money(self.minor_units * factor, self.currency)

    def is_negative(self) -> bool:
        """Tell whether the amount is strictly below zero.

        Returns:
            ``True`` when the minor units are negative.
        """
        return self.minor_units < 0

    def is_zero(self) -> bool:
        """Tell whether the amount is exactly zero.

        Returns:
            ``True`` when the minor units are zero.
        """
        return self.minor_units == 0

    def _same_currency(self, other: "Money") -> None:
        """Ensure another amount shares this amount's currency.

        Args:
            other: Amount to compare with.

        Raises:
            ValidationError: With code ``INVALID_AMOUNT`` and field
                ``CURRENCY`` when the currencies differ.
        """
        if self.currency is not other.currency:
            raise ValidationError(ErrorCode.INVALID_AMOUNT.value, FieldCode.CURRENCY.value)


def zero(currency: Currency) -> Money:
    """Build the neutral amount of a currency.

    Args:
        currency: Currency of the amount.

    Returns:
        A :class:`Money` of zero minor units in ``currency``.
    """
    return Money(0, currency)
