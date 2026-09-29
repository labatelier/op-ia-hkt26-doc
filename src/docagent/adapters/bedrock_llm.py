from __future__ import annotations

from typing import Any, Optional

from common.codes import ErrorCode
from common.errors import DomainError
from common.result import Result, err, ok

from docagent.domain.models import DocKind, DocTarget

_KIND_WORD = {
    DocKind.MODULE: "module",
    DocKind.CLASS: "class",
    DocKind.FUNCTION: "function",
}


def build_prompt(target: DocTarget) -> str:
    """Build the model prompt for documenting a single target.

    Pure function (no I/O) so it can be unit-tested without a model.

    Args:
        target: The definition to document.

    Returns:
        A prompt instructing the model to return only a PEP 257 docstring body.
    """
    kind = _KIND_WORD[target.kind]
    lines = [
        "Write a concise, accurate Python docstring for the following "
        + kind
        + ".",
        "Return ONLY the docstring text (no triple quotes, no code, no markdown).",
        "Follow PEP 257. For functions, include an Args section when there are "
        "parameters and a Returns section when it returns a value.",
        "",
        "Qualified name: " + target.qualified_name,
    ]
    if target.signature:
        lines.append("Signature: " + target.signature)
    lines.append("")
    lines.append("Source:")
    lines.append(target.source_snippet)
    return "\n".join(lines)


class BedrockDocGenerator:
    """A :class:`~docagent.ports.llm.DocGenerator` backed by Strands + Bedrock.

    Strands is an optional dependency, imported lazily so this module can be
    imported (and :func:`build_prompt` unit-tested) without it installed.
    """

    def __init__(self, model_id: str, region: str, agent: Optional[Any] = None) -> None:
        self._model_id = model_id
        self._region = region
        self._agent = agent

    def _ensure_agent(self) -> Any:
        if self._agent is not None:
            return self._agent
        try:
            from strands import Agent  # type: ignore
            from strands.models import BedrockModel  # type: ignore
        except Exception as exc:  # pragma: no cover - requires strands absent
            raise RuntimeError(
                "strands-agents is required for Bedrock generation; install the "
                "'agent' extra"
            ) from exc
        model = BedrockModel(model_id=self._model_id, region_name=self._region)
        self._agent = Agent(
            model=model,
            system_prompt="You write precise Python docstrings.",
        )
        return self._agent

    def generate_docstring(self, target: DocTarget) -> Result[str, DomainError]:
        """Generate a docstring for ``target`` by invoking the Bedrock model."""
        prompt = build_prompt(target)
        try:
            agent = self._ensure_agent()
            response = agent(prompt)
            text = str(response).strip()
        except Exception:  # pragma: no cover - live path
            return err(DomainError(ErrorCode.GENERATION_ERROR.value))
        if text == "":
            return err(DomainError(ErrorCode.GENERATION_ERROR.value))
        return ok(text)
