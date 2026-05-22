# 🧠 OpsMind AI — Incident Troubleshooting & Runbook Agent

> AI-powered cloud ops assistant that retrieves grounded, cited troubleshooting guidance from a
> Microsoft Foundry IQ knowledge base.

**Agents League Hackathon 2026 | Track: Reasoning Agents | IQ Layer: Foundry IQ**

***

## Why OpsMind AI?

Cloud incidents happen fast, and engineers often lose precious minutes searching scattered runbooks, postmortems, and alert notes. OpsMind AI retrieves grounded troubleshooting guidance from a Microsoft Foundry IQ knowledge base and turns it into cited diagnosis, remediation, validation, and escalation steps in seconds. It is designed to help on-call teams move faster without making unsafe or unsupported changes.

***

## Architecture

```text
User Input
    |
    v
Streamlit UI
    |
    v
IncidentAnalyzer
    |
    v
FoundryIQClient ------------------> Azure AI Foundry
    |                                      |
    |                                      v
    |                              Foundry IQ Knowledge Base
    |
    +---- fallback ----> LocalRetriever
                         |
                         v
TroubleshootingResponse -> Formatter -> UI Output
```

***

## Features

- 🔍 **Grounded retrieval** via Microsoft Foundry IQ knowledge base
- 🧠 **Multi-step reasoning**: classify → retrieve → diagnose → remediate → validate → escalate
- 📄 **Cited answers**: every recommendation links to source runbooks
- ⚠️ **Safety guardrails**: risk assessment and human review warnings
- 🏃 **Local fallback mode**: works without Azure for development and testing
- 🖥️ **Streamlit UI** + CLI interface
- 8 pre-built runbooks covering: CPU spike, disk full, VM connectivity, DNS, SSL,
  Kubernetes pod crashloop, HTTP 502/503, failed deployment

***

## Supported Incident Categories

| Category | Example Incidents |
|---|---|
| Compute | Linux VM CPU spike, VM unreachable |
| Storage | Disk space critical, filesystem full |
| Networking | DNS resolution failure, NSG blocking |
| Security | SSL certificate expiry, TLS error |
| Application | HTTP 502/503, gateway error |
| Kubernetes | Pod crashloop, deployment failure |

***

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Knowledge Retrieval | Microsoft Foundry IQ |
| Azure SDK | azure-ai-projects |
| Authentication | DefaultAzureCredential / API Key |
| UI | Streamlit |
| CLI | Python argparse |
| Tests | pytest |

***

## Microsoft Foundry IQ Integration

Foundry IQ provides a reusable knowledge layer for agents, backed by Azure AI Search and agentic retrieval. OpsMind AI uses Foundry IQ as the primary retrieval source for runbooks and incident documents, requesting hybrid retrieval with citations enabled. Retrieved source snippets are normalized into `RetrievedSource` objects, then used by the analyzer to create grounded troubleshooting responses that reduce hallucination risk.

If the SDK path is unavailable during local development, OpsMind can fall back to either the Foundry IQ REST endpoint or the local markdown retriever.

***

## Quick Start

### Option A: Local mode (no Azure required)

```bash
git clone https://github.com/manuleague/OpsMind-AI-Incident-Troubleshooting-Runbook-Agent.git
cd OpsMind-AI-Incident-Troubleshooting-Runbook-Agent
pip install -r requirements.txt
cp .env.example .env
# OPSMIND_RETRIEVAL_MODE is already set to "local" in .env.example
streamlit run app/opsmind/ui_streamlit.py
```

### Option B: Foundry IQ mode (full integration)

```bash
cp .env.example .env
# Edit .env: set OPSMIND_RETRIEVAL_MODE=foundry and fill in Azure credentials
# See docs/AZURE_SETUP.md for step-by-step Azure configuration
streamlit run app/opsmind/ui_streamlit.py
```

### CLI usage

```bash
python -m app.opsmind.cli "Linux VM CPU spike above 95%" --severity sev2 --environment production
```

***

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `OPSMIND_RETRIEVAL_MODE` | Retrieval mode: `local` or `foundry` | `local` |
| `OPSMIND_KB_PATH` | Local markdown runbook directory | `knowledge_base/runbooks` |
| `OPSMIND_TOP_K` | Number of sources to retrieve | `4` |
| `AZURE_AI_PROJECT_CONNECTION_STRING` | Azure AI Foundry project connection string for SDK mode | empty |
| `FOUNDRY_IQ_AUTH_MODE` | Authentication mode: `credential` or `apikey` | `credential` |
| `FOUNDRY_IQ_KNOWLEDGE_BASE_ID` | Foundry IQ knowledge base ID | empty |
| `FOUNDRY_IQ_ENDPOINT` | REST fallback endpoint, usually Azure AI Search URL | empty |
| `FOUNDRY_IQ_API_KEY` | API key for REST fallback or API key auth mode | empty |
| `FOUNDRY_IQ_API_VERSION` | Foundry IQ REST API version | `2025-11-01-preview` |

***

## Demo Flow

1. Enter an incident description, such as `Linux VM CPU spike above 95% for the last 10 minutes, application latency degraded`.
2. Select severity and environment.
3. Click Analyze to see cited evidence, diagnosis, remediation steps, validation checks, and escalation triggers.

***

## Judging Alignment

| Criterion | How OpsMind addresses it |
|---|---|
| Accuracy & Relevance | Grounded retrieval from Foundry IQ; answers cite source runbooks |
| Reasoning & Multi-step | Pipeline: classify → retrieve → diagnose → remediate → validate → escalate |
| Creativity & Originality | Ops-focused knowledge agent with safety guardrails |
| UX & Presentation | Clean Streamlit UI with structured output sections |
| Reliability & Safety | Risk labels, human review warnings, no destructive recommendations |

***

## Knowledge Base

- `RB-CPU-001 Linux VM CPU Spike`: Diagnose high CPU, load average, process saturation, and safe mitigation.
- `RB-DISK-001 Linux Disk Space Critically Low`: Handle filesystem usage, inode exhaustion, and safe cleanup.
- `RB-SSL-001 SSL Certificate Expiration Warning`: Validate TLS expiry, renewal path, bindings, and chain health.
- `RB-HTTP-001 Application Returning 502 or 503`: Triage gateway, backend health, deployment, and dependency failures.
- `RB-DNS-001 DNS Resolution Failure`: Diagnose NXDOMAIN, SERVFAIL, stale records, private DNS, and resolver issues.
- `RB-K8S-001 Kubernetes Pod CrashLoopBackOff`: Investigate restart loops, logs, probes, config, secrets, and dependencies.
- `RB-DEPLOY-001 Failed Deployment or Bad Release`: Analyze failed releases, rollback safety, migrations, and feature flags.
- `RB-VM-001 Azure VM Unreachable After Deployment`: Triage VM power, boot diagnostics, NSGs, routes, and health probes.

***

## Safety Considerations

- OpsMind provides **recommendations only** — it does not execute commands
- All high-risk actions are flagged with "Requires human review"
- No confidential data is stored or logged

***

## Future Improvements

- Add more runbooks (monitoring, database, network security)
- Connect to Azure Monitor alerts as live input
- Add follow-up question flow
- Support multi-language runbooks

***

## Setup for Foundry IQ

See [docs/AZURE_SETUP.md](docs/AZURE_SETUP.md) for the complete Azure configuration guide.

***

## License

MIT
