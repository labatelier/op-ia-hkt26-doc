from __future__ import annotations

import os
from typing import Any, AsyncIterator, Mapping

from docagent.adapters.bedrock_llm import BedrockDocGenerator
from docagent.adapters.github_api import GitHubApiPublisher
from docagent.agent import build_agent
from docagent.config.settings import DocAgentSettings, load_settings


class InvalidPromptError(ValueError):
    """Raised when the invocation payload does not carry a string prompt."""


def extract_prompt(request: Mapping[str, Any]) -> str:
    """Validate and extract the ``prompt`` from an invocation payload.

    Args:
        request: The JSON payload delivered to the entrypoint.

    Returns:
        The prompt string.

    Raises:
        InvalidPromptError: If ``prompt`` is missing or not a string.
    """
    prompt = request.get("prompt")
    if not isinstance(prompt, str) or prompt.strip() == "":
        raise InvalidPromptError("request 'prompt' must be a non-empty string")
    return prompt


def _build_default_agent(settings: DocAgentSettings) -> Any:
    token = os.environ.get(settings.pat_env_var, "")
    generator = BedrockDocGenerator(model_id=settings.model_id, region=settings.region)
    publisher = GitHubApiPublisher(
        owner=settings.repo_owner,
        repo=settings.repo_name,
        token=token,
        api_base=settings.github_api_base,
    )
    return build_agent(generator, publisher, settings)


def create_app(agent_factory: Any = None) -> Any:
    """Create the AgentCore application.

    Strands/AgentCore are optional dependencies imported lazily so this module is
    importable (and :func:`extract_prompt` unit-testable) without them.

    Args:
        agent_factory: Optional zero-arg callable returning an agent, used to
            inject a fake in tests. Defaults to building the real Bedrock + GitHub
            agent from settings.

    Returns:
        A configured ``BedrockAgentCoreApp`` with the entrypoint registered.
    """
    try:
        from bedrock_agentcore import BedrockAgentCoreApp  # type: ignore
    except Exception as exc:  # pragma: no cover - requires sdk absent
        raise RuntimeError(
            "bedrock-agentcore is required to create the app; install the 'agent' extra"
        ) from exc

    settings = load_settings()
    factory = agent_factory or (lambda: _build_default_agent(settings))
    app = BedrockAgentCoreApp()

    @app.entrypoint
    async def handler(request: Mapping[str, Any]) -> AsyncIterator[Any]:
        prompt = extract_prompt(request)
        agent = factory()
        async for event in agent.stream_async(prompt):
            yield event

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run()
