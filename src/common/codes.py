"""Numeric codes used to describe errors and the fields they relate to."""

from __future__ import annotations

from enum import IntEnum


class ErrorCode(IntEnum):
    """Stable numeric identifier of an error condition.

    Codes are grouped by range: ``1xxx`` for domain and validation problems,
    ``2xxx`` for infrastructure problems and ``3xxx`` for configuration
    problems.
    """

    UNKNOWN = 1000
    INVALID_AMOUNT = 1001
    INVALID_KIND = 1002
    INVALID_ACCOUNT = 1003
    NEGATIVE_BALANCE = 1004
    LIMIT_EXCEEDED = 1005
    NOT_FOUND = 1006
    DUPLICATE = 1007
    TIMEOUT = 2001
    UNAVAILABLE = 2002
    THROTTLED = 2003
    MISSING_CONFIG = 3001
    BAD_CONFIG = 3002


class FieldCode(IntEnum):
    """Identifier of the value a validation error points at."""

    AMOUNT = 1
    KIND = 2
    ACCOUNT = 3
    CURRENCY = 4
    REFERENCE = 5


def is_retryable(code: int) -> bool:
    """Tell whether an operation that failed with this code may be retried.

    Args:
        code: Numeric error code, normally the value of an :class:`ErrorCode`.

    Returns:
        ``True`` for the transient infrastructure codes ``TIMEOUT``,
        ``UNAVAILABLE`` and ``THROTTLED``, ``False`` for every other code.
    """
    return code in (
        ErrorCode.TIMEOUT.value,
        ErrorCode.UNAVAILABLE.value,
        ErrorCode.THROTTLED.value,
    )
