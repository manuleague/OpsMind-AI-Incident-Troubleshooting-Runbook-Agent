---
doc_id: RB-DISK-001
doc_type: runbook
title: Linux Disk Space Critically Low
category: storage
severity: high
service_area: linux virtual machines
environment: all
owner_team: cloud operations
risk_level: high
last_reviewed: 2026-05-22
---

# RB-DISK-001 Linux Disk Space Critically Low

## Retrieval Keywords

disk full, filesystem full, linux disk usage, df, du, inode exhaustion, write failure, log growth, no space left on device

## Symptoms

- Disk usage is above 90 percent.
- Application logs show `No space left on device`.
- Writes fail for logs, temporary files, uploads, or database spill files.
- Log rotation, backup, or package installation fails.

## Diagnostic Steps

1. Identify the impacted mount and usage percentage with `df -h`.
2. Check inode usage with `df -i`.
3. Identify large directories with `du -xh --max-depth=1` from the impacted mount.
4. Review recent log growth, core dumps, temporary files, failed backups, and package caches.
5. Confirm retention, audit, and customer-data requirements before deleting or truncating files.

## Likely Causes

- Application log growth or failed log rotation.
- Temporary files or core dumps accumulating.
- Backup or export files written to the wrong mount.
- Database or queue spill files growing because of downstream failures.

## Safe Remediation

- Compress, archive, or move old logs only when retention policy allows it.
- Clear package caches or temporary files only if they are confirmed safe.
- Increase disk size when growth is expected and online resize is supported.
- Do not delete database files, customer uploads, backups, audit logs, or unknown files without explicit approval.

## Validation Checks

- Disk usage returns below 80 percent or the configured recovery threshold.
- Application writes succeed.
- Inode usage is healthy.
- Disk alert clears and does not immediately re-trigger.

## Escalation Triggers

- Largest files contain customer data, database files, audit logs, or unknown application state.
- Disk growth continues after cleanup.
- Remediation requires deleting or moving production data.

