from __future__ import annotations

import dataclasses

import pytest

from docagent.domain.models import (
    AnalysisReport,
    DocKind,
    DocProposal,
    DocTarget,
)


def _target(name: str = "foo", kind: DocKind = DocKind.FUNCTION) -> DocTarget:
    return DocTarget(
        qualified_name=name,
        kind=kind,
        signature="def foo(x: int) -> int",
        source_snippet="def foo(x):\n    return x",
        start_line=1,
        end_line=2,
        file_path="src/mod.py",
    )


def test_dockind_members() -> None:
    assert {k.name for k in DocKind} == {"MODULE", "CLASS", "FUNCTION"}


def test_doctarget_fields() -> None:
    t = _target()
    assert t.qualified_name == "foo"
    assert t.kind is DocKind.FUNCTION
    assert t.start_line == 1
    assert t.end_line == 2
    assert t.file_path == "src/mod.py"


def test_doctarget_is_frozen() -> None:
    t = _target()
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.qualified_name = "bar"  # type: ignore[misc]


def test_docproposal_pairs_target_and_text() -> None:
    t = _target()
    p = DocProposal(target=t, docstring="Return x unchanged.")
    assert p.target is t
    assert p.docstring == "Return x unchanged."
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.docstring = "changed"  # type: ignore[misc]


def test_analysis_report_counts() -> None:
    empty = AnalysisReport(file_path="src/mod.py")
    assert empty.missing_count() == 0
    assert empty.has_missing() is False

    report = AnalysisReport(
        file_path="src/mod.py",
        targets=(_target("a"), _target("b", DocKind.CLASS)),
    )
    assert report.missing_count() == 2
    assert report.has_missing() is True
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.file_path = "other.py"  # type: ignore[misc]
