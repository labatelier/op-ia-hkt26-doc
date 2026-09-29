from __future__ import annotations

from docagent.domain.analyzer import analyze_source
from docagent.domain.models import DocKind

DOCUMENTED = '''"""Module docstring."""


class Documented:
    """A documented class."""

    def method(self) -> None:
        """A documented method."""
        return None


def free_function() -> int:
    """A documented function."""
    return 1
'''

MIXED = '''import os


def undocumented(x, y):
    return x + y


class Widget:
    def __init__(self, size):
        self.size = size

    def resize(self, factor: float) -> "Widget":
        """Return a resized widget."""
        return Widget(self.size * factor)
'''


def _names(report):
    return {t.qualified_name for t in report.targets}


def test_all_documented_reports_nothing() -> None:
    result = analyze_source(DOCUMENTED, "src/mod.py")
    assert result.is_ok()
    assert result.value.missing_count() == 0
    assert result.value.has_missing() is False


def test_mixed_flags_only_undocumented() -> None:
    result = analyze_source(MIXED, "src/widget.py")
    assert result.is_ok()
    report = result.value
    names = _names(report)
    # Module has real (non-import) body and no docstring -> flagged.
    assert "<module>" in names
    assert "undocumented" in names
    assert "Widget" in names
    assert "Widget.__init__" in names
    # The documented method must NOT be flagged.
    assert "Widget.resize" not in names


def test_kinds_are_correct() -> None:
    report = analyze_source(MIXED, "src/widget.py").value
    by_name = {t.qualified_name: t for t in report.targets}
    assert by_name["<module>"].kind is DocKind.MODULE
    assert by_name["undocumented"].kind is DocKind.FUNCTION
    assert by_name["Widget"].kind is DocKind.CLASS
    assert by_name["Widget.__init__"].kind is DocKind.FUNCTION


def test_signature_and_lines_captured() -> None:
    report = analyze_source(MIXED, "src/widget.py").value
    by_name = {t.qualified_name: t for t in report.targets}
    fn = by_name["undocumented"]
    assert fn.signature == "def undocumented(x, y)"
    assert fn.start_line == 4
    assert fn.end_line >= fn.start_line
    assert "return x + y" in fn.source_snippet
    cls = by_name["Widget"]
    assert cls.signature == "class Widget"


def test_invalid_source_returns_err() -> None:
    result = analyze_source("def broken(:\n    pass\n", "src/bad.py")
    assert result.is_err()
    from common.codes import ErrorCode

    assert result.error.code == ErrorCode.PARSE_ERROR.value


def test_module_with_only_imports_not_flagged() -> None:
    result = analyze_source("import os\nimport sys\n", "src/imports.py")
    assert result.is_ok()
    assert "<module>" not in {t.qualified_name for t in result.value.targets}
