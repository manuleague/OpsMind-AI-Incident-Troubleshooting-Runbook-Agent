# Hackathon Guide

## Track

OpsMind AI targets the Microsoft Agents League Hackathon 2026 Reasoning Agents track.

## Required IQ Layer

OpsMind integrates Foundry IQ as the primary knowledge retrieval layer. `app/opsmind/foundry_iq.py` queries the configured Azure Foundry gpt-4o endpoint backed by the Foundry IQ file search index. Retrieved runbook chunks are returned as cited `RetrievedSource` objects.

## Judging Criteria Alignment

| Criterion | How OpsMind satisfies it | Code references |
|---|---|---|
| Accuracy & Relevance | Uses Foundry IQ as primary retrieval, extracts real doc IDs, titles, chunk text, and relevance scores. Local fallback preserves offline reliability. | `app/opsmind/foundry_iq.py`, `app/opsmind/local_retriever.py` |
| Reasoning & Multi-step Thinking | Produces a four-step diagnosis chain, numbered remediation, validation checks, escalation triggers, rollback prompt, and confidence label. | `app/opsmind/analyzer.py`, `app/opsmind/formatter.py` |
| Creativity & Originality | Adds blast-radius estimation and similar incident patterns so the agent feels like an on-call troubleshooting partner. | `estimate_blast_radius()`, `build_similar_incidents()` |
| User Experience & Presentation | Streamlit UI includes status spinner, severity badge, blast-radius warning, recent incidents, and cited evidence expanders. | `app/streamlit_app.py` |
| Reliability & Safety | Human-in-the-loop warnings, high-risk blast-radius detection, rollback-plan prompt, input validation, and no command execution. | `app/opsmind/safety.py`, `app/streamlit_app.py` |

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Use local retrieval mode:

```bash
set OPSMIND_RETRIEVAL_MODE=local
```

Run the Streamlit app:

```bash
streamlit run app/streamlit_app.py
```

Run the offline demo:

```bash
python demo/run_demo.py
```

Run tests:

```bash
pytest tests/ -v
```

## Demo Narrative for Judges

1. Enter a production incident such as a Linux VM CPU spike.
2. Show the Foundry IQ or local retrieval evidence with citations.
3. Walk through category, confidence, blast radius, diagnosis, remediation, validation, escalation, rollback plan, and similar incidents.
4. Emphasize that OpsMind recommends only and requires human approval for high-risk actions.
