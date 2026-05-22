---
doc_id: RB-K8S-001
doc_type: runbook
title: Kubernetes Pod CrashLoopBackOff
category: kubernetes
severity: high
service_area: kubernetes workloads
environment: all
owner_team: platform engineering
risk_level: high
last_reviewed: 2026-05-22
---

# RB-K8S-001 Kubernetes Pod CrashLoopBackOff

## Retrieval Keywords

kubernetes crashloopbackoff, pod crash loop, restart count, container exits, liveness probe failed, readiness probe failed, image rollout

## Symptoms

- Pod status is CrashLoopBackOff.
- Container restart count increases repeatedly.
- Readiness or liveness probes fail.
- Incident begins after an image rollout, config map change, secret update, or dependency change.

## Diagnostic Steps

1. Inspect pod events, container state, exit code, and termination reason.
2. Review current and previous container logs.
3. Compare image tag, config map, secret, environment variables, and resource limits against the last healthy version.
4. Check readiness and liveness probe paths, ports, delays, and timeout values.
5. Validate dependencies such as database, cache, identity provider, queue, and message broker.

## Likely Causes

- Application crash on startup due to bad config, missing secret, or incompatible image.
- Probe configuration too aggressive for startup behavior.
- Dependency unreachable or authentication failure.
- Resource limit too low causing OOMKilled or repeated termination.

## Safe Remediation

- Roll back the deployment if the new image or configuration clearly introduced the crash and rollback is approved.
- Restore previous config map or secret only after ownership and audit requirements are confirmed.
- Adjust probes or resources only after evidence shows they are the cause.
- Do not delete pods as the only fix unless the root cause is understood.

## Validation Checks

- Restart count stops increasing.
- Pods become ready and stay ready.
- Service error rate and latency return to baseline.
- New logs no longer show startup, auth, config, or dependency failures.

## Escalation Triggers

- Rollback affects production traffic.
- Secrets, migrations, or customer data are involved.
- Logs indicate schema migration, irreversible data change, or widespread dependency outage.

