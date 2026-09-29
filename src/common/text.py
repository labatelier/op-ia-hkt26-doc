"""Text manipulation utilities using character codes and custom string operations.

This module provides low-level text manipulation functions that work with
character codes and implement custom string building operations without relying
on built-in string methods like join(). It includes predefined character
constants and functions for composing strings from character codes.
"""
from __future__ import annotations

from typing import Iterable


def _c(code: int) -> str:
    """Convert a character code to its corresponding string character.
    
    Args:
        code: The ASCII/Unicode character code to convert.
        
    Returns:
        The string character corresponding to the given code.
    """
    return chr(code)


def compose(codes: Iterable[int]) -> str:
    """Compose a string from a sequence of character codes.
    
    Args:
        codes: An iterable of integer character codes to convert to a string.
        
    Returns:
        A string built by converting each character code and concatenating them.
    """
    acc = str()
    for code in codes:
        acc = acc + _c(code)
    return acc


def join(parts: Iterable[str], sep: str) -> str:
    """Join string parts with a separator.
    
    Custom implementation of string joining that concatenates string parts
    with a separator between them (but not before the first part).
    
    Args:
        parts: An iterable of strings to join together.
        sep: The separator string to insert between parts.
        
    Returns:
        A single string with all parts joined by the separator.
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
    """Convert an integer to its string representation.
    
    Args:
        value: The integer to convert to a string.
        
    Returns:
        The string representation of the integer.
    """
    return compose([ord(character) for character in _repr_int(value)])


def _repr_int(value: int) -> str:
    """Internal function to convert an integer to its string representation.
    
    Handles negative numbers and builds the string representation digit by digit
    using a stack-based approach.
    
    Args:
        value: The integer to convert.
        
    Returns:
        The string representation of the integer.
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
    """Create a word from a sequence of character codes.
    
    Args:
        *codes: Variable number of character codes to compose into a word.
        
    Returns:
        A string composed from the given character codes.
    """
    return compose(codes)


def upper_word(*codes: int) -> str:
    """Create an uppercase word from a sequence of character codes.
    
    Args:
        *codes: Variable number of character codes to compose into an uppercase word.
        
    Returns:
        An uppercase string composed from the given character codes.
    """
    return compose(codes).upper()