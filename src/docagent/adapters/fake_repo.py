from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from common.codes import ErrorCode
from common.errors import DomainError
from common.result import Result, err, ok

from docagent.ports.repo import FileChange, PullRequest, RepoFile


class FakePublisher:
    """In-memory :class:`~docagent.ports.repo.RepoPublisher` for tests.

    Seeded with a mapping of path -> source content. Records opened pull requests
    and returns a deterministic fake PR URL so the whole publish flow can run
    offline.
    """

    def __init__(self, files: Dict[str, str]) -> None:
        self._files = dict(files)
        self.opened: List[Dict[str, object]] = []
        self._next_number = 1

    def list_python_files(self, ref: str) -> Result[Tuple[str, ...], DomainError]:
        """Return the seeded Python file paths."""
        paths = tuple(p for p in sorted(self._files) if p.endswith(".py"))
        return ok(paths)

    def read_file(self, path: str, ref: str) -> Result[RepoFile, DomainError]:
        """Return the seeded content for ``path`` or a NOT_FOUND error."""
        if path not in self._files:
            return err(DomainError(ErrorCode.NOT_FOUND.value))
        return ok(RepoFile(path=path, content=self._files[path], sha="fakesha-" + path))

    def open_pull_request(
        self,
        branch: str,
        base: str,
        title: str,
        body: str,
        changes: Sequence[FileChange],
    ) -> Result[PullRequest, DomainError]:
        """Record the pull request and return a deterministic fake PR."""
        number = self._next_number
        self._next_number += 1
        self.opened.append(
            {
                "branch": branch,
                "base": base,
                "title": title,
                "body": body,
                "changes": list(changes),
            }
        )
        # Apply changes to the in-memory store so re-reads reflect them.
        for change in changes:
            self._files[change.path] = change.content
        url = "https://github.com/fake/fake/pull/" + str(number)
        return ok(PullRequest(number=number, url=url, branch=branch))
