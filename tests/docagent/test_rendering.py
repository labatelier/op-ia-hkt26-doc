from __future__ import annotations

import ast

from docagent.domain.analyzer import analyze_source
from docagent.domain.models import (
    AnalysisReport,
    DocKind,
    DocProposal,
    DocTarget,
)
from docagent.domain.rendering import build_pr, render_documented_source

SOURCE = '''import os


def add(x, y):
    return x + y


class Widget:
    def __init__(self, size):
        self.size = size

    def area(self):
        return self.size * self.size
'''


def _proposals_for(source: str, file_path: str):
    report = analyze_source(source, file_path).value
    proposals = []
    for target in report.targets:
        text = "Summary for " + target.qualified_name + "."
        proposals.append(DocProposal(target=target, docstring=text))
    return report, proposals


def _docstrings(tree: ast.Module):
    found = {}
    if ast.get_docstring(tree) is not None:
        found["<module>"] = ast.get_docstring(tree)

    def visit(body, prefix):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = node.name if prefix == "" else prefix + "." + node.name
                ds = ast.get_docstring(node)
                if ds is not None:
                    found[q] = ds
                visit(node.body, q)

    visit(tree.body, "")
    return found


def test_rendered_source_reparses_and_has_all_docstrings() -> None:
    report, proposals = _proposals_for(SOURCE, "src/widget.py")
    result = render_documented_source(SOURCE, proposals)
    assert result.is_ok(), result

    rendered = result.value
    tree = ast.parse(rendered)  # must not raise
    docs = _docstrings(tree)

    assert "<module>" in docs
    assert docs["add"] == "Summary for add."
    assert docs["Widget"] == "Summary for Widget."
    assert docs["Widget.__init__"] == "Summary for Widget.__init__."
    assert docs["Widget.area"] == "Summary for Widget.area."


def test_reanalysis_after_render_finds_nothing() -> None:
    report, proposals = _proposals_for(SOURCE, "src/widget.py")
    rendered = render_documented_source(SOURCE, proposals).value
    # After documenting everything, a fresh analysis should be clean.
    second = analyze_source(rendered, "src/widget.py").value
    assert second.missing_count() == 0


def test_indentation_is_correct_for_nested_method() -> None:
    report, proposals = _proposals_for(SOURCE, "src/widget.py")
    rendered = render_documented_source(SOURCE, proposals).value
    lines = rendered.splitlines()
    # Find the method docstring line and assert 8-space indent (method body).
    method_doc = [ln for ln in lines if "Summary for Widget.area." in ln][0]
    assert method_doc.startswith('        """')


def test_multiline_docstring_renders() -> None:
    target = DocTarget(
        qualified_name="add",
        kind=DocKind.FUNCTION,
        signature="def add(x, y)",
        source_snippet="",
        start_line=4,
        end_line=5,
        file_path="src/widget.py",
    )
    proposal = DocProposal(
        target=target,
        docstring="Add two numbers.\n\nArgs:\n    x: first\n    y: second",
    )
    rendered = render_documented_source(SOURCE, [proposal]).value
    tree = ast.parse(rendered)
    docs = _docstrings(tree)
    assert docs["add"].startswith("Add two numbers.")
    assert "Args:" in docs["add"]


def test_build_pr_produces_branch_title_body() -> None:
    report, proposals = _proposals_for(SOURCE, "src/widget.py")
    branch, title, body = build_pr(report, proposals)
    assert branch.startswith("docagent/docstrings-")
    assert "src/widget.py" in title
    assert "Documented" in body
    for p in proposals:
        assert p.target.qualified_name in body


def test_build_pr_is_deterministic() -> None:
    report, proposals = _proposals_for(SOURCE, "src/widget.py")
    b1, _, _ = build_pr(report, proposals)
    b2, _, _ = build_pr(report, proposals)
    assert b1 == b2


def test_render_bad_source_returns_err() -> None:
    empty_report = AnalysisReport(file_path="x.py")
    result = render_documented_source("def broken(:\n", [])
    assert result.is_err()
