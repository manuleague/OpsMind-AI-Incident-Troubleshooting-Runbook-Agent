---
doc_id: RB-CPU-001
doc_type: runbook
title: Linux VM CPU Spike
category: compute
severity: high
service_area: linux virtual machines
environment: all
owner_team: cloud operations
risk_level: medium
last_reviewed: 2026-05-22
---

# RB-CPU-001 Linux VM CPU Spike

## Retrieval Keywords

linux vm cpu spike, high cpu, load average, process saturation, vm latency, health probe failure, runaway process

## Symptoms

- CPU usage is above 85 percent for more than 10 minutes.
- Load average is higher than the available vCPU count.
- Application latency increases or health probes begin failing.
- A recent deployment, cron job, backup, or batch process may correlate with the start time.

## Diagnostic Steps

1. Confirm the alert is still active and identify the impacted VM, region, and service owner.
2. Review CPU breakdown: user CPU, system CPU, iowait, and steal time.
3. Identify top consumers with approved process monitoring tools such as `top`, `ps`, or platform metrics.
4. Check recent deployment, package update, cron, backup, and traffic-change history.
5. Compare application latency, request volume, and dependency errors against the CPU spike window.

## Likely Causes

- Runaway application process or thread pool saturation.
- Batch, backup, antivirus, or indexing job running during peak traffic.
- Traffic increase beyond provisioned capacity.
- I/O wait misread as CPU saturation.

## Safe Remediation

- Pause or reschedule a known non-critical job only after owner approval.
- Scale out or shift traffic only after confirming capacity, quota, and rollback path.
- Restart or terminate a production process only with incident commander approval.
- Do not resize, redeploy, or reimage the VM until data and availability impact are reviewed.

## Validation Checks

- CPU remains below alert threshold for two monitoring intervals.
- Health probes recover.
- User-facing latency returns to baseline.
- No new platform or application errors appear after mitigation.

## Escalation Triggers

- The top process is unknown or security-sensitive.
- Customer impact is confirmed.
- Remediation requires process termination, scale changes, or VM redeployment.

