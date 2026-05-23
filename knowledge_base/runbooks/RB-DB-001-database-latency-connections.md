---
doc_id: RB-DB-001
doc_type: runbook
title: Database Latency and Connection Pool Exhaustion
category: database
severity: high
service_area: relational databases
environment: all
owner_team: data platform
risk_level: high
last_reviewed: 2026-05-23
---

# RB-DB-001 Database Latency and Connection Pool Exhaustion

## Retrieval Keywords

database latency, sql timeout, connection pool exhaustion, deadlock, lock wait, blocking query, slow query, max connections, azure sql

## Symptoms

- Application requests fail with SQL timeout or connection pool exhausted errors.
- Database CPU, DTU, vCore, lock waits, or active sessions are elevated.
- Query latency increases across multiple application instances.
- Error rate increases without a corresponding frontend deployment.

## Diagnostic Steps

1. Confirm whether the issue affects one service, one database, or all services sharing the database.
2. Check active connections, connection pool usage, and failed connection attempts.
3. Inspect long-running queries, blocking sessions, deadlocks, and lock waits.
4. Compare database CPU, memory, I/O, DTU, and storage metrics against the incident window.
5. Review recent schema migrations, index changes, application releases, and traffic spikes.

## Likely Causes

- Connection pool exhaustion caused by slow queries or leaked connections.
- Blocking transaction or deadlock storm.
- Database resource saturation.
- Recent schema, index, or query-plan regression.

## Safe Remediation

- Kill blocking sessions only after data owner approval and impact review.
- Roll back application query changes only after compatibility is confirmed.
- Scale database capacity only after confirming quota, cost, and rollback path.
- Do not restart a production database without incident commander approval.

## Validation Checks

- Connection success rate returns to baseline.
- Query latency returns to normal.
- Blocking locks and deadlocks stop increasing.
- Application error rate returns to baseline.

## Escalation Triggers

- Multiple services share the impacted database.
- Remediation requires killing sessions, failover, restart, or schema rollback.
- Customer-facing transactions are failing.
