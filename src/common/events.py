from __future__ import annotations

from enum import IntEnum


class Event(IntEnum):
    START = 1
    STOP = 2
    PROCESS = 3
    ACCEPT = 4
    REJECT = 5
    PERSIST = 6
    HEALTH = 7
    RETRY = 8
    FAIL = 9
    VALIDATE = 10
    CONFIG_LOAD = 11
    DISPATCH = 12
