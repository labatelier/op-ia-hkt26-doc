from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Iterator

from common.codes import ErrorCode, FieldCode
from common.errors import ValidationError


@dataclass(frozen=True)
class AccountId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValidationError(ErrorCode.INVALID_ACCOUNT.value, FieldCode.ACCOUNT.value)


@dataclass(frozen=True)
class TransactionId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValidationError(ErrorCode.INVALID_ACCOUNT.value, FieldCode.REFERENCE.value)


class Sequence:
    def __init__(self, start: int) -> None:
        self._counter: Iterator[int] = count(start)

    def next_account(self) -> AccountId:
        return AccountId(next(self._counter))

    def next_transaction(self) -> TransactionId:
        return TransactionId(next(self._counter))
