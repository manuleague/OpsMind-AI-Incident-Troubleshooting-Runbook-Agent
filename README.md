# 🧠 OpsMind AI — Incident Troubleshooting Agent

> **Agents League Hackathon 2026** · Powered by [Microsoft Azure AI Foundry](https://ai.azure.com)

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)](https://streamlit.io)
[![Azure Foundry](https://img.shields.io/badge/Azure-AI%20Foundry-0078D4?logo=microsoftazure)](https://ai.azure.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

OpsMind AI is a **grounded, cited incident troubleshooting agent** for cloud and DevOps operations teams. Given an incident description, it retrieves the most relevant runbooks from a knowledge base powered by **Microsoft Azure AI Foundry IQ**, classifies the incident, and returns structured diagnostic and remediation guidance — with full source citations.

---

## ✨ Key Features

- 🔍 **Grounded retrieval** — answers are backed by runbooks from Foundry IQ, not hallucinated
- 📄 **Full citations** — every diagnosis and remediation step references a specific source `[doc_id]`
- 🏷️ **Smart classification** — automatically maps incidents to: `compute`, `kubernetes`, `database`, `networking`, `storage`, `security`, `application`
- ⚠️ **Risk & safety layer** — flags high-risk actions and requires human approval before destructive changes
- 🖥️ **Streamlit UI** — clean, interactive web interface for ops teams
- 💻 **CLI mode** — scriptable for CI/CD pipelines and alerting integrations
- 🔄 **Dual retrieval** — Foundry IQ (cloud) or local markdown runbooks (offline/dev)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              OpsMind AI Agent                   │
│                                                 │
│  Input: Incident description + severity + env   │
│         ↓                                       │
│  IncidentAnalyzer                               │
│    ├── FoundryIQClient ──► Azure gpt-4o         │
│    │       └── Retrieves top-K runbooks         │
│    ├── classify_incident()  (keyword matching)  │
│    ├── assess_risk()        (safety layer)      │
│    └── build_response()     (structured output) │
│         ↓                                       │
│  TroubleshootingResponse (cited Markdown)       │
│                                                 │
│  Interfaces: Streamlit UI · CLI                 │
└─────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  Azure AI Foundry      │
│  Project: proj-default │
│  Model:   gpt-4o       │
│  Index:   runbooks     │
└────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure AI Foundry project with `gpt-4o` deployment
- API key from [Azure AI Foundry portal](https://ai.azure.com)

### 1. Clone & install

```bash
git clone https://github.com/manuleague/OpsMind-AI-Incident-Troubleshooting-Runbook-Agent.git
cd OpsMind-AI-Incident-Troubleshooting-Runbook-Agent
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Use "foundry" for Azure AI Foundry, "local" for offline testing
OPSMIND_RETRIEVAL_MODE=foundry

# Your Foundry project endpoint
AZURE_AI_PROJECT_CONNECTION_STRING=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>

# API key from Foundry Home
FOUNDRY_IQ_API_KEY=<your-api-key>

FOUNDRY_IQ_AUTH_MODE=apikey
OPSMIND_TOP_K=4
```

### 3. Run

**Streamlit UI:**
```bash
streamlit run app/opsmind/ui_streamlit.py
```
Open → http://localhost:8501

**CLI:**
```bash
python -m app.opsmind.cli "Linux VM CPU spike 95%"
python -m app.opsmind.cli "AKS node NotReady after maintenance"
python -m app.opsmind.cli "Azure SQL connection timeout 500 errors"
```

---

## 📋 Supported Incident Categories

| Category | Example Incidents |
|---|---|
| `compute` | CPU spike, VM unreachable, SSH timeout, VMSS scaling failure |
| `kubernetes` | Pod CrashLoopBackOff, AKS node NotReady, OOMKilled, ImagePullBackOff |
| `database` | SQL connection timeout, deadlock, connection pool exhaustion, high DTU |
| `networking` | DNS resolution failure, NSG blocking, VNet connectivity, packet loss |
| `storage` | Disk full, 403 Forbidden, blob access denied, IOPS throttling |
| `security` | TLS certificate expired, 401 Unauthorized, Key Vault access denied |
| `application` | 502/503 gateway errors, high latency, deployment failure, OOM |

---

## 🔧 Retrieval Modes

| Mode | When to use | Config |
|---|---|---|
| `foundry` | Demo / production — uses Azure gpt-4o | `OPSMIND_RETRIEVAL_MODE=foundry` |
| `local` | Offline / dev — uses local markdown runbooks | `OPSMIND_RETRIEVAL_MODE=local` |

---

## 📁 Project Structure

```
OpsMind-AI-Incident-Troubleshooting-Runbook-Agent/
├── app/
│   ├── streamlit_app.py          # Streamlit web UI
│   └── opsmind/
│       ├── analyzer.py           # Core incident analysis engine
│       ├── foundry_iq.py         # Azure Foundry IQ REST client
│       ├── local_retriever.py    # Local markdown retriever
│       ├── models.py             # Data models
│       ├── config.py             # Settings / .env loader
│       ├── safety.py             # Risk assessment & human review
│       └── cli.py                # CLI entrypoint
├── knowledge_base/
│   └── runbooks/                 # Local markdown runbooks (offline mode)
├── .env.example                  # Environment template
├── requirements.txt
└── README.md
```

---

## 🛡️ Safety & Human Review

OpsMind AI enforces a **human-in-the-loop** safety layer:

- `sev1` / `critical` incidents always require human approval
- Production environment incidents flag blast radius and rollback plan
- Destructive actions (rollback, secret rotation, DNS change) are never executed automatically
- All remediation steps are **recommendations only** — validated by a human before execution

---

## 🏆 Hackathon: Agents League 2026

This project was built for the **Agents League Hackathon 2026**, demonstrating:

- ✅ **Grounded AI** — no hallucinations, every answer cites a runbook source
- ✅ **Azure AI Foundry integration** — production-grade agent with gpt-4o
- ✅ **Responsible AI** — human review gates, risk classification, audit trail
- ✅ **Real ops value** — reduces MTTR for cloud incidents with structured, actionable guidance

---

