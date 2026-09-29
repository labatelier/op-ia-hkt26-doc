# Requirements — Documentation Agent

Context: Onepoint × AWS "Build your AI agent with Kiro" hackathon (2026-09-29, Bordeaux).
Workshop: **Documentation Agent**. Target runtime: **Amazon Bedrock AgentCore**.

## Introduction

Codebases accumulate documentation debt: functions, classes, and modules without
docstrings. This spec defines an AI agent, deployable on Amazon Bedrock AgentCore,
that reads Python source from a GitHub repository, detects symbols missing
docstrings, generates high-quality docstrings via a Bedrock model, and opens a
GitHub Pull Request with the changes. The Pull Request is the human-in-the-loop
approval gate — a human reviews and merges. The architecture must be extensible so
README generation and documentation-drift detection can be added later as
additional agent tools without reworking existing code.

## Confirmed decisions

| Decision | Choice |
| --- | --- |
| Hero feature | Docstring generation, architected for future features |
| Code access & publishing | GitHub REST API directly, via a `RepoPublisher` port/adapter |
| Human-in-the-loop | GitHub Pull Requests (agent never writes to the default branch) |
| File access mode | Fully remote (via GitHub REST API), no local clone dependency |
| PR granularity | Configurable, default one PR per run |
| Orchestration | Amazon Bedrock AgentCore SDK + Strands `Agent` |
| Model | Claude on Bedrock (already enabled) |
| Code analysis | Python stdlib `ast` |
| Target repository | This codebase (`op-ia-hkt26-doc`) on GitHub |
| Build order | Agent logic first (offline-testable), AgentCore deployment last |

## Requirements

### Requirement 1 — Detect missing docstrings (hero feature)

**User Story:** As a developer, I want the agent to find Python functions, classes,
and modules that lack docstrings, so that I know where documentation is missing.

#### Acceptance Criteria

1. WHEN given valid Python source THEN the agent SHALL parse it with the stdlib
   `ast` module and identify every module, class, and function definition.
2. WHEN a definition has no docstring THEN the agent SHALL flag it as a target,
   recording its qualified name, kind (module/class/function), signature, source
   snippet, and line range.
3. WHEN a definition already has a docstring THEN the agent SHALL NOT flag it.
4. IF the source is syntactically invalid THEN the agent SHALL return a structured
   error and SHALL NOT crash.

### Requirement 2 — Generate docstrings via Bedrock

**User Story:** As a developer, I want the agent to write clear docstrings for the
flagged symbols, so that documentation matches the code.

#### Acceptance Criteria

1. WHEN a target is identified THEN the agent SHALL generate a docstring using a
   Claude model on Amazon Bedrock.
2. WHEN generating THEN the agent SHALL provide the target's signature and source
   context to the model.
3. WHEN a docstring is generated THEN it SHALL be valid for insertion (PEP 257
   style) such that the resulting source re-parses successfully.
4. WHERE the generator is invoked in tests THE agent SHALL support a deterministic
   fake generator so the pipeline runs fully offline without AWS.

### Requirement 3 — Publish changes as a GitHub Pull Request (human-in-the-loop)

**User Story:** As a reviewer, I want proposed docstrings delivered as a Pull
Request, so that I can review, approve, and merge them through GitHub.

#### Acceptance Criteria

1. WHEN documentation changes are ready THEN the agent SHALL create a new branch,
   commit the changes, and open a Pull Request against the default branch.
2. The agent SHALL NOT commit or push directly to the default branch.
3. WHEN opening a Pull Request THEN the agent SHALL produce a descriptive title and
   a body listing the documented symbols.
4. The agent SHALL access GitHub exclusively through the GitHub REST API,
   authenticated with a Bearer PAT, behind a `RepoPublisher` port so the
   implementation can be swapped (real REST adapter for live, fake for tests).
5. The REST adapter SHALL use only the endpoints required to read source and open
   a pull request: get repository tree/contents, get/create git refs (branches),
   create/update file contents (commits), and create a pull request.

### Requirement 4 — Fully remote file access

**User Story:** As an operator, I want the agent to read source directly from
GitHub, so that it does not depend on a local checkout and runs cleanly inside
AgentCore.

#### Acceptance Criteria

1. WHEN the agent needs source THEN it SHALL read file contents and repository
   structure via the GitHub REST API (repository tree and file contents endpoints).
2. The agent SHALL NOT require a local clone of the repository to operate.

### Requirement 5 — Configurable PR granularity

**User Story:** As an operator, I want to control how many Pull Requests a run
produces, so that reviews stay manageable.

#### Acceptance Criteria

1. The agent SHALL default to one Pull Request per run covering all documented files.
2. WHERE configured for per-file granularity THE agent SHALL open one Pull Request
   per documented file.

### Requirement 6 — Amazon Bedrock AgentCore deployment

**User Story:** As an operator, I want to deploy the agent to Amazon Bedrock
AgentCore, so that it runs as a managed, scalable service.

#### Acceptance Criteria

1. The agent SHALL expose a `BedrockAgentCoreApp` entrypoint compatible with
   AgentCore Runtime (`POST /invocations`).
2. WHEN invoked THEN the entrypoint SHALL validate that the request `prompt` is a
   string before forwarding it to the agent.
3. WHEN a valid prompt is received THEN the entrypoint SHALL stream agent events.
4. The agent logic SHALL be buildable and testable offline (fake `RepoPublisher` +
   fake LLM) before any AgentCore deployment.

### Requirement 7 — Extensibility ("ready for all features")

**User Story:** As a maintainer, I want to add README generation and drift
detection later, so that the agent grows without rework.

#### Acceptance Criteria

1. Each capability SHALL be implemented as a discrete Strands `@tool`.
2. WHEN a new capability tool is added THEN it SHALL be registered in the agent
   builder WITHOUT modifying existing tools or the GitHub REST adapter.
3. External integrations (LLM, GitHub) SHALL sit behind ports/adapters so
   implementations can be swapped (e.g., fake for tests, Bedrock/GitHub for live).

### Requirement 8 — Follow existing repository conventions

**User Story:** As a maintainer of this codebase, I want the agent to match our
existing patterns, so that it integrates cleanly.

#### Acceptance Criteria

1. Domain logic SHALL use the existing `Result[T, E]` type and typed `DomainError`
   hierarchy for outcomes and errors.
2. Modules SHALL use `from __future__ import annotations` and frozen dataclasses for
   value objects, consistent with `src/common` and `src/npd`.
3. The package SHALL live under the `src/` layout and be testable with `pytest`.
4. Logging SHALL use the existing injected `StructuredLogger` pattern where logging
   is needed.

### Requirement 9 — Security and safety

**User Story:** As an operator, I want the agent to behave safely with credentials
and repository access, so that it is safe to run.

#### Acceptance Criteria

1. Custom tools SHALL return structured `{"status": "error", ...}` results rather
   than raising unhandled exceptions.
2. The GitHub PAT SHALL be provided via environment variable / secret and SHALL NOT
   be hardcoded or logged.
3. The deployment SHALL follow least privilege: a `repo`-scoped PAT and a
   least-privilege IAM policy for Bedrock model invocation.
