"""Domain model of the non-production environment: accounts and their state."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List

from common.codes import ErrorCode, FieldCode
from common.enums import Status
from common.errors import DomainError
from common.identifiers import AccountId, TransactionId
from common.money import Currency, Money, zero


@dataclass(frozen=True)
class AccountState:
    """Immutable snapshot of an account at one point of its history.

    Attributes:
        balance: Current balance of the account.
        version: Number of mutations applied so far, incremented on every
            credit, debit and close.
        open: Whether the account still accepts movements.
    """

    balance: Money
    version: int
    open: bool


@dataclass
class Account:
    """Mutable account aggregate guarding balance and currency invariants.

    Attributes:
        account_id: Identifier of the account.
        currency: Only currency the account accepts.
        state: Current state. When left unset, an open account with a zero
            balance and version ``0`` is created.
        history: Identifiers of the transactions applied, in order.
    """

    account_id: AccountId
    currency: Currency
    state: AccountState = field(default=None)
    history: List[TransactionId] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialise the state when the caller did not provide one."""
        if self.state is None:
            self.state = AccountState(balance=zero(self.currency), version=0, open=True)

    def balance(self) -> Money:
        """Return the current balance.

        Returns:
            The balance held in the current state.
        """
        return self.state.balance

    def is_open(self) -> bool:
        """Tell whether the account still accepts movements.

        Returns:
            ``True`` while the account is open.
        """
        return self.state.open

    def credit(self, amount: Money, reference: TransactionId) -> None:
        """Add an amount to the balance and record the transaction.

        Args:
            amount: Amount to credit, in the account currency.
            reference: Identifier of the transaction being applied.

        Raises:
            DomainError: With code ``INVALID_ACCOUNT`` when the account is
                closed, or ``INVALID_AMOUNT`` when the currency does not match.
        """
        self._guard_open()
        self._guard_currency(amount)
        self._apply(self.state.balance.add(amount), reference)

    def debit(self, amount: Money, reference: TransactionId) -> None:
        """Remove an amount from the balance and record the transaction.

        Args:
            amount: Amount to debit, in the account currency.
            reference: Identifier of the transaction being applied.

        Raises:
            DomainError: With code ``INVALID_ACCOUNT`` when the account is
                closed, ``INVALID_AMOUNT`` when the currency does not match, or
                ``NEGATIVE_BALANCE`` when the debit would overdraw the account.
        """
        self._guard_open()
        self._guard_currency(amount)
        projected = self.state.balance.subtract(amount)
        if projected.is_negative():
            raise DomainError(ErrorCode.NEGATIVE_BALANCE.value)
        self._apply(projected, reference)

    def close(self) -> None:
        """Close the account and bump its version.

        Raises:
            DomainError: With code ``NEGATIVE_BALANCE`` when the balance is not
                zero.
        """
        if not self.state.balance.is_zero():
            raise DomainError(ErrorCode.NEGATIVE_BALANCE.value)
        self.state = replace(self.state, open=False, version=self.state.version + 1)

    def _apply(self, new_balance: Money, reference: TransactionId) -> None:
        """Replace the state with a new balance and append the reference.

        Args:
            new_balance: Balance of the resulting state.
            reference: Identifier appended to :attr:`history`.
        """
        self.state = replace(
            self.state,
            balance=new_balance,
            version=self.state.version + 1,
        )
        self.history.append(reference)

    def _guard_open(self) -> None:
        """Ensure the account is still open.

        Raises:
            DomainError: With code ``INVALID_ACCOUNT`` when it is closed.
        """
        if not self.state.open:
            raise DomainError(ErrorCode.INVALID_ACCOUNT.value)

    def _guard_currency(self, amount: Money) -> None:
        """Ensure an amount uses the account currency.

        Args:
            amount: Amount to check.

        Raises:
            DomainError: With code ``INVALID_AMOUNT`` when the currencies
                differ.
        """
        if amount.currency is not self.currency:
            raise DomainError(ErrorCode.INVALID_AMOUNT.value)

    def snapshot(self) -> AccountState:
        """Return the current state.

        Returns:
            The current :class:`AccountState`, which is immutable and therefore
            safe to hand out.
        """
        return self.state

    def transaction_count(self) -> int:
        """Return how many transactions were applied to the account.

        Returns:
            The length of :attr:`history`.
        """
        return len(self.history)
