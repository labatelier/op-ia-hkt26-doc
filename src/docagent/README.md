# Documentation Agent

An AI agent, deployable on **Amazon Bedrock AgentCore**, that reads Python source
from a GitHub repository, detects definitions missing docstrings (via `ast`),
generates docstrings with a Claude model on Bedrock, and opens a **pull request**
with the changes for human review. The pull request is the human-in-the-loop
approval gate.

Built for the Onepoint × AWS "Build your AI agent with Kiro" hackathon. See the
full spec under `.kiro/specs/documentation-agent/`.

## Architecture

Layered / hexagonal:

- `domain/` — pure logic: models, `ast` analyzer, docstring rendering + PR text.
- `ports/` — `DocGenerator` (LLM) and `RepoPublisher` (GitHub) protocols.
- `adapters/` — `BedrockDocGenerator`, `GitHubApiPublisher` (REST, stdlib only),
  plus `FakeDocGenerator` / `FakePublisher` for offline tests.
- `tools/` — Strands `@tool`s: `list_python_files`, `read_source_file`,
  `analyze_python_source`, `generate_docstrings`, `render_documented_source`,
  `open_documentation_pr`.
- `agent.py` — assembles the Strands `Agent`.
- `app.py` — the AgentCore `BedrockAgentCoreApp` entrypoint.
- `main.py` — local CLI (`hkt-docagent`).

All GitHub access is via the GitHub REST API; there is no MCP dependency.

## Configuration (environment variables)

| Variable | Default | Purpose |
| --- | --- | --- |
| `DOCAGENT_MODEL_ID` | `us.anthropic.claude-sonnet-4-20250514-v1:0` | Bedrock model id |
| `DOCAGENT_REGION` | `eu-west-3` | AWS region for Bedrock |
| `DOCAGENT_REPO_OWNER` | _(empty)_ | GitHub owner |
| `DOCAGENT_REPO_NAME` | _(empty)_ | GitHub repo |
| `DOCAGENT_BASE_BRANCH` | `main` | Branch PRs target |
| `DOCAGENT_GITHUB_PAT_ENV` | `GITHUB_PAT` | Name of the env var holding the PAT |
| `DOCAGENT_ONE_PR_PER_RUN` | `true` | One PR per run vs. per file |

The GitHub PAT itself is read from the env var named by `DOCAGENT_GITHUB_PAT_ENV`
(default `GITHUB_PAT`). Use a least-privilege token with the `repo` scope.

## Install

```bash
pip install -e ".[agent]"   # installs strands-agents + bedrock-agentcore
```

## Run locally (CLI)

```bash
export GITHUB_PAT=...        # repo-scoped PAT
hkt-docagent --owner <owner> --repo <repo>
```

Requires AWS credentials with permission to invoke the configured Bedrock model.

## Deploy to Amazon Bedrock AgentCore

`app.py` exposes a `BedrockAgentCoreApp` with an `@app.entrypoint` handler that
validates the incoming `prompt` is a non-empty string and streams agent events.

```bash
# from the package directory, with the 'agent' extra installed
agentcore configure --entrypoint src/docagent/app.py
agentcore launch
```

Provide `GITHUB_PAT` (and the `DOCAGENT_*` settings) as environment/secret values
in the AgentCore configuration.

### Least-privilege notes

- **PAT:** `repo` scope only (Contents: read/write, Pull requests: read/write for a
  fine-grained token). The agent never writes to the base branch.
- **IAM:** grant the runtime role only `bedrock:InvokeModel` (and streaming) for the
  specific model ARN — avoid wildcard resources.

## Testing

The domain, tools, and adapters are fully unit-tested offline (fake LLM + fake
publisher, no network/AWS):

```bash
pytest tests/docagent
```
