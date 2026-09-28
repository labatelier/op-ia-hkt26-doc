# Amazon Bedrock AgentCore Use Cases

End-to-end samples organized by agent type. Each folder maps to one of the three workload categories used in AgentCore documentation. Two of those categories ship in this repository today; the coding-assistant category is not part of it yet.

## Categories

### [01-conversational-agents](./01-conversational-agents/)

Agents that interact with users in real time. Users authenticate through an identity provider, the agent maintains session and long-term memory per user, and responses stream back as the agent works. See the [category README](./01-conversational-agents/README.md) for the full list and a guide on which sample to start with.

| Sample | Description | Vertical | Key Features |
|--------|-------------|----------|--------------|
| [A2A-multi-agent-incident-response](./01-conversational-agents/A2A-multi-agent-incident-response/) | Multi-agent incident response implemented with three A2A frameworks | IT / DevOps | Runtime, Gateway, Memory, A2A (3 frameworks) |
| [AWS-operations-agent](./01-conversational-agents/AWS-operations-agent/) | AWS operations assistant with Okta OAuth2 and 20+ read-only AWS tools reached through an MCP Gateway | Cloud Operations | Runtime, Gateway, Memory, Identity (Okta), Observability |
| [customer-support-assistant-vpc](./01-conversational-agents/customer-support-assistant-vpc/) | Customer support agent deployed in a fully private VPC, with tools over Aurora PostgreSQL, DynamoDB, and Lambda | Retail / E-commerce | Runtime, Gateway, Identity (Cognito M2M), all inside a VPC |
| [deep-research-agent](./01-conversational-agents/deep-research-agent/) | Deep research assistant with web search and runtime deployment | Research / Q&A | Gateway (Web Search), Runtime |
| [device-management-agent](./01-conversational-agents/device-management-agent/) | IoT device management system with Cognito authentication and real-time monitoring | IoT / Smart Home | Runtime, Gateway, Identity (Cognito), Observability |
| [episodic-memory-claims-agent](./01-conversational-agents/episodic-memory-claims-agent/) | Multi-agent claims processing that learns from human adjuster decisions through episodic memory | Insurance | Runtime, Memory (episodic), Identity (Cognito) |
| [finance-personal-assistant](./01-conversational-agents/finance-personal-assistant/) | Personal budget management with multi-agent workflows and guardrails | Personal Finance | Runtime, Identity (Cognito), Bedrock Guardrails |
| [healthcare-appointment-agent](./01-conversational-agents/healthcare-appointment-agent/) | FHIR-compliant healthcare appointment scheduling with patient data integration | Healthcare | Runtime, Gateway, Policy, Observability (FHIR R4) |
| [lakehouse-agent](./01-conversational-agents/lakehouse-agent/) | Secure data lakehouse assistant with memory and row-level access controls | Data and Analytics | Runtime, Gateway, Memory, Policy (row-level security) |
| [market-trends-agent](./01-conversational-agents/market-trends-agent/) | Financial market analysis with browser tools and memory integration | Financial Services | Runtime, Memory, Browser, Evaluations, Optimization |
| [SRE-agent](./01-conversational-agents/SRE-agent/) | Site reliability engineering assistant with multi-agent LangGraph workflows | Site Reliability | Runtime, Gateway, Memory, Observability |
| [video-games-sales-assistant](./01-conversational-agents/video-games-sales-assistant/) | Conversational data analyst assistant over video game sales data, with a Next.js / Amplify Gen 2 frontend and CDK deployment | Retail / Gaming | Runtime, Gateway, Memory |

### [02-workflow-automation-agents](./02-workflow-automation-agents/)

Agents that run without a user in the loop. They are triggered by events such as file uploads, webhook calls, or scheduled jobs. Identity is service-to-service rather than user-facing, and memory is minimal since state is carried in the event payload.

