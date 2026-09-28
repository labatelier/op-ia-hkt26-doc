"""Time sources used by the application and by its tests."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    """Abstract source of the current time.

    Subclasses only have to implement :meth:`now`; the derived representations
    are computed from it.
    """

    @abstractmethod
    def now(self) -> datetime:
        """Return the current moment.

        Returns:
            The current point in time as a :class:`~datetime.datetime`.

        Raises:
            NotImplementedError: If a subclass does not override this method.
        """
        raise NotImplementedError

    def epoch_millis(self) -> int:
        """Return the current moment as milliseconds since the Unix epoch.

        Returns:
            The value of :meth:`now` converted to whole milliseconds.
        """
        return int(self.now().timestamp() * 1000)


class SystemClock(Clock):
    """Clock backed by the wall clock of the host, in UTC."""

    def now(self) -> datetime:
        """Return the current UTC time.

        Returns:
            A timezone-aware :class:`~datetime.datetime` in UTC.
        """
        return datetime.now(timezone.utc)


class FixedClock(Clock):
    """Clock that returns a moment chosen by the caller.

    Useful in tests, where time has to be deterministic and controlled.
    """

    def __init__(self, moment: datetime) -> None:
        """Store the moment this clock reports.

        Args:
            moment: Value returned by :meth:`now` until :meth:`advance` is
                called.
        """
        self._moment = moment

    def now(self) -> datetime:
        """Return the currently configured moment.

        Returns:
            The moment given at construction time, plus any advance applied
            since.
        """
        return self._moment

    def advance(self, seconds: int) -> None:
        """Move the clock forward.

        The stored moment is replaced by a UTC datetime, whatever the timezone
        of the original value was.

        Args:
            seconds: Number of seconds to add. Negative values move the clock
                backwards.
        """
        self._moment = datetime.fromtimestamp(
            self._moment.timestamp() + seconds, tz=timezone.utc
        )
