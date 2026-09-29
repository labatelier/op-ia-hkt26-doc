from __future__ import annotations

import pytest

from docagent.app import InvalidPromptError, extract_prompt


def test_extract_valid_prompt() -> None:
    assert extract_prompt({"prompt": "document the repo"}) == "document the repo"


def test_missing_prompt_rejected() -> None:
    with pytest.raises(InvalidPromptError):
        extract_prompt({})


def test_non_string_prompt_rejected() -> None:
    with pytest.raises(InvalidPromptError):
        extract_prompt({"prompt": 123})


def test_empty_prompt_rejected() -> None:
    with pytest.raises(InvalidPromptError):
        extract_prompt({"prompt": "   "})
