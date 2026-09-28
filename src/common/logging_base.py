from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from typing import Any, Mapping

from common.clock import Clock, SystemClock
from common.enums import Environment, Severity
from common.vocab import FIELD_TS, FIELD_ENV, FIELD_LEVEL, FIELD_EVENT, FIELD_CONTEXT


class LogSink(ABC):
    @abstractmethod
    def emit(self, payload: Mapping[str, Any]) -> None:
        raise NotImplementedError


class StreamSink(LogSink):
    def __init__(self, stream: Any = None) -> None:
        self._stream = stream if stream is not None else sys.stdout

    def emit(self, payload: Mapping[str, Any]) -> None:
        self._stream.write(json.dumps(payload, sort_keys=True))
        self._stream.write(chr(10))
        self._stream.flush()


class MemorySink(LogSink):
    def __init__(self) -> None:
        self.records: list[Mapping[str, Any]] = []

    def emit(self, payload: Mapping[str, Any]) -> None:
        self.records.append(dict(payload))


class StructuredLogger:
    def __init__(
        self,
        environment: Environment,
        threshold: Severity,
        sink: LogSink,
        clock: Clock | None = None,
    ) -> None:
        self._environment = environment
        self._threshold = threshold
        self._sink = sink
        self._clock = clock if clock is not None else SystemClock()

    def log(self, level: Severity, event: int, context: Mapping[str, Any]) -> None:
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
        self.log(Severity.DEBUG, event, context)

    def info(self, event: int, context: Mapping[str, Any]) -> None:
        self.log(Severity.INFO, event, context)

    def warning(self, event: int, context: Mapping[str, Any]) -> None:
        self.log(Severity.WARNING, event, context)

    def error(self, event: int, context: Mapping[str, Any]) -> None:
        self.log(Severity.ERROR, event, context)

    def critical(self, event: int, context: Mapping[str, Any]) -> None:
        self.log(Severity.CRITICAL, event, context)
