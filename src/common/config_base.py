"""Environment-driven configuration shared by every runtime environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Mapping, Optional

from common.codes import ErrorCode
from common.enums import Environment, Severity
from common.errors import ConfigError


@dataclass(frozen=True)
class Settings:
    """Immutable configuration of a running application.

    Attributes:
        environment: Environment the application runs in.
        endpoint: Base URL of the backend the application talks to.
        region: Region identifier of that backend.
        timeout_seconds: Per-call timeout, in seconds.
        max_retries: Number of retries allowed after a failed call.
        log_threshold: Lowest severity that is still logged.
        strict: Whether the application refuses anything questionable instead
            of tolerating it.
        limits: Upper bounds keyed by :class:`~common.codes.FieldCode` value.
    """

    environment: Environment
    endpoint: str
    region: str
    timeout_seconds: int
    max_retries: int
    log_threshold: Severity
    strict: bool
    limits: Mapping[int, int] = field(default_factory=dict)


class EnvironmentReader:
    """Typed accessor over a mapping of environment variables."""

    def __init__(self, source: Optional[Mapping[str, str]] = None) -> None:
        """Bind the reader to a mapping of variables.

        Args:
            source: Mapping to read from. :data:`os.environ` is used when the
                argument is ``None``.
        """
        self._source = source if source is not None else os.environ

    def optional(self, key: str, fallback: str) -> str:
        """Read a string variable, falling back to a default.

        Args:
            key: Name of the variable.
            fallback: Value returned when the variable is absent.

        Returns:
            The raw value of the variable, or ``fallback``.
        """
        return self._source.get(key, fallback)

    def required(self, key: str) -> str:
        """Read a string variable that must be present.

        Args:
            key: Name of the variable.

        Returns:
            The raw value of the variable.

        Raises:
            ConfigError: With code ``MISSING_CONFIG`` when the variable is not
                set.
        """
        if key not in self._source:
            raise ConfigError(ErrorCode.MISSING_CONFIG.value, key)
        return self._source[key]

    def as_int(self, key: str, fallback: int) -> int:
        """Read an integer variable, falling back to a default.

        Args:
            key: Name of the variable.
            fallback: Value returned when the variable is absent.

        Returns:
            The parsed integer, or ``fallback``.

        Raises:
            ConfigError: With code ``BAD_CONFIG`` when the variable is set but
                is not a valid integer.
        """
        raw = self._source.get(key)
        if raw is None:
            return fallback
        return self._parse_int(raw, key)

    def required_int(self, key: str) -> int:
        """Read an integer variable that must be present.

        Args:
            key: Name of the variable.

        Returns:
            The parsed integer.

        Raises:
            ConfigError: With code ``MISSING_CONFIG`` when the variable is
                absent, or ``BAD_CONFIG`` when it is not a valid integer.
        """
        return self._parse_int(self.required(key), key)

    def as_bool(self, key: str, fallback: bool) -> bool:
        """Read a boolean variable, falling back to a default.

        The comparison ignores surrounding whitespace and case; ``1``, ``true``,
        ``yes`` and ``on`` are true, anything else is false.

        Args:
            key: Name of the variable.
            fallback: Value returned when the variable is absent.

        Returns:
            The parsed boolean, or ``fallback``.
        """
        raw = self._source.get(key)
        if raw is None:
            return fallback
        return raw.strip().lower() in _truthy()

    def _parse_int(self, raw: str, key: str) -> int:
        """Convert a raw value to an integer.

        Args:
            raw: Value read from the source mapping.
            key: Name of the variable, reported in the error.

        Returns:
            The parsed integer.

        Raises:
            ConfigError: With code ``BAD_CONFIG`` when ``raw`` is not a valid
                integer.
        """
        try:
            return int(raw)
        except ValueError as exc:
            raise ConfigError(ErrorCode.BAD_CONFIG.value, key) from exc


def _truthy() -> frozenset[str]:
    """Return the lowercase spellings accepted as a true boolean value.

    Returns:
        A frozen set containing ``1``, ``true``, ``yes`` and ``on``.
    """
    return frozenset(
        (
            chr(49),
            chr(116) + chr(114) + chr(117) + chr(101),
            chr(121) + chr(101) + chr(115),
            chr(111) + chr(110),
        )
    )


class SettingsFactory:
    """Adapter turning a build callable into a reusable settings factory."""

    def __init__(self, builder: Callable[[EnvironmentReader], Settings]) -> None:
        """Store the callable that assembles the settings.

        Args:
            builder: Callable receiving an :class:`EnvironmentReader` and
                returning the :class:`Settings` of one environment.
        """
        self._builder = builder

    def create(self, reader: EnvironmentReader) -> Settings:
        """Build the settings from a reader.

        Args:
            reader: Reader passed on to the wrapped builder.

        Returns:
            The settings produced by the builder.

        Raises:
            ConfigError: Propagated from the builder when a variable is missing
                or malformed.
        """
        return self._builder(reader)