| Sample | Description | Vertical | Key Features |
|--------|-------------|----------|--------------|
| [event-driven-claims-agent](./02-workflow-automation-agents/event-driven-claims-agent/) | Event-driven insurance claims processing with policy enforcement and evaluation | Insurance | Runtime, Gateway, Memory, Policy, Evaluations, Observability |
| [visa-b2b-account-payable-agent](./02-workflow-automation-agents/visa-b2b-account-payable-agent/) | Automated B2B accounts payable workflows with Visa payments | B2B Payments | Runtime, Gateway, Policy, Payments |
| [enterprise-web-intelligence-agent](./02-workflow-automation-agents/enterprise-web-intelligence-agent/) | Web research and analysis agent using browser tools for competitive intelligence | Market Intelligence | Runtime, Browser |
| [intelligent-event-agent](./02-workflow-automation-agents/intelligent-event-agent/) | Event automation agent with runtime, memory, and gateway integration | General / Events | Runtime, Memory, Gateway *(in development)* |
| [it-incident-response-agent](./02-workflow-automation-agents/it-incident-response-agent/) | Ticket published to SNS is diagnosed and resolved using a knowledge base and Lambda tools behind a Gateway | IT Operations / ITSM | Runtime, Gateway, Memory, Policy, Identity, Observability, Evaluations |
| [multi-isv-orchestration](./02-workflow-automation-agents/multi-isv-orchestration/) | Multi-system workflow orchestration across enterprise CRM and ERP services | Enterprise CRM + ERP | Gateway (multi-target), Identity (Cognito + CustomOauth2) |
| [receipts-intelligent-document-processing-agent](./02-workflow-automation-agents/receipts-intelligent-document-processing-agent/) | Dual-agent receipt processing: OCR, validation, and governed writes, with a model degradation ladder on capacity errors | Finance / Expense Management | Runtime, Gateway, Memory, Policy (Cedar), Evaluations, Observability |
| [gpu-music-production-agent](./02-workflow-automation-agents/gpu-music-production-agent/) | Collaborative music production with local GPU inference, mastering, and compliance screening | Media & Entertainment | Runtime (EC2 capacity provider, GPU), Memory; local model inference, collocated agents on a shared volume |

### 03-coding-assistants *(not in this repository yet)*

Agents that help developers write, run, or fix code. Tasks tend to be longer-running and scoped to a project or repository. AgentCore Code Interpreter handles sandboxed execution, and Gateway can aggregate multiple developer tool APIs behind one MCP endpoint. The samples planned for this category — a text-to-Python IDE built on Code Interpreter and a Claude Code integration that fronts several MCP servers with a single Gateway endpoint — are tracked in [use-case-assessment.md](./use-case-assessment.md) and are not part of this repository yet.

## Prerequisites

Every sample carries its own prerequisites and deployment steps in its README — start there. The recurring requirements across samples are:

- An AWS account with the AWS CLI configured (`aws sts get-caller-identity` works) and Amazon Bedrock model access enabled in your region.
- Python 3.10 or later (some samples require 3.11 or 3.12) and [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Node.js 20 or later plus the AgentCore CLI (`npm install -g @aws/agentcore@0.30.0`) for the samples deployed with `agentcore deploy`.
- A container engine (Docker or [Finch](https://runfinch.com)) for samples whose runtime uses a container build.
- CDK bootstrapped in the target account and region (`npx cdk bootstrap aws://<ACCOUNT>/<REGION>`) for CDK-based samples.

## Getting started

```bash
git clone https://github.com/labatelier/op-ia-hkt26-doc.git
cd op-ia-hkt26-doc
```

Pick a sample from the tables above and follow its README. If you prefer a shared Python environment for the notebook-based samples, the root `requirements.txt` installs the packages they have in common (Strands Agents, LangChain / LangGraph, `bedrock-agentcore`, JupyterLab, boto3):

```bash
pip install -r requirements.txt
```

Python linting is configured repository-wide in [pyproject.toml](./pyproject.toml) (ruff, 120-character lines, with tutorial-friendly rules relaxed).

## Repository structure

```
.
├── 01-conversational-agents/        # User-facing chat, Q&A, interactive assistants
├── 02-workflow-automation-agents/   # Event-driven and background pipelines
├── requirements.txt                 # Shared Python dependencies for notebook-based samples
├── pyproject.toml                   # Repo-wide ruff configuration
├── MIGRATION.md                     # Starter Toolkit to AgentCore CLI migration guide
├── use-case-assessment.md           # Assessment and restructuring plan for the samples
├── CHANGELOG.md                     # Log of changes to this repository
├── CONTRIBUTING.md
├── CONTRIBUTORS.md
└── CODE_OF_CONDUCT.md
```

Each category folder has a README describing the typical service configuration and multi-agent patterns for that workload type, plus a table of its samples.

## Resources

- [AgentCore docs](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Migrating from the Starter Toolkit to the AgentCore CLI](./MIGRATION.md)
- [Contributing guidelines](./CONTRIBUTING.md) and [code of conduct](./CODE_OF_CONDUCT.md)
