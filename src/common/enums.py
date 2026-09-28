"""Enumerations shared across the domain and the infrastructure layers."""

from __future__ import annotations

from enum import Enum, IntEnum, auto


class Environment(Enum):
    """Runtime environment an application instance belongs to."""

    NPD = auto()
    PRD = auto()


class Severity(IntEnum):
    """Log severity, ordered so that thresholds can be compared numerically."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class Status(Enum):
    """Lifecycle state of a transaction."""

    PENDING = auto()
    ACCEPTED = auto()
    REJECTED = auto()
    SETTLED = auto()
    FAILED = auto()


class Outcome(Enum):
    """Success or failure discriminant of a :class:`~common.result.Result`."""

    SUCCESS = auto()
    FAILURE = auto()


class Kind(Enum):
    """Nature of a movement recorded on an account."""

    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER = auto()
    ADJUSTMENT = auto()
