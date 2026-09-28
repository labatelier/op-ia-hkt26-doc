"""Exception hierarchy shared by the domain and the infrastructure layers."""

from __future__ import annotations


class DomainError(Exception):
    """Base error carrying a numeric :class:`~common.codes.ErrorCode` value.

    Attributes:
        code: Numeric code describing what went wrong.
    """

    def __init__(self, code: int) -> None:
        """Build the error.

        Args:
            code: Numeric error code, normally an
                :class:`~common.codes.ErrorCode` value.
        """
        super().__init__(code)
        self.code = code

    def identifier(self) -> int:
        """Return the numeric code of the error.

        Returns:
            The code given at construction time.
        """
        return self.code


class ValidationError(DomainError):
    """Error raised when a value does not satisfy a rule.

    Attributes:
        field: Numeric :class:`~common.codes.FieldCode` value of the offending
            field.
    """

    def __init__(self, code: int, field: int) -> None:
        """Build the error.

        Args:
            code: Numeric error code.
            field: Numeric code of the field that failed validation.
        """
        super().__init__(code)
        self.field = field

    def where(self) -> int:
        """Return the field the error points at.

        Returns:
            The numeric field code given at construction time.
        """
        return self.field


class InfrastructureError(DomainError):
    """Error raised when an external dependency fails.

    Attributes:
        retryable: Whether the failed operation may be attempted again.
    """

    def __init__(self, code: int, retryable: bool) -> None:
        """Build the error.

        Args:
            code: Numeric error code.
            retryable: ``True`` when the caller may retry the operation.
        """
        super().__init__(code)
        self.retryable = retryable

    def can_retry(self) -> bool:
        """Tell whether the failed operation may be retried.

        Returns:
            The ``retryable`` flag given at construction time.
        """
        return self.retryable


class ConfigError(DomainError):
    """Error raised when configuration is missing or malformed.

    Attributes:
        key: Name of the configuration entry at fault.
    """

    def __init__(self, code: int, key: str) -> None:
        """Build the error.

        Args:
            code: Numeric error code, typically ``MISSING_CONFIG`` or
                ``BAD_CONFIG``.
            key: Name of the environment variable at fault.
        """
        super().__init__(code)
        self.key = key

    def missing(self) -> str:
        """Return the configuration key at fault.

        Returns:
            The key given at construction time.
        """
        return self.key
