from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        raise NotImplementedError

    def epoch_millis(self) -> int:
        return int(self.now().timestamp() * 1000)


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock(Clock):
    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment

    def advance(self, seconds: int) -> None:
        self._moment = datetime.fromtimestamp(
            self._moment.timestamp() + seconds, tz=timezone.utc
        )
