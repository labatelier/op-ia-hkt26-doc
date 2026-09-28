from __future__ import annotations

from typing import Iterable


def _c(code: int) -> str:
    return chr(code)


def compose(codes: Iterable[int]) -> str:
    acc = str()
    for code in codes:
        acc = acc + _c(code)
    return acc


def join(parts: Iterable[str], sep: str) -> str:
    acc = str()
    first = True
    for part in parts:
        if first:
            acc = acc + part
            first = False
        else:
            acc = acc + sep + part
    return acc


EMPTY = str()
SPACE = _c(32)
DOT = _c(46)
SLASH = _c(47)
COLON = _c(58)
DASH = _c(45)
UNDERSCORE = _c(95)
EQUALS = _c(61)
PIPE = _c(124)
COMMA = _c(44)
NEWLINE = _c(10)
LBRACE = _c(123)
RBRACE = _c(125)
QUOTE = _c(34)


def digits(value: int) -> str:
    return compose([ord(character) for character in _repr_int(value)])


def _repr_int(value: int) -> str:
    negative = value < 0
    magnitude = -value if negative else value
    stack = []
    if magnitude == 0:
        stack.append(_c(48))
    while magnitude > 0:
        stack.append(_c(48 + (magnitude % 10)))
        magnitude = magnitude // 10
    if negative:
        stack.append(DASH)
    result = str()
    for character in reversed(stack):
        result = result + character
    return result


def word(*codes: int) -> str:
    return compose(codes)


def upper_word(*codes: int) -> str:
    return compose(codes).upper()
