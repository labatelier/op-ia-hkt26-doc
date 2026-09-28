# Changelog

Documentation changes proposed by the documentation agent, newest first.

This file is maintained automatically: an entry is prepended each time the agent
opens a pull request. The agent never reviews or rewrites it.

## 2026-09-28 12:51 UTC — run 99e99e06

Triggered by `push` on `main`, targeting `main`.

The root README contained a corrupted `01-converssdfsfational-agents` heading and link, a `data-analyst-conversational-assistant` row pointing at a folder that does not exist (a duplicate of video-games-sales-assistant), and a `03-coding-assistants` section linking to a folder and two samples absent from the repository; all are now corrected, and the stray trailing `# hackathon-aws-agentcore-samples` heading was dropped. Samples present in the tree but missing from the tables were added — episodic-memory-claims-agent under 01, it-incident-response-agent and receipts-intelligent-document-processing-agent under 02 — in the root README and in both category READMEs. The root README also gains a repository layout, a prerequisites section derived from the manifests and sample READMEs (AWS CLI, Node 20 + AgentCore CLI 0.30.0, Python 3.10+/uv, Docker or Finch, CDK bootstrap, root requirements.txt), and pointers to MIGRATION.md, CONTRIBUTING.md and CODE_OF_CONDUCT.md.

- `01-conversational-agents/README.md` — documentation: List the episodic-memory-claims-agent sample that exists in the folder but was missing from the table, align the video-games-sales-assistant entry with its README, and drop the link to the absent 03-coding-assistants folder.
- `02-workflow-automation-agents/README.md` — documentation: Add the it-incident-response-agent and receipts-intelligent-document-processing-agent samples that exist in the folder but were missing from the table, and drop the link to the absent 03-coding-assistants folder.
- `README.md` — documentation: Fix the corrupted category heading and broken links in the root README, add the samples that were missing from the tables, and document repository layout, prerequisites and contributing pointers.
