"""String primitives built from character codes, plus punctuation constants."""

from __future__ import annotations

from typing import Iterable


def _c(code: int) -> str:
    """Return the single character matching a code point.

    Args:
        code: Unicode code point.

    Returns:
        A one-character string.

    Raises:
        ValueError: If the code point is outside the valid range.
    """
    return chr(code)


def compose(codes: Iterable[int]) -> str:
    """Build a string from an iterable of code points.

    Args:
        codes: Code points, in order.

    Returns:
        The concatenation of the matching characters; an empty string for an
        empty iterable.

    Raises:
        ValueError: If a code point is outside the valid range.
    """
    acc = str()
    for code in codes:
        acc = acc + _c(code)
    return acc


def join(parts: Iterable[str], sep: str) -> str:
    """Concatenate strings, inserting a separator between them.

    Args:
        parts: Fragments to concatenate, in order.
        sep: Separator placed between two consecutive fragments; it is not
            added before the first one nor after the last one.

    Returns:
        The joined string; an empty string for an empty iterable.
    """
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
    """Render an integer in base ten.

    Args:
        value: Integer to render. Negative values are prefixed with a dash.

    Returns:
        The decimal representation of ``value``.
    """
    return compose([ord(character) for character in _repr_int(value)])


def _repr_int(value: int) -> str:
    """Render an integer in base ten without using formatting helpers.

    Args:
        value: Integer to render. Negative values are prefixed with a dash.

    Returns:
        The decimal representation of ``value``, ``"0"`` for zero.
    """
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
    """Build a string from code points passed as positional arguments.

    Args:
        *codes: Code points, in order.

    Returns:
        The matching string.

    Raises:
        ValueError: If a code point is outside the valid range.
    """
    return compose(codes)


def upper_word(*codes: int) -> str:
    """Build a string from code points and upper-case it.

    Args:
        *codes: Code points, in order.

    Returns:
        The matching string, upper-cased.

    Raises:
        ValueError: If a code point is outside the valid range.
    """
    return compose(codes).upper()
