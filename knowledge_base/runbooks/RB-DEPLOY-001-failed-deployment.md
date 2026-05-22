---
doc_id: RB-DEPLOY-001
doc_type: runbook
title: Failed Deployment or Bad Release
category: application
severity: high
service_area: release operations
environment: all
owner_team: release engineering
risk_level: high
last_reviewed: 2026-05-22
---

# RB-DEPLOY-001 Failed Deployment or Bad Release

## Retrieval Keywords

failed deployment, bad release, rollback, health check failed, pipeline failure, new version degraded, release outage

## Symptoms

- Deployment fails or completes with degraded service.
- New version fails health checks.
- Error rate, latency, or saturation increases after release.
- Pipeline logs show failed migration, failed test, missing artifact, or configuration error.

## Diagnostic Steps

1. Identify deployment start time, version, commit, artifact, and changed components.
2. Compare health metrics before, during, and after deployment.
3. Review pipeline logs, deployment events, and application startup logs.
4. Check schema migration, feature flag, secret, environment variable, and infrastructure template changes.
5. Confirm whether rollback is compatible with database schema, messages, cache format, and external contracts.

## Likely Causes

- Incompatible application version or missing configuration.
- Failed or partial deployment.
- Feature flag enabled before dependency readiness.
- Database or message contract migration incompatible with rollback.

## Safe Remediation

- Freeze further deployments during active investigation.
- Roll back only if rollback plan is tested and data compatibility is confirmed.
- Disable a risky feature flag when it is the smallest reversible mitigation.
- Do not retry deployment repeatedly without understanding the failure mode.

## Validation Checks

- Previous healthy version or corrected version serves traffic.
- Error rate and latency return to baseline.
- Pipeline status and deployment state are documented in the incident timeline.
- No unresolved migration or compatibility warnings remain.

## Escalation Triggers

- Production rollback is required.
- Schema migration, data contract, or irreversible change is involved.
- Release owner, service owner, or incident commander approval is missing.

