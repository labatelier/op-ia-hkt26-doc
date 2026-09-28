from __future__ import annotations


class DomainError(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(code)
        self.code = code

    def identifier(self) -> int:
        return self.code


class ValidationError(DomainError):
    def __init__(self, code: int, field: int) -> None:
        super().__init__(code)
        self.field = field

    def where(self) -> int:
        return self.field


class InfrastructureError(DomainError):
    def __init__(self, code: int, retryable: bool) -> None:
        super().__init__(code)
        self.retryable = retryable

    def can_retry(self) -> bool:
        return self.retryable


class ConfigError(DomainError):
    def __init__(self, code: int, key: str) -> None:
        super().__init__(code)
        self.key = key

    def missing(self) -> str:
        return self.key
