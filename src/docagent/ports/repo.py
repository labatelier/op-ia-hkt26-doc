from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, Tuple, runtime_checkable

from common.errors import DomainError
from common.result import Result


@dataclass(frozen=True)
class RepoFile:
    """A file read from the repository.

    Attributes:
        path: Repository-relative path.
        content: Decoded UTF-8 text content.
        sha: The blob SHA GitHub reports for the file; required when updating it.
    """

    path: str
    content: str
    sha: str


@dataclass(frozen=True)
class FileChange:
    """A single file to write in a documentation commit.

    Attributes:
        path: Repository-relative path to create or update.
        content: Full new content of the file.
        sha: Existing blob SHA when updating an existing file, or an empty
            string when creating a new file.
    """

    path: str
    content: str
    sha: str = ""


@dataclass(frozen=True)
class PullRequest:
    """A pull request opened by the agent.

    Attributes:
        number: The pull request number.
        url: The HTML URL a reviewer can open.
        branch: The head branch containing the changes.
    """

    number: int
    url: str
    branch: str


@runtime_checkable
class RepoPublisher(Protocol):
    """Port for reading source from and publishing changes to a repository.

    The concrete adapter (GitHub REST API) is responsible for all network I/O.
    Domain code and tools depend only on this protocol so a fake can be
    substituted in tests.
    """

    def list_python_files(self, ref: str) -> Result[Tuple[str, ...], DomainError]:
        """List repository-relative paths of Python files on ``ref``."""
        ...

    def read_file(self, path: str, ref: str) -> Result[RepoFile, DomainError]:
        """Read a single file at ``path`` on ``ref``."""
        ...

    def open_pull_request(
        self,
        branch: str,
        base: str,
        title: str,
        body: str,
        changes: Sequence[FileChange],
    ) -> Result[PullRequest, DomainError]:
        """Create ``branch`` from ``base``, commit ``changes``, and open a PR.

        Implementations MUST NOT write to ``base`` directly; all changes land on
        ``branch`` and are surfaced through the returned pull request.
        """
        ...
