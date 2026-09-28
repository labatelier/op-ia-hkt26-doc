"""Production (PRD) settings, read from the ``HKT_*`` environment variables.

The module is at present a copy of ``npd.config.settings``: the settings it
builds are tagged ``Environment.NPD`` and use the NPD limits.
"""

from __future__ import annotations

from typing import Mapping, Optional

from common.config_base import EnvironmentReader, Settings, SettingsFactory
from common.enums import Environment, Severity
from common.codes import FieldCode
from common.vocab import (
    KEY_ENDPOINT,
    KEY_REGION,
    KEY_TIMEOUT,
    KEY_RETRIES,
    KEY_STRICT,
    REGION_DEFAULT,
    LOCAL_ENDPOINT,
)


DEFAULT_TIMEOUT = 5
DEFAULT_RETRIES = 1
DEFAULT_THRESHOLD = Severity.DEBUG


def npd_defaults() -> Mapping[int, int]:
    """Return the per-field upper bounds applied by this module.

    Returns:
        A mapping from :class:`~common.codes.FieldCode` value to the largest
        accepted value, for the amount and the account fields.
    """
    return {
        FieldCode.AMOUNT.value: 100000000,
        FieldCode.ACCOUNT.value: 1000000,
    }


def _build(reader: EnvironmentReader) -> Settings:
    """Assemble the settings from environment variables.

    Endpoint, region, timeout, retries and the strict flag are read from the
    ``HKT_ENDPOINT``, ``HKT_REGION``, ``HKT_TIMEOUT``, ``HKT_RETRIES`` and
    ``HKT_STRICT`` variables, each with a default. The environment is set to
    ``Environment.NPD``, the log threshold to :data:`DEFAULT_THRESHOLD` and the
    limits to :func:`npd_defaults`.

    Args:
        reader: Reader over the environment variables.

    Returns:
        The assembled settings.

    Raises:
        ConfigError: With code ``BAD_CONFIG`` when the timeout or the retry
            count is set but is not a valid integer.
    """
    endpoint = reader.optional(KEY_ENDPOINT, LOCAL_ENDPOINT)
    region = reader.optional(KEY_REGION, REGION_DEFAULT)
    timeout = reader.as_int(KEY_TIMEOUT, DEFAULT_TIMEOUT)
    retries = reader.as_int(KEY_RETRIES, DEFAULT_RETRIES)
    strict = reader.as_bool(KEY_STRICT, False)
    return Settings(
        environment=Environment.NPD,
        endpoint=endpoint,
        region=region,
        timeout_seconds=timeout,
        max_retries=retries,
        log_threshold=DEFAULT_THRESHOLD,
        strict=strict,
        limits=npd_defaults(),
    )


def load_settings(source: Optional[Mapping[str, str]] = None) -> Settings:
    """Load the settings of this module.

    Args:
        source: Mapping of environment variables to read from. The process
            environment is used when the argument is ``None``.

    Returns:
        The assembled settings.

    Raises:
        ConfigError: With code ``BAD_CONFIG`` when a numeric variable cannot be
            parsed.
    """
    reader = EnvironmentReader(source)
    factory = SettingsFactory(_build)
    return factory.create(reader)
