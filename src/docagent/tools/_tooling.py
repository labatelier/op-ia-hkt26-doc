from __future__ import annotations

from typing import Any, Callable

# Strands provides the `@tool` decorator that turns a function into an agent
# tool (using its docstring + type hints as the schema). It is an optional
# dependency: in offline/test environments it may be absent, so we fall back to
# a no-op decorator that leaves the function directly callable and unit-testable.
try:  # pragma: no cover - exercised only when strands is installed
    from strands import tool as tool  # type: ignore
except Exception:  # pragma: no cover - the offline path

    def tool(func: Callable[..., Any]) -> Callable[..., Any]:
        """No-op fallback for the Strands ``@tool`` decorator.

        Returns the function unchanged so tool bodies remain plain callables when
        Strands is not installed.
        """
        return func
