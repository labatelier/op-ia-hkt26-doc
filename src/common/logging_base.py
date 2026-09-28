"""Minimal structured logging: JSON payloads written to pluggable sinks."""

from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Mapping

from common.clock import Clock, SystemClock
from common.enums import Environment, Severity
from common.vocab import FIELD_TS, FIELD_ENV, FIELD_LEVEL, FIELD_EVENT, FIELD_CONTEXT


class LogSink(ABC):
    """Destination a :class:`StructuredLogger` hands its payloads to."""

    @abstractmethod
    def emit(self, payload: Mapping[str, Any]) -> None:
        """Write one log record.

        Args:
            payload: Already assembled log record.

        Raises:
            NotImplementedError: If a subclass does not override this method.
        """
        raise NotImplementedError


class StreamSink(LogSink):
    """Sink writing one JSON object per line to a text stream."""

    def __init__(self, stream: Any = None) -> None:
        """Bind the sink to a stream.

        Args:
            stream: Object exposing ``write`` and ``flush``. :data:`sys.stdout`
                is used when the argument is ``None``.
        """
        self._stream = stream if stream is not None else sys.stdout

    def emit(self, payload: Mapping[str, Any]) -> None:
        """Serialise a record as JSON with sorted keys and flush the stream.

        Args:
            payload: Log record to write.

        Raises:
            TypeError: If the payload contains values JSON cannot serialise.
        """
        self._stream.write(json.dumps(payload, sort_keys=True))
        self._stream.write(chr(10))
        self._stream.flush()


class MemorySink(LogSink):
    """Sink keeping every record in memory, for tests and assertions.

    Attributes:
        records: Records emitted so far, in order, each copied into a plain
            dictionary.
    """

    def __init__(self) -> None:
        """Create an empty sink."""
        self.records: list[Mapping[str, Any]] = []

    def emit(self, payload: Mapping[str, Any]) -> None:
        """Append a copy of the record to :attr:`records`.

        Args:
            payload: Log record to store.
        """
        self.records.append(dict(payload))


class StructuredLogger:
    """Logger emitting flat JSON-friendly records to a single sink."""

    def __init__(
        self,
        environment: Environment,
        threshold: Severity,
        sink: LogSink,
        clock: Clock | None = None,
    ) -> None:
        """Configure the logger.

        Args:
            environment: Environment name stamped on every record.
            threshold: Lowest severity that is emitted; anything below is
                dropped.
            sink: Destination of the records.
            clock: Time source used for the timestamp. A
                :class:`~common.clock.SystemClock` is used when ``None``.
        """
        self._environment = environment
        self._threshold = threshold
        self._sink = sink
        self._clock = clock if clock is not None else SystemClock()

    def log(self, level: Severity, event: int, context: Mapping[str, Any]) -> None:
        """Emit a record unless its severity is below the threshold.

        The record carries the epoch timestamp in milliseconds, the environment
        name, the severity name, the event identifier and a copy of the
        context.

        Args:
            level: Severity of the record.
            event: Numeric event identifier, normally a
                :class:`~common.events.Event` value.
            context: Additional key/value pairs describing the occurrence.
        """
        if level.value < self._threshold.value:
            return
        payload = {
            FIELD_TS: self._clock.epoch_millis(),
            FIELD_ENV: self._environment.name,
            FIELD_LEVEL: level.name,
            FIELD_EVENT: event,
            FIELD_CONTEXT: dict(context),
        }
        self._sink.emit(payload)

    def debug(self, event: int, context: Mapping[str, Any]) -> None:
        """Log at :attr:`~common.enums.Severity.DEBUG` level.

        Args:
            event: Numeric event identifier.
            context: Additional key/value pairs.
        """
        self.log(Severity.DEBUG, event, context)

    def info(self, event: int, context: Mapping[str, Any]) -> None:
        """Log at :attr:`~common.enums.Severity.INFO` level.

        Args:
            event: Numeric event identifier.
            context: Additional key/value pairs.
        """
        self.log(Severity.INFO, event, context)

    def warning(self, event: int, context: Mapping[str, Any]) -> None:
        """Log at :attr:`~common.enums.Severity.WARNING` level.

        Args:
            event: Numeric event identifier.
            context: Additional key/value pairs.
        """
        self.log(Severity.WARNING, event, context)

    def error(self, event: int, context: Mapping[str, Any]) -> None:
        """Log at :attr:`~common.enums.Severity.ERROR` level.

        Args:
            event: Numeric event identifier.
            context: Additional key/value pairs.
        """
        self.log(Severity.ERROR, event, context)

    def critical(self, event: int, context: Mapping[str, Any]) -> None:
        """Log at :attr:`~common.enums.Severity.CRITICAL` level.

        Args:
            event: Numeric event identifier.
            context: Additional key/value pairs.
        """
        self.log(Severity.CRITICAL, event, context)
