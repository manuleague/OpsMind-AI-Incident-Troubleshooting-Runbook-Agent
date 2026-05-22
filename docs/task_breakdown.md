# Task List by Priority

## P0 - Core Demo Path

### 1. Repository Scaffold

Objective: Create a clear project layout that judges can scan quickly.

Files:

- `README.md`
- `app/opsmind/*`
- `knowledge_base/runbooks/*`
- `prompts/*`
- `demo/*`
- `docs/*`

Implement:

- Python package structure.
- Configuration folder.
- Prompts folder.
- Sample knowledge base folder.
- Tests folder.

Acceptance criteria:

- A reviewer can understand the app layout in under one minute.
- README explains how to run local demo mode.

### 2. Local Demo Retrieval

Objective: Make the project demoable without cloud credentials.

Files:

- `app/opsmind/local_retriever.py`
- `knowledge_base/runbooks/*.md`

Implement:

- Token-based markdown retrieval.
- Relevance scoring.
- Metadata extraction for category and severity.

Acceptance criteria:

- Query for "502 after deployment" returns the HTTP 502/503 runbook first.
- Query for "CrashLoopBackOff" returns the Kubernetes runbook.

### 3. Foundry IQ Adapter

Objective: Keep Foundry IQ central while isolating preview API changes.

Files:

- `app/opsmind/foundry_iq.py`
- `config/app.example.env`

Implement:

- Endpoint, knowledge base ID, API version, and API key config.
- Request payload builder.
- Response normalization into citation-ready sources.
- Local fallback if Foundry IQ mode fails during demo.

Acceptance criteria:

- The app can switch between `local` and `foundry` retrieval modes.
- Foundry IQ result mapping is isolated to one file.

### 4. Incident Analyzer

Objective: Convert retrieved sources into structured troubleshooting guidance.

Files:

- `app/opsmind/analyzer.py`
- `app/opsmind/models.py`
- `app/opsmind/formatter.py`

Implement:

- Incident classification.
- Confidence label.
- Risk label.
- Evidence, diagnosis, remediation, validation, escalation, and citations.

Acceptance criteria:

- Every response includes citations when sources exist.
- Diagnosis and remediation are separate.
- Insufficient retrieval produces a safe fallback.

### 5. Safety Guardrails

Objective: Prevent unsafe or overconfident operational guidance.

Files:

- `app/opsmind/safety.py`
- `prompts/safety_guardrails.md`

Implement:

- Risk detection for production, deletion, rollback, firewall, DNS, certificate, and secret changes.
- Human review warnings.

Acceptance criteria:

- High-risk incidents include human approval warnings.
- The agent never claims to execute infrastructure changes.

### 6. Streamlit UI

Objective: Provide a polished hackathon demo interface.

Files:

- `app/opsmind/ui_streamlit.py`

Implement:

- Incident input.
- Severity selector.
- Environment selector.
- Results sections.
- Citations expander.

Acceptance criteria:

- A judge can submit a scenario and understand the answer without reading code.

## P1 - Submission Polish

### 7. Knowledge Base Design Guide

Objective: Explain how Foundry IQ should be populated.

Files:

- `docs/kb_design.md`

Implement:

- Document types.
- Metadata fields.
- Naming conventions.
- Ingestion checklist.

Acceptance criteria:

- A builder can create a Foundry IQ knowledge base from the guide.

### 8. Demo Script

Objective: Make the 3 to 5 minute presentation crisp.

Files:

- `demo/demo_script.md`
- `demo/sample_incidents.json`

Implement:

- Scenario.
- Screen flow.
- Talking points.
- Foundry IQ value moment.

Acceptance criteria:

- Demo shows retrieval, citations, safety, and practical next actions.

### 9. README and Judging Optimization

Objective: Improve submission clarity and scoring.

Files:

- `README.md`
- `docs/judging_optimization.md`

Implement:

- Project overview.
- Architecture.
- Setup steps.
- Hackathon alignment.
- Safety and future improvements.

Acceptance criteria:

- README can stand alone as the public GitHub submission page.

## P2 - Stretch

### 10. Export Response

Objective: Let engineers save a generated incident plan.

Files:

- `app/opsmind/ui_streamlit.py`
- `app/opsmind/formatter.py`

Implement:

- Download response as Markdown.

Acceptance criteria:

- User can download the current analysis.

### 11. Foundry Agent Service Path

Objective: Show deeper Microsoft agent integration.

Files:

- `app/opsmind/foundry_iq.py`
- `docs/architecture.md`

Implement:

- Optional notes or adapter for a Foundry Agent Service tool call path.

Acceptance criteria:

- Demo can explain both custom app retrieval and agent-service integration options.

### 12. Ticket Draft

Objective: Help support teams turn results into handoff notes.

Files:

- new `app/opsmind/ticket_draft.py`

Implement:

- Markdown summary suitable for Jira, Azure DevOps, or incident timeline.

Acceptance criteria:

- Draft contains summary, impact, evidence, actions, owner, and next update.

