"""Abstract clock interface and concrete implementations for time management.

Provides Clock abstract base class with now() method and epoch_millis() utility.
Includes SystemClock for real system time and FixedClock for testing with
controllable time advancement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    """Abstract base class for clock implementations.

    Defines the interface for retrieving current time with concrete implementations
    providing the now() method. Includes utility method for epoch milliseconds.
    """
    @abstractmethod
    def now(self) -> datetime:
        """Return the current datetime.

        Returns:
            datetime: The current date and time.
        """
        raise NotImplementedError

    def epoch_millis(self) -> int:
        """Return the current time as milliseconds since Unix epoch.

        Returns:
            int: The current time in milliseconds since January 1, 1970 UTC.
        """
        return int(self.now().timestamp() * 1000)


class SystemClock(Clock):
    """Clock implementation that returns the actual system time.

    Provides real-time clock functionality using the system's current UTC time.
    """
    def now(self) -> datetime:
        """Return the current system time in UTC.

        Returns:
            datetime: The current system date and time in UTC timezone.
        """
        return datetime.now(timezone.utc)


class FixedClock(Clock):
    """Clock implementation that returns a fixed, controllable time.

    Useful for testing scenarios where time needs to be controlled. Allows setting
    a specific moment and advancing time programmatically.
    """
    def __init__(self, moment: datetime) -> None:
        """Initialize the fixed clock with a specific moment in time.

        Args:
            moment: The datetime to use as the fixed time for this clock.
        """
        self._moment = moment

    def now(self) -> datetime:
        """Return the fixed moment in time.

        Returns:
            datetime: The fixed datetime set for this clock.
        """
        return self._moment

    def advance(self, seconds: int) -> None:
        """Advance the fixed clock time by the specified number of seconds.

        Args:
            seconds: The number of seconds to advance the clock time.
        """
        self._moment = datetime.fromtimestamp(
            self._moment.timestamp() + seconds, tz=timezone.utc
        )
