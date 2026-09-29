from __future__ import annotations

import ast
import hashlib
from typing import List, Sequence, Tuple

from common.codes import ErrorCode
from common.errors import DomainError
from common.result import Result, err, ok

from docagent.domain.models import AnalysisReport, DocKind, DocProposal

_INDENT = "    "


def render_documented_source(
    source: str,
    proposals: Sequence[DocProposal],
) -> Result[str, DomainError]:
    """Insert generated docstrings into Python source.

    Each proposal's docstring is inserted immediately after the ``def``/``class``
    header (for functions and classes) or at the very top of the file (for the
    module). Indentation is derived from the target's body so the result is valid
    Python. The rendered source is re-parsed with :mod:`ast` as a safety check.

    Args:
        source: The original source text.
        proposals: Docstrings to insert. Proposals whose target already resolves
            to a documented node are still inserted; callers are expected to pass
            only genuinely-missing targets (as produced by the analyzer).

    Returns:
        ``ok(str)`` with the documented source, or ``err(DomainError)`` with
        :attr:`ErrorCode.RENDER_ERROR` if the result does not parse or a target
        cannot be located.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return err(DomainError(ErrorCode.RENDER_ERROR.value))

    lines = source.splitlines()
    # (insert_at_line_index, indent, docstring_text, is_module)
    insertions: List[Tuple[int, str, str, bool]] = []

    module_proposals = [p for p in proposals if p.target.kind is DocKind.MODULE]
    node_proposals = [p for p in proposals if p.target.kind is not DocKind.MODULE]

    node_index = _index_definitions(tree)
    for proposal in node_proposals:
        located = node_index.get(proposal.target.qualified_name)
        if located is None:
            return err(DomainError(ErrorCode.RENDER_ERROR.value))
        header_line, body_indent = located
        insertions.append(
            (header_line, body_indent, proposal.docstring, False)
        )

    for proposal in module_proposals:
        insertions.append((0, "", proposal.docstring, True))

    # Apply insertions from the bottom up so earlier line indices stay valid.
    insertions.sort(key=lambda item: item[0], reverse=True)
    for insert_at, indent, docstring, is_module in insertions:
        block = _format_docstring(docstring, indent, is_module)
        lines[insert_at:insert_at] = block

    rendered = "\n".join(lines)
    if source.endswith("\n") and not rendered.endswith("\n"):
        rendered += "\n"

    try:
        ast.parse(rendered)
    except SyntaxError:
        return err(DomainError(ErrorCode.RENDER_ERROR.value))
    return ok(rendered)


def _index_definitions(tree: ast.Module):
    """Map qualified names to (insert_line_index, body_indent)."""
    index = {}

    def visit(body, prefix: str) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qualified = node.name if prefix == "" else prefix + "." + node.name
                # Insert after the header line (the line where the body starts).
                first_body = node.body[0]
                insert_index = first_body.lineno - 1
                body_indent = _INDENT * _depth(qualified)
                index[qualified] = (insert_index, body_indent)
                visit(node.body, qualified)

    visit(tree.body, "")
    return index


def _depth(qualified_name: str) -> int:
    return qualified_name.count(".") + 1


def _format_docstring(text: str, indent: str, is_module: bool) -> List[str]:
    cleaned = text.strip().strip('"').strip()
    body_lines = cleaned.splitlines() or [""]
    if len(body_lines) == 1:
        rendered = [indent + '"""' + body_lines[0] + '"""']
    else:
        rendered = [indent + '"""' + body_lines[0]]
        for line in body_lines[1:]:
            rendered.append((indent + line) if line else "")
        rendered.append(indent + '"""')
    if is_module:
        rendered.append("")
    return rendered


def build_pr(
    report: AnalysisReport,
    proposals: Sequence[DocProposal],
) -> Tuple[str, str, str]:
    """Build the branch name, title, and body for a documentation pull request.

    Args:
        report: The analysis report the proposals were derived from.
        proposals: The docstrings that will be committed.

    Returns:
        A ``(branch_name, title, body)`` tuple. The branch name embeds a short
        hash of the file path and documented symbols so repeated runs do not
        collide.
    """
    names = ", ".join(p.target.qualified_name for p in proposals) or "none"
    seed = report.file_path + "|" + names
    short = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    branch = "docagent/docstrings-" + short

    count = len(proposals)
    title = "docs: add docstrings to " + report.file_path

    body_lines = [
        "## Documentation Agent",
        "",
        "Generated docstrings for `" + report.file_path + "`.",
        "",
        "Documented " + str(count) + " symbol(s):",
        "",
    ]
    for proposal in proposals:
        kind = proposal.target.kind.name.lower()
        body_lines.append("- `" + proposal.target.qualified_name + "` (" + kind + ")")
    body_lines.append("")
    body_lines.append("_Please review and merge if the docstrings are accurate._")
    body = "\n".join(body_lines)

    return branch, title, body
