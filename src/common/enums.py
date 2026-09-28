from __future__ import annotations

from enum import Enum, IntEnum, auto


class Environment(Enum):
    NPD = auto()
    PRD = auto()


class Severity(IntEnum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class Status(Enum):
    PENDING = auto()
    ACCEPTED = auto()
    REJECTED = auto()
    SETTLED = auto()
    FAILED = auto()


class Outcome(Enum):
    SUCCESS = auto()
    FAILURE = auto()


class Kind(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER = auto()
    ADJUSTMENT = auto()
