# Tasks — Documentation Agent

Inside-out build order: pure domain → ports/adapters → custom tools → GitHub MCP
wiring → agent → AgentCore deploy. Tasks 1–7 are fully offline (fake LLM + fake MCP,
no network/AWS). Tasks 8–9 need Bedrock + a GitHub PAT. Task 10 is stretch.
Each task ends with a demoable increment.

- [ ] 1. Scaffolding + domain models
  - Create `src/docagent/` and `src/docagent/config/settings.py` following the
    existing `settings.py` pattern (model id, AWS region, repo `owner`/`name`,
    allowed MCP tool list, PAT env-var name, `one_pr_per_run` flag).
  - Add `domain/models.py`: `DocKind` (MODULE/CLASS/FUNCTION), `DocTarget`,
    `DocProposal`, `AnalysisReport` — frozen dataclasses, `from __future__ import
    annotations`.
  - Add deps to `pyproject.toml` (`strands-agents`, `bedrock-agentcore`) and a
    `docagent.main:main` script entry.
  - Create `tests/docagent/`.
  - _Test:_ construct each model; assert immutability and field values.
  - _Demo:_ `pytest tests/docagent/test_models.py` passes; models importable.
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 2. AST analyzer
  - Implement `domain/analyzer.py` `analyze_source(source, file_path) ->
    Result[AnalysisReport, DomainError]` using `ast` to flag module/class/function
    definitions missing docstrings, capturing signature/snippet/line range.
  - Invalid source returns `err(...)`.
  - _Test:_ fixtures with mixed documented/undocumented defs; assert exactly the
    undocumented ones are reported with correct kind/name/lines; invalid source
    returns `err`.
  - _Demo:_ run over real `src/common/money.py` content and print missing-docstring
    symbols.
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 8.1_

- [ ] 3. Rendering (docstring insertion + PR text)
  - Implement `domain/rendering.py` `render_documented_source(source, proposals) ->
    Result[str, DomainError]` (insert docstrings at correct indentation; output
    re-parses via `ast`) and `build_pr(report, proposals) -> (branch_name, title,
    body)`.
  - _Test:_ rendered output re-parses with docstrings present and correct
    indentation; PR body lists each symbol; branch name valid.
  - _Demo:_ print the documented version of a sample file plus the PR title/body.
  - _Requirements: 2.3, 3.3_

- [ ] 4. LLM port + fake adapter
  - Define `ports/llm.py` `DocGenerator` protocol:
    `generate_docstring(target) -> Result[str, DomainError]`.
  - Implement `adapters/fake_llm.py` returning deterministic PEP 257-style
    docstrings.
  - _Test:_ fake returns a well-formed docstring per target; conforms to protocol.
  - _Demo:_ offline end-to-end test — analyze → fake-generate → render — for
    `money.py`, printed. First full pipeline slice, no network.
  - _Requirements: 2.1, 2.2, 2.4, 7.3_

- [ ] 5. Custom docstring tools (`@tool`)
  - Implement `tools/docstring_tools.py`: `analyze_python_source`,
    `generate_docstrings`, `render_documented_source` — rich docstrings (they are
    the schemas), returning structured `{"status": "success"|"error", ...}` (never
    raise). Inject `DocGenerator` via a class-based tool holder.
  - _Test:_ call each tool directly with the fake generator; assert `analyze`
    reports targets, `render` output re-parses with docstrings; error path returns
    `status: error`.
  - _Demo:_ drive the three tools in sequence over sample source; show documented
    result + structured outputs.
  - _Requirements: 1.1, 2.1, 7.1, 9.1_

- [ ] 6. GitHub MCP client wiring (with fake for tests)
  - Implement `github_mcp.py` `build_github_mcp_client(pat, settings) -> MCPClient`
    using `streamablehttp_client("https://api.githubcopilot.com/mcp/",
    headers={"Authorization": f"Bearer {pat}"})` with
    `tool_filters={"allowed": settings.allowed_github_tools}`.
  - Add a `FakeMcpProvider` test double exposing stub GitHub tools returning canned
    responses (including a fake PR URL).
  - _Test:_ client constructed with expected URL/headers/filters (assert config, no
    live call); fake provider tools return canned values.
  - _Demo:_ (optional live) list filtered tools from the real MCP server if a PAT is
    present; otherwise show the fake provider's tool set.
  - _Requirements: 3.4, 3.5, 4.1, 4.2, 9.2, 9.3_

- [ ] 7. Assemble the Strands agent
  - Implement `agent.py` `build_agent(generator, github_provider, settings) ->
    Agent` constructing `Agent(model=<bedrock model id>, tools=[...custom...,
    github_provider], system_prompt=...)`.
  - System prompt enforces: discover files → read → analyze → generate → render →
    create branch → commit → open ONE PR (per `one_pr_per_run`); never commit to the
    default branch. Keep everything injectable for fakes.
  - _Test:_ build agent with fakes + stubbed model runner; assert custom + GitHub
    tools registered and system prompt enforces the branch→PR flow. No live calls.
  - _Demo:_ instantiate the agent; print registered tool names + system prompt.
  - _Requirements: 3.1, 3.2, 5.1, 7.1, 7.2_

- [ ] 8. Bedrock adapter + local CLI (live)
  - Implement `adapters/bedrock_llm.py` `DocGenerator` backed by Strands/Bedrock
    (model id + region from settings); pure prompt-builder function from
    `DocTarget`.
  - Implement `main.py` (`hkt-docagent`): read PAT from env, build real MCP client +
    Bedrock generator + agent, run against the target repo.
  - _Test:_ unit-test prompt construction (pure); guard a live integration test
    behind an env flag / creds presence.
  - _Demo:_ `hkt-docagent --owner <you> --repo op-ia-hkt26-doc` runs against real
    Bedrock + GitHub and opens a real PR (needs AWS creds + PAT).
  - _Requirements: 2.1, 2.2, 3.1, 6.4, 9.2, 9.3_

- [ ] 9. AgentCore deployment wiring
  - Implement `app.py`: `BedrockAgentCoreApp()`, `@app.entrypoint async def
    handler(request)` validating `request["prompt"]` is a string, building the agent
    (Bedrock + real MCP from env/secret PAT), streaming events; `app.run()`.
  - Add a short `docagent` README with `agentcore configure`/`launch` steps,
    required env/secrets (PAT, model id, region), and least-privilege IAM/PAT notes.
  - _Test:_ unit-test the entrypoint with a fake agent — non-string prompt rejected,
    valid prompt yields events.
  - _Demo:_ run `app.py` locally, `curl POST /invocations` with a JSON prompt →
    agent opens a PR; then `agentcore launch` deploys it (live AWS step).
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 9.2, 9.3_

- [ ] 10. (Stretch) Extensibility proof — README tool + per-file PR granularity
  - Add `tools/readme_tools.py` `generate_readme` `@tool` (same pattern) and
    register it in `build_agent()` — proving extensibility.
  - Implement the `one_pr_per_run=False` path (one PR per file) end-to-end.
  - _Test:_ README tool produces a draft with the fake generator; per-file mode
    yields multiple PR payloads in the fake MCP provider.
  - _Demo:_ one agent run that documents functions and updates a README, and (in
    per-file mode) opens multiple PRs.
  - _Requirements: 5.2, 7.1, 7.2_
