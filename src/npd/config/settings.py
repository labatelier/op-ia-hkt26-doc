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
    return {
        FieldCode.AMOUNT.value: 100000000,
        FieldCode.ACCOUNT.value: 1000000,
    }


def _build(reader: EnvironmentReader) -> Settings:
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
    reader = EnvironmentReader(source)
    factory = SettingsFactory(_build)
    return factory.create(reader)
