"""Typed identifiers for accounts and transactions, and their generator."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Iterator

from common.codes import ErrorCode, FieldCode
from common.errors import ValidationError


@dataclass(frozen=True)
class AccountId:
    """Identifier of an account.

    Attributes:
        value: Strictly positive integer identifying the account.
    """

    value: int

    def __post_init__(self) -> None:
        """Reject non-positive identifiers.

        Raises:
            ValidationError: With code ``INVALID_ACCOUNT`` and field
                ``ACCOUNT`` when ``value`` is zero or negative.
        """
        if self.value <= 0:
            raise ValidationError(ErrorCode.INVALID_ACCOUNT.value, FieldCode.ACCOUNT.value)


@dataclass(frozen=True)
class TransactionId:
    """Identifier of a transaction.

    Attributes:
        value: Strictly positive integer identifying the transaction.
    """

    value: int

    def __post_init__(self) -> None:
        """Reject non-positive identifiers.

        Raises:
            ValidationError: With code ``INVALID_ACCOUNT`` and field
                ``REFERENCE`` when ``value`` is zero or negative.
        """
        if self.value <= 0:
            raise ValidationError(ErrorCode.INVALID_ACCOUNT.value, FieldCode.REFERENCE.value)


class Sequence:
    """Monotonic source of account and transaction identifiers.

    Both factory methods draw from the same counter, so an identifier value is
    never handed out twice by the same instance.
    """

    def __init__(self, start: int) -> None:
        """Create the sequence.

        Args:
            start: First value the counter yields.
        """
        self._counter: Iterator[int] = count(start)

    def next_account(self) -> AccountId:
        """Draw the next account identifier.

        Returns:
            A fresh :class:`AccountId`.

        Raises:
            ValidationError: When the counter yields a non-positive value, for
                instance because ``start`` was zero or negative.
        """
        return AccountId(next(self._counter))

    def next_transaction(self) -> TransactionId:
        """Draw the next transaction identifier.

        Returns:
            A fresh :class:`TransactionId`.

        Raises:
            ValidationError: When the counter yields a non-positive value, for
                instance because ``start`` was zero or negative.
        """
        return TransactionId(next(self._counter))
