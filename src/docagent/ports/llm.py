from __future__ import annotations

from typing import Protocol, runtime_checkable

from common.errors import DomainError
from common.result import Result

from docagent.domain.models import DocTarget


@runtime_checkable
class DocGenerator(Protocol):
    """Port for generating a docstring for a single target.

    Implementations may call a language model (Bedrock) or return canned text
    (the fake used in tests). The returned string is the docstring body WITHOUT
    surrounding triple quotes; rendering adds those and handles indentation.
    """

    def generate_docstring(self, target: DocTarget) -> Result[str, DomainError]:
        """Generate a docstring for ``target``.

        Args:
            target: The definition needing documentation.

        Returns:
            ``ok(str)`` with the docstring body, or ``err(DomainError)`` on
            failure.
        """
        ...
