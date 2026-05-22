# Insufficient Information Fallback Prompt

The retrieved sources are insufficient or not relevant enough to provide a grounded diagnosis.

Respond with:

- a short statement that the answer cannot be fully grounded
- what evidence is missing
- safe diagnostic questions
- low-risk checks the engineer can perform
- escalation guidance

Do not fabricate remediation steps. Do not cite sources that were not retrieved.

