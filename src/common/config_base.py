from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Mapping, Optional

from common.codes import ErrorCode
from common.enums import Environment, Severity
from common.errors import ConfigError


@dataclass(frozen=True)
class Settings:
    environment: Environment
    endpoint: str
    region: str
    timeout_seconds: int
    max_retries: int
    log_threshold: Severity
    strict: bool
    limits: Mapping[int, int] = field(default_factory=dict)


class EnvironmentReader:
    def __init__(self, source: Optional[Mapping[str, str]] = None) -> None:
        self._source = source if source is not None else os.environ

    def optional(self, key: str, fallback: str) -> str:
        return self._source.get(key, fallback)

    def required(self, key: str) -> str:
        if key not in self._source:
            raise ConfigError(ErrorCode.MISSING_CONFIG.value, key)
        return self._source[key]

    def as_int(self, key: str, fallback: int) -> int:
        raw = self._source.get(key)
        if raw is None:
            return fallback
        return self._parse_int(raw, key)

    def required_int(self, key: str) -> int:
        return self._parse_int(self.required(key), key)

    def as_bool(self, key: str, fallback: bool) -> bool:
        raw = self._source.get(key)
        if raw is None:
            return fallback
        return raw.strip().lower() in _truthy()

    def _parse_int(self, raw: str, key: str) -> int:
        try:
            return int(raw)
        except ValueError as exc:
            raise ConfigError(ErrorCode.BAD_CONFIG.value, key) from exc


def _truthy() -> frozenset[str]:
    return frozenset(
        (
            chr(49),
            chr(116) + chr(114) + chr(117) + chr(101),
            chr(121) + chr(101) + chr(115),
            chr(111) + chr(110),
        )
    )


class SettingsFactory:
    def __init__(self, builder: Callable[[EnvironmentReader], Settings]) -> None:
        self._builder = builder

    def create(self, reader: EnvironmentReader) -> Settings:
        return self._builder(reader)
