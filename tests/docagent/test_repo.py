from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional

from docagent.adapters.fake_repo import FakePublisher
from docagent.adapters.github_api import GitHubApiPublisher
from docagent.ports.repo import FileChange, RepoPublisher
from docagent.tools.repo_tools import RepoTools


class RecordingOpener:
    """Stub URL opener that records requests and returns queued responses."""

    def __init__(self, responses: List[Any]) -> None:
        self._responses = list(responses)
        self.calls: List[Dict[str, Any]] = []

    def __call__(
        self,
        url: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[bytes],
    ) -> Any:
        parsed = json.loads(body.decode("utf-8")) if body else None
        self.calls.append(
            {"url": url, "method": method, "headers": headers, "body": parsed}
        )
        return self._responses.pop(0)


# -- FakePublisher + RepoTools ------------------------------------------------


def test_fake_conforms_to_protocol() -> None:
    assert isinstance(FakePublisher({}), RepoPublisher)


def test_repo_tools_list_and_read() -> None:
    pub = FakePublisher({"src/a.py": "x = 1\n", "README.md": "# hi\n"})
    tools = RepoTools(pub, base_branch="main")

    listed = tools.list_python_files()
    assert listed["status"] == "success"
    assert listed["files"] == ["src/a.py"]

    read = tools.read_source_file("src/a.py")
    assert read["status"] == "success"
    assert read["content"] == "x = 1\n"

    missing = tools.read_source_file("nope.py")
    assert missing["status"] == "error"


def test_repo_tools_open_pr_records_and_returns_url() -> None:
    pub = FakePublisher({"src/a.py": "x = 1\n"})
    tools = RepoTools(pub, base_branch="main")
    out = tools.open_documentation_pr(
        branch="docagent/docstrings-abc",
        title="docs: add docstrings",
        body="body",
        changes=[{"path": "src/a.py", "content": "x = 1  # documented\n", "sha": "s"}],
    )
    assert out["status"] == "success"
    assert out["pr_url"].endswith("/pull/1")
    assert out["branch"] == "docagent/docstrings-abc"
    assert len(pub.opened) == 1
    assert pub.opened[0]["base"] == "main"


# -- GitHubApiPublisher REST request building ---------------------------------


def test_list_python_files_uses_tree_api() -> None:
    opener = RecordingOpener(
        [
            {
                "tree": [
                    {"type": "blob", "path": "src/a.py"},
                    {"type": "blob", "path": "README.md"},
                    {"type": "tree", "path": "src"},
                ]
            }
        ]
    )
    pub = GitHubApiPublisher("owner", "repo", "tok", opener=opener)
    result = pub.list_python_files("main")
    assert result.is_ok()
    assert result.value == ("src/a.py",)
    call = opener.calls[0]
    assert call["method"] == "GET"
    assert call["url"].endswith("/repos/owner/repo/git/trees/main?recursive=1")
    assert call["headers"]["Authorization"] == "Bearer tok"


def test_read_file_decodes_base64() -> None:
    encoded = base64.b64encode(b"hello = 1\n").decode("ascii")
    opener = RecordingOpener([{"content": encoded, "sha": "abc123"}])
    pub = GitHubApiPublisher("owner", "repo", "tok", opener=opener)
    result = pub.read_file("src/a.py", "main")
    assert result.is_ok()
    assert result.value.content == "hello = 1\n"
    assert result.value.sha == "abc123"


def test_open_pull_request_full_sequence() -> None:
    # Responses in order: resolve base sha, create branch, put file, create PR.
    opener = RecordingOpener(
        [
            {"object": {"sha": "basesha"}},
            {"ref": "refs/heads/feature"},
            {"content": {}},
            {"number": 42, "html_url": "https://github.com/owner/repo/pull/42"},
        ]
    )
    pub = GitHubApiPublisher("owner", "repo", "tok", opener=opener)
    result = pub.open_pull_request(
        branch="feature",
        base="main",
        title="docs",
        body="body",
        changes=[FileChange(path="src/a.py", content="documented\n", sha="oldsha")],
    )
    assert result.is_ok()
    pr = result.value
    assert pr.number == 42
    assert pr.url.endswith("/pull/42")

    methods = [c["method"] for c in opener.calls]
    assert methods == ["GET", "POST", "PUT", "POST"]

    # Branch creation references the resolved base sha.
    assert opener.calls[1]["body"] == {"ref": "refs/heads/feature", "sha": "basesha"}
    # File content is base64-encoded and includes the existing sha for update.
    put_body = opener.calls[2]["body"]
    assert put_body["sha"] == "oldsha"
    assert base64.b64decode(put_body["content"]).decode("utf-8") == "documented\n"
    assert put_body["branch"] == "feature"
    # PR targets the base branch.
    pr_body = opener.calls[3]["body"]
    assert pr_body["head"] == "feature"
    assert pr_body["base"] == "main"


def test_never_writes_to_base_branch() -> None:
    opener = RecordingOpener(
        [
            {"object": {"sha": "basesha"}},
            {"ref": "refs/heads/feature"},
            {"content": {}},
            {"number": 1, "html_url": "u"},
        ]
    )
    pub = GitHubApiPublisher("owner", "repo", "tok", opener=opener)
    pub.open_pull_request(
        branch="feature",
        base="main",
        title="t",
        body="b",
        changes=[FileChange(path="a.py", content="c\n")],
    )
    # The PUT that commits the file must target the feature branch, never main.
    put_body = opener.calls[2]["body"]
    assert put_body["branch"] == "feature"
