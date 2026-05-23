# OpsMind AI Architecture

OpsMind AI is a Python incident troubleshooting agent for cloud operations teams. It retrieves grounded runbook evidence from Foundry IQ when available and uses local markdown runbooks as an offline fallback.

## Data Flow

```text
Incident description + severity + environment
        |
        v
Streamlit UI / CLI
        |
        v
IncidentAnalyzer
        |
        +--> FoundryIQClient (primary, Foundry IQ REST)
        |       |
        |       v
        |   gpt-4o + file search index / Foundry IQ knowledge base
        |
        +--> LocalMarkdownRetriever (offline fallback)
        |
        v
RetrievedSource objects with doc_id, title, chunk text, score
        |
        v
Classification + confidence + blast radius + safety assessment
        |
        v
TroubleshootingResponse
        |
        v
Formatter / Streamlit output / CLI output
```

## Foundry IQ Retrieval

`app/opsmind/foundry_iq.py` calls the Azure Foundry REST chat completions endpoint for the configured gpt-4o deployment. The prompt asks Foundry IQ to retrieve relevant runbooks from the file search index and include document IDs, titles, chunk text, relevance scores, and remediation details.

The client extracts citations from structured response fields when available. If the payload does not include structured citations, it parses `[doc_id]` references from the model response and converts them into `RetrievedSource` objects. HTTP 429 rate limits are retried once after three seconds. If Foundry retrieval fails, `IncidentAnalyzer` falls back to local markdown retrieval so the demo remains reliable offline.

## Classification

`classify_incident()` first trusts the top retrieved source metadata when available. This keeps the answer grounded in the runbook Foundry IQ actually selected. When metadata is unavailable, it uses keyword scoring across seven categories:

- compute
- kubernetes
- database
- networking
- storage
- security
- application

Unknown incidents remain `unknown` when no category keywords match.

## Reasoning Pipeline

`IncidentAnalyzer.analyze()` performs the same sequence for UI and CLI:

1. Retrieve sources.
2. Classify the incident.
3. Compute confidence from top retrieval score.
4. Estimate blast radius from severity, category, and impact keywords.
5. Assess risk and human review requirements.
6. Build diagnosis, remediation, validation, escalation, rollback, and similar incident sections.

## Safety Layer

`app/opsmind/safety.py` assigns risk based on destructive operations, production changes, and blast-radius terms such as `all`, `region`, `cluster`, `namespace`, `every`, and `global`. High-risk incidents always produce human approval warnings.

OpsMind never executes infrastructure changes. It only recommends actions and requires a rollback plan before remediation.
