---
doc_id: RB-SSL-001
doc_type: runbook
title: SSL Certificate Expiration Warning
category: security
severity: high
service_area: tls endpoints
environment: all
owner_team: security platform
risk_level: medium
last_reviewed: 2026-05-22
---

# RB-SSL-001 SSL Certificate Expiration Warning

## Retrieval Keywords

ssl expiry, tls certificate expiration, certificate warning, x509, key vault certificate, load balancer certificate, ingress tls

## Symptoms

- Certificate expires within the alert threshold, commonly 30 days.
- Synthetic checks fail certificate validation.
- Browser or API clients report certificate warnings.
- A gateway, ingress, or load balancer presents an unexpected certificate.

## Diagnostic Steps

1. Identify endpoint, port, certificate common name, subject alternative names, issuer, and expiry date.
2. Confirm whether the certificate is managed by automation, Key Vault, ingress controller, or manual upload.
3. Validate the full certificate chain, including intermediate certificates.
4. Identify every binding that presents the certificate: gateway, app service, ingress, CDN, or load balancer.
5. Check recent certificate renewal jobs and deployment failures.

## Likely Causes

- Renewal automation failed.
- Certificate was renewed but not bound to the production endpoint.
- Intermediate certificate chain is incomplete.
- Multiple endpoints use the same certificate but only some bindings were updated.

## Safe Remediation

- Renew through the approved certificate authority or automation path.
- Update production bindings only during an approved change window or incident approval flow.
- Keep the previous certificate available until validation completes.
- Do not export, email, or paste private keys into tickets or chat.

## Validation Checks

- External TLS check shows the expected certificate and expiry date.
- Certificate chain validates from an external client.
- Synthetic checks pass.
- Expiry alert clears.

## Escalation Triggers

- Private keys, wildcard certificates, payment endpoints, or production gateways are involved.
- Certificate replacement requires DNS, gateway, or load balancer changes.
- Automation repeatedly renews but fails to bind the certificate.

