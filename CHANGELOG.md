# Changelog

Documentation changes proposed by the documentation agent, newest first.

This file is maintained automatically: an entry is prepended each time the agent
opens a pull request. The agent never reviews or rewrites it.

## 2026-09-28 13:27 UTC — run c09963cf

Triggered by `push` on `main`, targeting `main`.

Fix the conversational-agent tables, which credited samples with frameworks, frontends, identity providers and AgentCore features their code does not use, and list CHANGELOG.md and CONTRIBUTORS.md in the repository structure.

- `01-conversational-agents/README.md` — documentation: framework, frontend and feature claims did not match the samples
- `README.md` — documentation: sample descriptions and feature lists contradicted the code

## 2026-09-28 13:21 UTC — run 6e3795f1

Triggered by `push` on `main`, targeting `main`.

Repair the corrupted 01-conversational-agents heading link, drop paths to folders that do not exist, list the three samples the tables were missing, remove the stray trailing title, and add prerequisites, getting started and repository structure sections.

- `01-conversational-agents/README.md` — documentation: sample table omitted one folder, dead category link
- `02-workflow-automation-agents/README.md` — documentation: sample table omitted two folders, dead category link
- `README.md` — documentation: broken heading link, dead paths, missing samples, stray title
