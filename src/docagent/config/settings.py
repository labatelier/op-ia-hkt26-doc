from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from common.config_base import EnvironmentReader, SettingsFactory
from common.enums import Severity


# Environment variable keys.
KEY_MODEL_ID = "DOCAGENT_MODEL_ID"
KEY_REGION = "DOCAGENT_REGION"
KEY_REPO_OWNER = "DOCAGENT_REPO_OWNER"
KEY_REPO_NAME = "DOCAGENT_REPO_NAME"
KEY_BASE_BRANCH = "DOCAGENT_BASE_BRANCH"
KEY_PAT_ENV = "DOCAGENT_GITHUB_PAT_ENV"
KEY_ONE_PR_PER_RUN = "DOCAGENT_ONE_PR_PER_RUN"

# Defaults.
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
DEFAULT_REGION = "eu-west-3"
DEFAULT_BASE_BRANCH = "main"
DEFAULT_PAT_ENV = "GITHUB_PAT"
GITHUB_API_BASE = "https://api.github.com"


@dataclass(frozen=True)
class DocAgentSettings:
    """Configuration for the Documentation Agent.

    Attributes:
        model_id: Bedrock model identifier used for docstring generation.
        region: AWS region hosting the Bedrock model.
        repo_owner: GitHub owner (user or organization) of the target repo.
        repo_name: GitHub repository name.
        base_branch: Branch pull requests are opened against.
        pat_env_var: Name of the environment variable holding the GitHub PAT.
            The token itself is never stored on the settings object.
        one_pr_per_run: When ``True`` a run produces a single pull request; when
            ``False`` the agent opens one pull request per documented file.
        github_api_base: Base URL for the GitHub REST API.
        log_threshold: Minimum severity emitted by the structured logger.
    """

    model_id: str
    region: str
    repo_owner: str
    repo_name: str
    base_branch: str
    pat_env_var: str
    one_pr_per_run: bool
    github_api_base: str = GITHUB_API_BASE
    log_threshold: Severity = Severity.INFO


def _build(reader: EnvironmentReader) -> DocAgentSettings:
    return DocAgentSettings(
        model_id=reader.optional(KEY_MODEL_ID, DEFAULT_MODEL_ID),
        region=reader.optional(KEY_REGION, DEFAULT_REGION),
        repo_owner=reader.optional(KEY_REPO_OWNER, ""),
        repo_name=reader.optional(KEY_REPO_NAME, ""),
        base_branch=reader.optional(KEY_BASE_BRANCH, DEFAULT_BASE_BRANCH),
        pat_env_var=reader.optional(KEY_PAT_ENV, DEFAULT_PAT_ENV),
        one_pr_per_run=reader.as_bool(KEY_ONE_PR_PER_RUN, True),
    )


def load_settings(source: Optional[Mapping[str, str]] = None) -> DocAgentSettings:
    """Load :class:`DocAgentSettings` from an environment mapping.

    Args:
        source: Optional mapping to read from; defaults to ``os.environ`` when
            omitted.

    Returns:
        A fully-populated, immutable settings object.
    """
    reader = EnvironmentReader(source)
    factory = SettingsFactory(_build)
    return factory.create(reader)
