from __future__ import annotations

from typing import Any, Dict, List

from docagent.domain.analyzer import analyze_source
from docagent.domain.models import DocProposal, DocTarget
from docagent.domain.rendering import render_documented_source
from docagent.ports.llm import DocGenerator
from docagent.tools._tooling import tool


def _error(message: str) -> Dict[str, Any]:
    return {"status": "error", "message": message}


def _ok(**payload: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {"status": "success"}
    result.update(payload)
    return result


class DocstringTools:
    """Docstring analysis/generation tools sharing a :class:`DocGenerator`.

    The generator is injected once so the same instance (fake in tests, Bedrock
    in production) is reused across tool calls. Each method is registered as a
    Strands ``@tool``; every method returns a structured ``{"status": ...}`` dict
    and never raises into the agent loop.
    """

    def __init__(self, generator: DocGenerator) -> None:
        self._generator = generator

    @tool
    def analyze_python_source(self, path: str, source: str) -> Dict[str, Any]:
        """Analyze Python source and list definitions missing docstrings.

        Use this first to discover which module, classes, and functions in a
        file lack documentation.

        Args:
            path: Repository-relative path of the file (used for labelling).
            source: The full text of the Python file.

        Returns:
            On success, ``{"status": "success", "path", "missing_count",
            "targets": [{"qualified_name", "kind", "signature", "start_line",
            "end_line"}, ...]}``. On a parse error, ``{"status": "error",
            "message"}``.
        """
        result = analyze_source(source, path)
        if result.is_err():
            return _error("could not parse " + path)
        report = result.value
        targets = [
            {
                "qualified_name": t.qualified_name,
                "kind": t.kind.name,
                "signature": t.signature,
                "start_line": t.start_line,
                "end_line": t.end_line,
            }
            for t in report.targets
        ]
        return _ok(path=path, missing_count=report.missing_count(), targets=targets)

    @tool
    def generate_docstrings(self, path: str, source: str) -> Dict[str, Any]:
        """Generate docstrings for every undocumented definition in a file.

        Analyzes the source, then asks the language model for a docstring per
        missing target.

        Args:
            path: Repository-relative path of the file.
            source: The full text of the Python file.

        Returns:
            On success, ``{"status": "success", "path", "proposals":
            [{"qualified_name", "docstring"}, ...]}``. On failure,
            ``{"status": "error", "message"}``.
        """
        analysis = analyze_source(source, path)
        if analysis.is_err():
            return _error("could not parse " + path)
        proposals: List[Dict[str, str]] = []
        for target in analysis.value.targets:
            generated = self._generator.generate_docstring(target)
            if generated.is_err():
                return _error("generation failed for " + target.qualified_name)
            proposals.append(
                {"qualified_name": target.qualified_name, "docstring": generated.value}
            )
        return _ok(path=path, proposals=proposals)

    @tool
    def render_documented_source(self, path: str, source: str) -> Dict[str, Any]:
        """Produce a fully documented version of a Python file.

        Analyzes the file, generates a docstring for each missing target, and
        inserts them, returning the new file content ready to be committed.

        Args:
            path: Repository-relative path of the file.
            source: The full text of the Python file.

        Returns:
            On success, ``{"status": "success", "path", "content",
            "documented_count"}``. On failure, ``{"status": "error", "message"}``.
        """
        analysis = analyze_source(source, path)
        if analysis.is_err():
            return _error("could not parse " + path)

        proposals: List[DocProposal] = []
        for target in analysis.value.targets:
            generated = self._generator.generate_docstring(target)
            if generated.is_err():
                return _error("generation failed for " + target.qualified_name)
            proposals.append(DocProposal(target=target, docstring=generated.value))

        if not proposals:
            return _ok(path=path, content=source, documented_count=0)

        rendered = render_documented_source(source, proposals)
        if rendered.is_err():
            return _error("could not render docstrings for " + path)
        return _ok(path=path, content=rendered.value, documented_count=len(proposals))
