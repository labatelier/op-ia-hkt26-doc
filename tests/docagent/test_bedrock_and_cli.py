from __future__ import annotations

from docagent.adapters.bedrock_llm import BedrockDocGenerator, build_prompt
from docagent.domain.models import DocKind, DocTarget
from docagent.main import main


def _target(kind=DocKind.FUNCTION, sig="def add(a, b)"):
    return DocTarget(
        qualified_name="add",
        kind=kind,
        signature=sig,
        source_snippet="def add(a, b):\n    return a + b",
        start_line=1,
        end_line=2,
        file_path="src/m.py",
    )


def test_prompt_includes_signature_and_source() -> None:
    prompt = build_prompt(_target())
    assert "def add(a, b)" in prompt
    assert "return a + b" in prompt
    assert "PEP 257" in prompt
    assert "function" in prompt


def test_prompt_kind_word_for_class() -> None:
    prompt = build_prompt(_target(kind=DocKind.CLASS, sig="class Box"))
    assert "class" in prompt
    assert "class Box" in prompt


def test_generator_with_injected_agent_returns_text() -> None:
    class StubAgent:
        def __call__(self, prompt: str) -> str:
            return "  Add two numbers and return the sum.  "

    gen = BedrockDocGenerator("model", "region", agent=StubAgent())
    result = gen.generate_docstring(_target())
    assert result.is_ok()
    assert result.value == "Add two numbers and return the sum."


def test_generator_empty_response_is_error() -> None:
    class EmptyAgent:
        def __call__(self, prompt: str) -> str:
            return "   "

    gen = BedrockDocGenerator("model", "region", agent=EmptyAgent())
    assert gen.generate_docstring(_target()).is_err()


def test_cli_requires_owner_and_repo(capsys) -> None:
    code = main(["--prompt", "go"])
    assert code == 2
    assert "owner/name required" in capsys.readouterr().err


def test_cli_requires_token(monkeypatch, capsys) -> None:
    monkeypatch.delenv("GITHUB_PAT", raising=False)
    code = main(["--owner", "o", "--repo", "r"])
    assert code == 2
    assert "PAT not found" in capsys.readouterr().err
