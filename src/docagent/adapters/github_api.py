from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from common.codes import ErrorCode
from common.errors import DomainError
from common.result import Result, err, ok

from docagent.ports.repo import FileChange, PullRequest, RepoFile

# A URL opener takes (url, method, headers, body_bytes) and returns the decoded
# JSON response. Injectable so tests can stub out the network entirely.
Opener = Callable[[str, str, Dict[str, str], Optional[bytes]], Any]


class GitHubApiPublisher:
    """A :class:`~docagent.ports.repo.RepoPublisher` backed by the GitHub REST API.

    Uses only the Python standard library (:mod:`urllib.request`) so it adds no
    runtime dependency. All requests are authenticated with a bearer PAT and sent
    to the configured API base over HTTPS. The adapter never writes to the base
    branch: :meth:`open_pull_request` creates a new branch, commits changes to it,
    and opens a pull request.
    """

    def __init__(
        self,
        owner: str,
        repo: str,
        token: str,
        api_base: str = "https://api.github.com",
        opener: Optional[Opener] = None,
    ) -> None:
        self._owner = owner
        self._repo = repo
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._opener = opener if opener is not None else self._default_opener

    # -- RepoPublisher protocol -------------------------------------------------

    def list_python_files(self, ref: str) -> Result[Tuple[str, ...], DomainError]:
        """List repository-relative ``.py`` paths on ``ref`` via the git tree API."""
        url = self._repo_url("/git/trees/" + ref + "?recursive=1")
        response = self._get(url)
        if response.is_err():
            return err(response.error)
        tree = response.value.get("tree", [])
        paths = tuple(
            entry["path"]
            for entry in tree
            if entry.get("type") == "blob" and entry.get("path", "").endswith(".py")
        )
        return ok(paths)

    def read_file(self, path: str, ref: str) -> Result[RepoFile, DomainError]:
        """Read ``path`` at ``ref`` via the contents API (base64-decoded)."""
        url = self._repo_url("/contents/" + path + "?ref=" + ref)
        response = self._get(url)
        if response.is_err():
            return err(response.error)
        payload = response.value
        encoded = payload.get("content", "")
        try:
            content = base64.b64decode(encoded).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return err(DomainError(ErrorCode.UNKNOWN.value))
        return ok(RepoFile(path=path, content=content, sha=payload.get("sha", "")))

    def open_pull_request(
        self,
        branch: str,
        base: str,
        title: str,
        body: str,
        changes: Sequence[FileChange],
    ) -> Result[PullRequest, DomainError]:
        """Create ``branch`` from ``base``, commit ``changes``, and open a PR."""
        base_sha = self._resolve_ref_sha(base)
        if base_sha.is_err():
            return err(base_sha.error)

        created = self._create_branch(branch, base_sha.value)
        if created.is_err():
            return err(created.error)

        for change in changes:
            committed = self._put_file(change, branch, title)
            if committed.is_err():
                return err(committed.error)

        return self._create_pull_request(branch, base, title, body)

    # -- internal helpers -------------------------------------------------------

    def _resolve_ref_sha(self, base: str) -> Result[str, DomainError]:
        url = self._repo_url("/git/ref/heads/" + base)
        response = self._get(url)
        if response.is_err():
            return err(response.error)
        sha = response.value.get("object", {}).get("sha")
        if not sha:
            return err(DomainError(ErrorCode.NOT_FOUND.value))
        return ok(sha)

    def _create_branch(self, branch: str, sha: str) -> Result[Dict[str, Any], DomainError]:
        url = self._repo_url("/git/refs")
        payload = {"ref": "refs/heads/" + branch, "sha": sha}
        return self._request(url, "POST", payload)

    def _put_file(
        self,
        change: FileChange,
        branch: str,
        message: str,
    ) -> Result[Dict[str, Any], DomainError]:
        url = self._repo_url("/contents/" + change.path)
        encoded = base64.b64encode(change.content.encode("utf-8")).decode("ascii")
        payload: Dict[str, Any] = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }
        if change.sha:
            payload["sha"] = change.sha
        return self._request(url, "PUT", payload)

    def _create_pull_request(
        self,
        branch: str,
        base: str,
        title: str,
        body: str,
    ) -> Result[PullRequest, DomainError]:
        url = self._repo_url("/pulls")
        payload = {"title": title, "head": branch, "base": base, "body": body}
        response = self._request(url, "POST", payload)
        if response.is_err():
            return err(response.error)
        data = response.value
        return ok(
            PullRequest(
                number=data.get("number", 0),
                url=data.get("html_url", ""),
                branch=branch,
            )
        )

    def _repo_url(self, suffix: str) -> str:
        return self._api_base + "/repos/" + self._owner + "/" + self._repo + suffix

    def _get(self, url: str) -> Result[Any, DomainError]:
        return self._request(url, "GET", None)

    def _request(
        self,
        url: str,
        method: str,
        payload: Optional[Dict[str, Any]],
    ) -> Result[Any, DomainError]:
        headers = {
            "Authorization": "Bearer " + self._token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "docagent",
        }
        body: Optional[bytes] = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        try:
            data = self._opener(url, method, headers, body)
        except urllib.error.HTTPError as exc:
            code = ErrorCode.NOT_FOUND.value if exc.code == 404 else ErrorCode.UNAVAILABLE.value
            return err(DomainError(code))
        except urllib.error.URLError:
            return err(DomainError(ErrorCode.UNAVAILABLE.value))
        return ok(data)

    @staticmethod
    def _default_opener(
        url: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes],
    ) -> Any:
        request = urllib.request.Request(url=url, data=body, method=method)
        for key, value in headers.items():
            request.add_header(key, value)
        with urllib.request.urlopen(request) as response:  # noqa: S310 (https only)
            raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}
