from __future__ import annotations

from common.errors import DomainError
from common.result import Result, ok

from docagent.domain.models import DocKind, DocTarget


class FakeDocGenerator:
    """Deterministic :class:`~docagent.ports.llm.DocGenerator` for tests.

    Produces PEP 257-style docstrings without any network or model call, so the
    full analyze -> generate -> render pipeline can run offline.
    """

    def generate_docstring(self, target: DocTarget) -> Result[str, DomainError]:
        """Return a deterministic docstring for ``target``."""
        if target.kind is DocKind.MODULE:
            summary = "Module documentation."
        elif target.kind is DocKind.CLASS:
            summary = "Documentation for the " + target.qualified_name + " class."
        else:
            summary = "Documentation for the " + target.qualified_name + " function."
        return ok(summary)
