from __future__ import annotations

from typing import Any, List

from docagent.config.settings import DocAgentSettings
from docagent.ports.llm import DocGenerator
from docagent.ports.repo import RepoPublisher
from docagent.tools.docstring_tools import DocstringTools
from docagent.tools.repo_tools import RepoTools

SYSTEM_PROMPT = """\
You are the Documentation Agent. Your job is to add missing docstrings to a
Python repository and deliver them as a single pull request for human review.

Follow this workflow:
1. Call list_python_files to discover the Python files in the repository.
2. For each candidate file, call read_source_file to get its contents.
3. Call analyze_python_source to find definitions missing docstrings. Skip files
   with no missing docstrings.
4. Call generate_docstrings (or render_documented_source) to produce docstrings
   and the fully documented file content.
5. Collect the documented files and call open_documentation_pr ONCE to open a
   single pull request containing all changes, with a clear title and a body that
   lists the documented symbols.

Rules:
- NEVER commit or push directly to the default branch. All changes must go on a
  new branch surfaced through a pull request.
- Only add docstrings; do not otherwise modify code.
- If a tool returns {"status": "error"}, report the problem and continue with the
  remaining files rather than stopping.
"""

# The order tools are advertised to the model.
TOOL_NAMES: List[str] = [
    "list_python_files",
    "read_source_file",
    "analyze_python_source",
    "generate_docstrings",
    "render_documented_source",
    "open_documentation_pr",
]


def collect_tools(generator: DocGenerator, publisher: RepoPublisher, settings: DocAgentSettings) -> List[Any]:
    """Build the ordered list of bound tool callables for the agent.

    Args:
        generator: Docstring generator (fake or Bedrock-backed).
        publisher: Repository publisher (fake or GitHub REST-backed).
        settings: Agent settings (supplies the base branch).

    Returns:
        The bound tool methods in :data:`TOOL_NAMES` order.
    """
    doc_tools = DocstringTools(generator)
    repo_tools = RepoTools(publisher, base_branch=settings.base_branch)
    return [
        repo_tools.list_python_files,
        repo_tools.read_source_file,
        doc_tools.analyze_python_source,
        doc_tools.generate_docstrings,
        doc_tools.render_documented_source,
        repo_tools.open_documentation_pr,
    ]


def build_agent(
    generator: DocGenerator,
    publisher: RepoPublisher,
    settings: DocAgentSettings,
) -> Any:
    """Construct the Strands agent wired with the documentation tools.

    Strands is an optional dependency; importing it here (rather than at module
    load) keeps the domain, tools, and their tests runnable without it installed.

    Args:
        generator: Docstring generator implementation.
        publisher: Repository publisher implementation.
        settings: Agent settings (model id, base branch, ...).

    Returns:
        A configured Strands ``Agent`` instance.

    Raises:
        RuntimeError: If the ``strands`` package is not installed.
    """
    try:
        from strands import Agent  # type: ignore
    except Exception as exc:  # pragma: no cover - requires strands absent
        raise RuntimeError(
            "strands-agents is required to build the agent; install the 'agent' extra"
        ) from exc

    tools = collect_tools(generator, publisher, settings)
    return Agent(
        model=settings.model_id,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
