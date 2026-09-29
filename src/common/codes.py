from __future__ import annotations

from enum import IntEnum


class ErrorCode(IntEnum):
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
    PARSE_ERROR = 4001
    RENDER_ERROR = 4002
    GENERATION_ERROR = 4003


class FieldCode(IntEnum):
    AMOUNT = 1
    KIND = 2
    ACCOUNT = 3
    CURRENCY = 4
    REFERENCE = 5


def is_retryable(code: int) -> bool:
    return code in (
        ErrorCode.TIMEOUT.value,
        ErrorCode.UNAVAILABLE.value,
        ErrorCode.THROTTLED.value,
    )
