# Architecture Recommendation

## Best Stack

Use a simple Python app with Streamlit for the UI, a small incident analysis service, and a retrieval abstraction that calls Foundry IQ in production or local markdown files in demo mode.

This is the best hackathon tradeoff because it is:

- quick to build
- easy to demo
- simple for judges to understand
- clearly centered on Foundry IQ
- safe because it recommends actions but does not execute them

## Flow

1. Engineer enters an incident description, severity, and environment.
2. The app builds a retrieval query.
3. Retrieval layer calls Foundry IQ knowledge base.
4. Retrieved sources are normalized into citations.
5. Incident analyzer classifies the issue and prepares a structured response.
6. Safety layer labels risk and adds human review warnings.
7. UI renders the final response and citation snippets.

## Where Foundry IQ Fits

Foundry IQ is the knowledge layer. It should index operational runbooks, known incident records, postmortems, and escalation guides. The agent depends on Foundry IQ to retrieve grounded evidence and citation-bearing source snippets.

## Keep It Simple

Do not build a heavy backend unless time remains. Streamlit plus Python services is enough for a polished solo-builder demo.

