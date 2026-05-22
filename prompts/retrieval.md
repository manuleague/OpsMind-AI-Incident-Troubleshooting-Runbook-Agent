# Retrieval Prompt

Given the incident description, retrieve operational sources that help diagnose and safely remediate the issue.

Retrieve:

- runbooks matching the symptom
- known incident documents with similar failure modes
- diagnostic checklists
- validation steps
- rollback or mitigation guidance
- escalation policies

Prefer documents with explicit symptoms, causes, commands, metrics, safe remediation, and post-remediation validation.

Return source title, source ID, content snippet, score, and citation path.

