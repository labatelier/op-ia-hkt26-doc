from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


class DocKind(Enum):
    """Kind of Python definition that can carry a docstring."""

    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()


@dataclass(frozen=True)
class DocTarget:
    """A definition that is missing a docstring.

    Attributes:
        qualified_name: Dotted path to the definition (e.g. ``Account.credit``).
            The module target uses ``<module>`` as its name.
        kind: Whether the target is a module, class, or function.
        signature: The reconstructed signature for functions, the ``class``
            header for classes, or an empty string for modules.
        source_snippet: The source text of the definition, used to give the
            language model enough context to write an accurate docstring.
        start_line: 1-based line where the definition begins.
        end_line: 1-based line where the definition ends.
        file_path: Repository-relative path of the file the target lives in.
    """

    qualified_name: str
    kind: DocKind
    signature: str
    source_snippet: str
    start_line: int
    end_line: int
    file_path: str


@dataclass(frozen=True)
class DocProposal:
    """A generated docstring paired with the target it documents.

    Attributes:
        target: The definition the docstring was generated for.
        docstring: The raw docstring text WITHOUT surrounding quotes or
            indentation; rendering is responsible for placing it correctly.
    """

    target: DocTarget
    docstring: str


@dataclass(frozen=True)
class AnalysisReport:
    """The result of analysing a single source file for missing docstrings.

    Attributes:
        file_path: Repository-relative path of the analysed file.
        targets: Definitions found to be missing a docstring.
    """

    file_path: str
    targets: Tuple[DocTarget, ...] = field(default_factory=tuple)

    def missing_count(self) -> int:
        """Return the number of definitions missing a docstring."""
        return len(self.targets)

    def has_missing(self) -> bool:
        """Return ``True`` when at least one definition needs a docstring."""
        return len(self.targets) > 0
