from __future__ import annotations

from typing import Any, Dict, List

from docagent.ports.repo import FileChange, RepoPublisher
from docagent.tools._tooling import tool


def _error(message: str) -> Dict[str, Any]:
    return {"status": "error", "message": message}


def _ok(**payload: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {"status": "success"}
    result.update(payload)
    return result


class RepoTools:
    """GitHub tools sharing a :class:`RepoPublisher`.

    The publisher (fake in tests, GitHub REST adapter in production) is injected
    once and reused. Each method is a Strands ``@tool`` returning a structured
    ``{"status": ...}`` dict and never raising into the agent loop.
    """

    def __init__(self, publisher: RepoPublisher, base_branch: str) -> None:
        self._publisher = publisher
        self._base_branch = base_branch

    @tool
    def list_python_files(self) -> Dict[str, Any]:
        """List the Python files in the target repository.

        Returns:
            On success, ``{"status": "success", "files": [path, ...]}``; on
            failure, ``{"status": "error", "message"}``.
        """
        result = self._publisher.list_python_files(self._base_branch)
        if result.is_err():
            return _error("could not list repository files")
        return _ok(files=list(result.value))

    @tool
    def read_source_file(self, path: str) -> Dict[str, Any]:
        """Read a single source file from the target repository.

        Args:
            path: Repository-relative path to read.

        Returns:
            On success, ``{"status": "success", "path", "content", "sha"}``; on
            failure, ``{"status": "error", "message"}``.
        """
        result = self._publisher.read_file(path, self._base_branch)
        if result.is_err():
            return _error("could not read " + path)
        f = result.value
        return _ok(path=f.path, content=f.content, sha=f.sha)

    @tool
    def open_documentation_pr(
        self,
        branch: str,
        title: str,
        body: str,
        changes: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Open a pull request containing documentation changes.

        Creates ``branch`` from the base branch, commits each change, and opens a
        pull request against the base branch. Never writes to the base branch
        directly.

        Args:
            branch: Head branch name to create for the changes.
            title: Pull request title.
            body: Pull request description (Markdown).
            changes: List of ``{"path", "content", "sha"?}`` file changes. ``sha``
                is required only when updating an existing file.

        Returns:
            On success, ``{"status": "success", "pr_number", "pr_url", "branch"}``;
            on failure, ``{"status": "error", "message"}``.
        """
        file_changes = [
            FileChange(
                path=c["path"],
                content=c["content"],
                sha=c.get("sha", ""),
            )
            for c in changes
        ]
        result = self._publisher.open_pull_request(
            branch=branch,
            base=self._base_branch,
            title=title,
            body=body,
            changes=file_changes,
        )
        if result.is_err():
            return _error("could not open pull request")
        pr = result.value
        return _ok(pr_number=pr.number, pr_url=pr.url, branch=pr.branch)
