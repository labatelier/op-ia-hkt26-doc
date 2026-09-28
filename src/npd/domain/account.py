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
    balance: Money
    version: int
    open: bool


@dataclass
class Account:
    account_id: AccountId
    currency: Currency
    state: AccountState = field(default=None)
    history: List[TransactionId] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.state is None:
            self.state = AccountState(balance=zero(self.currency), version=0, open=True)

    def balance(self) -> Money:
        return self.state.balance

    def is_open(self) -> bool:
        return self.state.open

    def credit(self, amount: Money, reference: TransactionId) -> None:
        self._guard_open()
        self._guard_currency(amount)
        self._apply(self.state.balance.add(amount), reference)

    def debit(self, amount: Money, reference: TransactionId) -> None:
        self._guard_open()
        self._guard_currency(amount)
        projected = self.state.balance.subtract(amount)
        if projected.is_negative():
            raise DomainError(ErrorCode.NEGATIVE_BALANCE.value)
        self._apply(projected, reference)

    def close(self) -> None:
        if not self.state.balance.is_zero():
            raise DomainError(ErrorCode.NEGATIVE_BALANCE.value)
        self.state = replace(self.state, open=False, version=self.state.version + 1)

    def _apply(self, new_balance: Money, reference: TransactionId) -> None:
        self.state = replace(
            self.state,
            balance=new_balance,
            version=self.state.version + 1,
        )
        self.history.append(reference)

    def _guard_open(self) -> None:
        if not self.state.open:
            raise DomainError(ErrorCode.INVALID_ACCOUNT.value)

    def _guard_currency(self, amount: Money) -> None:
        if amount.currency is not self.currency:
            raise DomainError(ErrorCode.INVALID_AMOUNT.value)

    def snapshot(self) -> AccountState:
        return self.state

    def transaction_count(self) -> int:
        return len(self.history)
