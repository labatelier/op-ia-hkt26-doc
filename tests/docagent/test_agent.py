from __future__ import annotations

from docagent.adapters.fake_llm import FakeDocGenerator
from docagent.adapters.fake_repo import FakePublisher
from docagent.agent import (
    SYSTEM_PROMPT,
    TOOL_NAMES,
    collect_tools,
)
from docagent.config.settings import load_settings


def _settings():
    return load_settings({"DOCAGENT_BASE_BRANCH": "main"})


def test_tool_names_order() -> None:
    assert TOOL_NAMES == [
        "list_python_files",
        "read_source_file",
        "analyze_python_source",
        "generate_docstrings",
        "render_documented_source",
        "open_documentation_pr",
    ]


def test_collect_tools_matches_declared_names() -> None:
    tools = collect_tools(FakeDocGenerator(), FakePublisher({}), _settings())
    names = [t.__name__ for t in tools]
    assert names == TOOL_NAMES


def test_collected_tools_are_callable_and_bound() -> None:
    pub = FakePublisher({"src/a.py": "def f():\n    return 1\n"})
    tools = collect_tools(FakeDocGenerator(), pub, _settings())
    by_name = {t.__name__: t for t in tools}
    # The bound list tool works end to end against the fake publisher.
    listed = by_name["list_python_files"]()
    assert listed["status"] == "success"
    assert listed["files"] == ["src/a.py"]


def test_system_prompt_enforces_pr_flow() -> None:
    assert "open_documentation_pr" in SYSTEM_PROMPT
    assert "ONCE" in SYSTEM_PROMPT
    assert "NEVER commit or push directly to the default branch" in SYSTEM_PROMPT
