from __future__ import annotations

import ast

from docagent.adapters.fake_llm import FakeDocGenerator
from docagent.tools.docstring_tools import DocstringTools

SOURCE = '''def add(a, b):
    return a + b


class Box:
    def open(self):
        return True
'''


def _tools() -> DocstringTools:
    return DocstringTools(FakeDocGenerator())


def test_analyze_reports_targets() -> None:
    out = _tools().analyze_python_source("src/m.py", SOURCE)
    assert out["status"] == "success"
    assert out["missing_count"] >= 3
    names = {t["qualified_name"] for t in out["targets"]}
    assert "add" in names
    assert "Box" in names
    assert "Box.open" in names


def test_analyze_error_on_bad_source() -> None:
    out = _tools().analyze_python_source("src/bad.py", "def broken(:\n")
    assert out["status"] == "error"
    assert "bad.py" in out["message"]


def test_generate_returns_proposals() -> None:
    out = _tools().generate_docstrings("src/m.py", SOURCE)
    assert out["status"] == "success"
    assert len(out["proposals"]) >= 3
    for p in out["proposals"]:
        assert p["docstring"].strip() != ""


def test_render_produces_valid_documented_source() -> None:
    out = _tools().render_documented_source("src/m.py", SOURCE)
    assert out["status"] == "success"
    assert out["documented_count"] >= 3
    # Rendered content parses and every def/class now has a docstring.
    tree = ast.parse(out["content"])
    func = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "add"][0]
    assert ast.get_docstring(func) is not None
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Box"][0]
    assert ast.get_docstring(cls) is not None


def test_render_error_on_bad_source() -> None:
    out = _tools().render_documented_source("src/bad.py", "class X(:\n")
    assert out["status"] == "error"


def test_render_no_targets_returns_source_unchanged() -> None:
    documented = '"""Module."""\n\n\ndef f():\n    """Doc."""\n    return 1\n'
    out = _tools().render_documented_source("src/ok.py", documented)
    assert out["status"] == "success"
    assert out["documented_count"] == 0
    assert out["content"] == documented
