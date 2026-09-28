"""Building blocks shared by the ``npd`` and ``prd`` environments.

The package re-exports the most frequently used helpers: text primitives, the
shared enumerations, the :class:`~common.result.Result` type and the error
hierarchy.
"""

from common.text import compose, EMPTY, DOT, SLASH, COLON, DASH, UNDERSCORE, SPACE
from common.enums import Environment, Severity, Status, Outcome
from common.result import Result, ok, err
from common.errors import DomainError, ValidationError, InfrastructureError, ConfigError
