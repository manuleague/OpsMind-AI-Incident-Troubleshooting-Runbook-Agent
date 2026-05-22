# Foundry IQ Knowledge Base Design

## Document Types

Include:

- operational runbooks
- known error guides
- incident postmortems
- deployment rollback procedures
- service dependency maps
- monitoring alert definitions
- escalation policies
- validation checklists

## Structure

Each document should include:

- title
- category
- severity
- service area
- symptoms
- diagnostic steps
- safe remediation
- validation
- escalation
- owner or review group
- last reviewed date

## Naming Convention

Use:

`RB-<AREA>-<NUMBER>-<short-topic>.md`

Examples:

- `RB-CPU-001-linux-vm-cpu-spike.md`
- `RB-K8S-001-pod-crashloop.md`
- `RB-HTTP-001-app-502-503.md`

## Metadata Fields

Recommended metadata:

- `doc_type`: runbook, postmortem, known_issue, escalation_policy
- `category`: compute, networking, application, storage, kubernetes, security
- `severity`: low, medium, high, critical
- `service_area`
- `owner_team`
- `last_reviewed`
- `environment`: prod, staging, dev, all
- `risk_level`

## Retrieval Quality Tips

- Use concrete symptom phrases that match alert language.
- Include common error strings such as 502, NXDOMAIN, CrashLoopBackOff, disk usage, and certificate expiry.
- Separate diagnosis from remediation.
- Add explicit validation checks.
- Include "do not" safety warnings.
- Keep each runbook focused on one failure mode.
- Update docs after every real incident.

## Ingestion Checklist

- Validate source documents are current.
- Remove secrets and customer data.
- Add metadata consistently.
- Confirm document owners.
- Test retrieval with 10 to 20 realistic incident queries.
- Check that citations point to the expected docs.
- Review access controls for sensitive operational docs.

