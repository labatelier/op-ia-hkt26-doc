# Amazon Bedrock AgentCore Use Cases

End-to-end samples organized by agent type. Each folder maps to one of the workload categories used in AgentCore documentation.

## Repository layout

```
.
├── 01-conversational-agents/       # user-facing chat, Q&A and interactive assistants
├── 02-workflow-automation-agents/  # event-driven and background agents
├── MIGRATION.md                    # Starter Toolkit to AgentCore CLI migration guide
├── use-case-assessment.md          # per-sample assessment and restructuring plan
├── requirements.txt                # shared Python packages for the notebook-based samples
└── pyproject.toml                  # repository-wide ruff configuration
```

Every sample is self-contained: it ships its own README, its own dependency manifest (`requirements.txt`, `pyproject.toml` or `package.json`) and its own deployment scripts. Start from the README of the sample you are interested in.

## Prerequisites

The list below covers what most samples need. Each sample README states the exact versions and any extra setup it requires.

- An AWS account with the Amazon Bedrock models used by the sample enabled, and the AWS CLI configured (`aws sts get-caller-identity` should succeed).
- Node.js 20 or later plus the AgentCore CLI for the samples that deploy with it: `npm install -g @aws/agentcore@0.30.0`.
- Python 3.10 or later (some samples require 3.11 or 3.12) and [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Docker, or [Finch](https://runfinch.com), for the samples whose runtime is a container build.
- CDK bootstrapped in the target account and region (`npx cdk bootstrap aws://<ACCOUNT>/<REGION>`) for the CDK-based samples.

For the notebook-based samples, the root `requirements.txt` installs the shared Python dependencies (Strands Agents, LangChain/LangGraph, `bedrock-agentcore`, JupyterLab, and others):

```bash
pip install -r requirements.txt
```

Migrating an existing project from the Bedrock AgentCore Starter Toolkit to the AgentCore CLI? See [MIGRATION.md](./MIGRATION.md).

## Categories

### [01-conversational-agents](./01-conversational-agents/)

Agents that interact with users in real time. Users authenticate through an identity provider, the agent maintains session and long-term memory per user, and responses stream back as the agent works. See the [category README](./01-conversational-agents/README.md) for the full list and a guide on which sample to start with.

| Sample | Description | Vertical | Key Features |
|--------|-------------|----------|--------------|
| [A2A-multi-agent-incident-response](./01-conversational-agents/A2A-multi-agent-incident-response/) | Multi-agent incident response implemented with three A2A frameworks | IT / DevOps | Runtime, Gateway, Memory, A2A (3 frameworks) |
| [AWS-operations-agent](./01-conversational-agents/AWS-operations-agent/) | Intelligent AWS operations assistant with Okta authentication and comprehensive monitoring capabilities | Cloud Operations | Runtime, Gateway, Memory, Policy, Observability |
| [customer-support-assistant-vpc](./01-conversational-agents/customer-support-assistant-vpc/) | Production-ready customer service agent with memory, knowledge base integration, and Google OAuth | Retail / E-commerce | Runtime, Gateway (VPC) |
| [deep-research-agent](./01-conversational-agents/deep-research-agent/) | Deep research assistant with web search and runtime deployment | Research / Q&A | Gateway (Web Search), Runtime |
| [device-management-agent](./01-conversational-agents/device-management-agent/) | IoT device management system with Cognito authentication and real-time monitoring | IoT / Smart Home | Runtime, Gateway, Policy, Identity (Cognito) |
| [episodic-memory-claims-agent](./01-conversational-agents/episodic-memory-claims-agent/) | Multi-agent claims processing that learns from human adjuster decisions through trust-filtered episodic memory | Insurance | Runtime, Memory (episodic), Identity (Cognito) |
| [finance-personal-assistant](./01-conversational-agents/finance-personal-assistant/) | Personal budget management with multi-agent workflows and guardrails | Personal Finance | Gateway, Policy |
| [healthcare-appointment-agent](./01-conversational-agents/healthcare-appointment-agent/) | FHIR-compliant healthcare appointment scheduling with patient data integration | Healthcare | Runtime, Gateway, Policy, Observability (FHIR R4) |
| [lakehouse-agent](./01-conversational-agents/lakehouse-agent/) | Secure data lakehouse assistant with memory and row-level access controls | Data and Analytics | Runtime, Gateway, Memory, Policy (row-level security) |
| [market-trends-agent](./01-conversational-agents/market-trends-agent/) | Financial market analysis with browser tools and memory integration | Financial Services | Runtime, Memory, Browser, Evaluations, Optimization |
| [SRE-agent](./01-conversational-agents/SRE-agent/) | Site reliability engineering assistant with multi-agent LangGraph workflows | Site Reliability | Runtime, Gateway, Memory, Observability |
| [video-games-sales-assistant](./01-conversational-agents/video-games-sales-assistant/) | Conversational data analyst assistant over video game sales data, with a Next.js / Amplify Gen 2 frontend and CDK backend | Data and Analytics / Gaming | Runtime, Memory, Observability |

### [02-workflow-automation-agents](./02-workflow-automation-agents/)

Agents that run without a user in the loop. They are triggered by events such as file uploads, webhook calls, or scheduled jobs. Identity is service-to-service rather than user-facing, and memory is minimal since state is carried in the event payload.

| Sample | Description | Vertical | Key Features |
|--------|-------------|----------|--------------|
| [event-driven-claims-agent](./02-workflow-automation-agents/event-driven-claims-agent/) | Event-driven insurance claims processing with policy enforcement and evaluation | Insurance | Runtime, Gateway, Memory, Policy, Evaluations, Observability |
| [visa-b2b-account-payable-agent](./02-workflow-automation-agents/visa-b2b-account-payable-agent/) | Automated B2B accounts payable workflows with Visa payments | B2B Payments | Runtime, Gateway, Policy, Payments |
| [enterprise-web-intelligence-agent](./02-workflow-automation-agents/enterprise-web-intelligence-agent/) | Web research and analysis agent using browser tools for competitive intelligence | Market Intelligence | Runtime, Browser |
| [intelligent-event-agent](./02-workflow-automation-agents/intelligent-event-agent/) | Event automation agent with runtime, memory, and gateway integration | General / Events | Runtime, Memory, Gateway *(in development)* |
| [it-incident-response-agent](./02-workflow-automation-agents/it-incident-response-agent/) | Ticket published to SNS is diagnosed against a knowledge base and Lambda tools, then resolved back in the ticket store | IT Operations / ITSM | Runtime, Gateway, Memory, Policy, Identity, Evaluations, Observability |
| [multi-isv-orchestration](./02-workflow-automation-agents/multi-isv-orchestration/) | Multi-system workflow orchestration across enterprise CRM and ERP services | Enterprise CRM + ERP | Gateway (multi-target), Identity (Cognito + CustomOauth2) |
| [receipts-intelligent-document-processing-agent](./02-workflow-automation-agents/receipts-intelligent-document-processing-agent/) | Dual-agent receipt processing (OCR, validation, persisted expense) with a config-driven model degradation ladder | Intelligent Document Processing | Runtime, Gateway, Memory, Policy, Evaluations, Observability |
| [gpu-music-production-agent](./02-workflow-automation-agents/gpu-music-production-agent/) | Collaborative music production with local GPU inference, mastering, and compliance screening | Media & Entertainment | Runtime (EC2 capacity provider, GPU), Memory; local model inference, collocated agents on a shared volume |

### 03-coding-assistants *(planned)*

Agents that help developers write, run, or fix code. Tasks tend to be longer-running and scoped to a project or repository. AgentCore Code Interpreter handles sandboxed execution, and Gateway can aggregate multiple developer tool APIs behind one MCP endpoint. No samples in this category ship at this revision — see [use-case-assessment.md](./use-case-assessment.md) for the candidates being prepared.

## Contributing

- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to report bugs and submit pull requests
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) — the code of conduct this project has adopted
- [CONTRIBUTORS.md](./CONTRIBUTORS.md) — the people behind the samples

## Resources
- [AgentCore docs](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore CLI](https://github.com/aws/agentcore-cli)
