from __future__ import annotations

import ast
from typing import List, Optional

from common.codes import ErrorCode
from common.errors import DomainError
from common.result import Result, err, ok

from docagent.domain.models import AnalysisReport, DocKind, DocTarget

_FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


def analyze_source(source: str, file_path: str) -> Result[AnalysisReport, DomainError]:
    """Analyse Python source and report definitions missing docstrings.

    The module itself, every class, and every function/method (including nested
    and async definitions) are inspected. A definition is reported when
    :func:`ast.get_docstring` returns ``None``.

    Args:
        source: The full text of a Python source file.
        file_path: Repository-relative path used to label the report and the
            resulting targets.

    Returns:
        ``ok(AnalysisReport)`` with one :class:`DocTarget` per undocumented
        definition, or ``err(DomainError)`` with
        :attr:`ErrorCode.PARSE_ERROR` when the source cannot be parsed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return err(DomainError(ErrorCode.PARSE_ERROR.value))

    lines = source.splitlines()
    targets: List[DocTarget] = []

    if ast.get_docstring(tree) is None and _module_has_body(tree):
        targets.append(
            DocTarget(
                qualified_name="<module>",
                kind=DocKind.MODULE,
                signature="",
                source_snippet=_module_snippet(lines),
                start_line=1,
                end_line=len(lines),
                file_path=file_path,
            )
        )

    targets.extend(_walk(tree.body, lines, file_path, prefix=""))
    return ok(AnalysisReport(file_path=file_path, targets=tuple(targets)))


def _module_has_body(tree: ast.Module) -> bool:
    return any(
        not isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body
    )


def _module_snippet(lines: List[str], limit: int = 40) -> str:
    return "\n".join(lines[:limit])


def _walk(
    body: List[ast.stmt],
    lines: List[str],
    file_path: str,
    prefix: str,
) -> List[DocTarget]:
    found: List[DocTarget] = []
    for node in body:
        if isinstance(node, ast.ClassDef):
            found.extend(_handle_class(node, lines, file_path, prefix))
        elif isinstance(node, _FUNCTION_NODES):
            found.extend(_handle_function(node, lines, file_path, prefix))
    return found


def _handle_class(
    node: ast.ClassDef,
    lines: List[str],
    file_path: str,
    prefix: str,
) -> List[DocTarget]:
    qualified = _join(prefix, node.name)
    found: List[DocTarget] = []
    if ast.get_docstring(node) is None:
        found.append(
            DocTarget(
                qualified_name=qualified,
                kind=DocKind.CLASS,
                signature=_class_signature(node),
                source_snippet=_snippet(node, lines),
                start_line=node.lineno,
                end_line=_end_line(node, lines),
                file_path=file_path,
            )
        )
    found.extend(_walk(node.body, lines, file_path, prefix=qualified))
    return found


def _handle_function(
    node: ast.stmt,
    lines: List[str],
    file_path: str,
    prefix: str,
) -> List[DocTarget]:
    qualified = _join(prefix, node.name)
    found: List[DocTarget] = []
    if ast.get_docstring(node) is None:
        found.append(
            DocTarget(
                qualified_name=qualified,
                kind=DocKind.FUNCTION,
                signature=_function_signature(node),
                source_snippet=_snippet(node, lines),
                start_line=node.lineno,
                end_line=_end_line(node, lines),
                file_path=file_path,
            )
        )
    # Recurse to catch nested functions and methods.
    found.extend(_walk(node.body, lines, file_path, prefix=qualified))
    return found


def _join(prefix: str, name: str) -> str:
    if prefix == "":
        return name
    return prefix + "." + name


def _class_signature(node: ast.ClassDef) -> str:
    bases = [ast.unparse(base) for base in node.bases]
    keywords = [ast.unparse(kw) for kw in node.keywords]
    parts = bases + keywords
    if parts:
        return "class " + node.name + "(" + ", ".join(parts) + ")"
    return "class " + node.name


def _function_signature(node: ast.stmt) -> str:
    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    args = ast.unparse(node.args)
    returns = ""
    if node.returns is not None:
        returns = " -> " + ast.unparse(node.returns)
    return prefix + node.name + "(" + args + ")" + returns


def _snippet(node: ast.stmt, lines: List[str], limit: int = 60) -> str:
    start = node.lineno - 1
    end = _end_line(node, lines)
    return "\n".join(lines[start : min(end, start + limit)])


def _end_line(node: ast.stmt, lines: List[str]) -> int:
    end: Optional[int] = getattr(node, "end_lineno", None)
    if end is not None:
        return end
    return node.lineno
