# OpsMind AI — Demo Script (4 minutes)

## Setup (before recording)

- Set OPSMIND_RETRIEVAL_MODE=foundry (or local if Foundry IQ not available)
- Run: streamlit run app/opsmind/ui_streamlit.py
- Open browser at localhost:8501

## Scene 1 — Introduction (30 seconds)

Say: "This is OpsMind AI — an incident troubleshooting agent that retrieves grounded,
cited guidance from a Microsoft Foundry IQ knowledge base."
Show: the Streamlit home screen with the input area visible.

## Scene 2 — Demo incident 1: Linux VM CPU spike (60 seconds)

Type: "Linux VM CPU spike above 95% for the last 10 minutes, application latency degraded"
Select: Severity = sev2, Environment = production
Click Analyze
Show: full response including Evidence (with Foundry IQ citations), Diagnosis, Remediation steps
Highlight: the citation links and the Human Review Required warning

## Scene 3 — Demo incident 2: Kubernetes pod crashloop (60 seconds)

Type: "Kubernetes deployment pod restarting every 30 seconds, crashloopbackoff error"
Select: Severity = sev1, Environment = production
Click Analyze
Show: how the agent classifies the incident differently and retrieves Kubernetes-specific runbook
Highlight: different remediation steps per category

## Scene 4 — Show Foundry IQ value (60 seconds)

Switch to sidebar and show the retrieval mode badge (Foundry IQ / local)
Explain: "All answers are grounded — the agent does not fabricate steps.
Every recommendation cites the source document it retrieved from Foundry IQ."
Show: the Evidence expander with citation IDs

## Scene 5 — Close (30 seconds)

Show: GitHub repository with clean README
Say: "OpsMind AI is open source, built on Python and Microsoft Foundry IQ,
and designed for cloud operations engineers who need fast, safe, cited incident guidance."
