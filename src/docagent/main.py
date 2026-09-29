from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from docagent.adapters.bedrock_llm import BedrockDocGenerator
from docagent.adapters.github_api import GitHubApiPublisher
from docagent.agent import build_agent
from docagent.config.settings import load_settings


def _parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="hkt-docagent",
        description="Run the Documentation Agent against a GitHub repository.",
    )
    parser.add_argument("--owner", help="GitHub repository owner")
    parser.add_argument("--repo", help="GitHub repository name")
    parser.add_argument(
        "--prompt",
        default="Document the Python files in the repository and open a pull request.",
        help="Instruction passed to the agent.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint for running the agent locally.

    Reads settings from the environment, resolves the GitHub PAT from the
    configured environment variable, wires the Bedrock generator and GitHub REST
    publisher into the agent, and runs it against the target repository.

    Args:
        argv: Optional argument list (defaults to ``sys.argv``).

    Returns:
        Process exit code: ``0`` on success, non-zero on configuration errors.
    """
    args = _parse_args(argv)
    settings = load_settings()

    owner = args.owner or settings.repo_owner
    repo = args.repo or settings.repo_name
    if not owner or not repo:
        print("error: repository owner/name required (--owner/--repo or env)", file=sys.stderr)
        return 2

    token = os.environ.get(settings.pat_env_var, "")
    if not token:
        print(
            "error: GitHub PAT not found in env var " + settings.pat_env_var,
            file=sys.stderr,
        )
        return 2

    generator = BedrockDocGenerator(model_id=settings.model_id, region=settings.region)
    publisher = GitHubApiPublisher(
        owner=owner,
        repo=repo,
        token=token,
        api_base=settings.github_api_base,
    )
    agent = build_agent(generator, publisher, settings)
    response = agent(args.prompt)
    print(response)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
