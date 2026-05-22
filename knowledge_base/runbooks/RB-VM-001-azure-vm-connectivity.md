---
doc_id: RB-VM-001
doc_type: runbook
title: Azure VM Unreachable After Deployment
category: compute
severity: high
service_area: azure virtual machines
environment: all
owner_team: cloud platform
risk_level: high
last_reviewed: 2026-05-22
---

# RB-VM-001 Azure VM Unreachable After Deployment

## Retrieval Keywords

azure vm unreachable, ssh failure, rdp failure, health probe failed, nsg deny, route table, boot diagnostics, guest agent

## Symptoms

- VM is unreachable by SSH or RDP.
- Load balancer or application gateway health probe fails.
- Issue begins after deployment, network change, image update, or firewall policy update.
- Boot diagnostics, guest agent status, or network logs show errors.

## Diagnostic Steps

1. Confirm VM power state, platform health, and recent Azure activity log events.
2. Check boot diagnostics and serial console output if available.
3. Review recent NSG, route table, public IP, load balancer, firewall, and private endpoint changes.
4. Validate source IP, jump host path, and just-in-time access policy.
5. Compare deployment template changes against the last known working state.

## Likely Causes

- NSG or firewall rule blocks management or health probe traffic.
- Route table sends traffic to an unavailable next hop.
- VM boot failure or guest agent issue.
- Deployment changed public IP, NIC, load balancer pool, or probe configuration.

## Safe Remediation

- Revert network rule changes only after identifying the exact deny path.
- Use run command or serial console for diagnostics when normal access is unavailable.
- Restore last known good route, NSG, or probe configuration with cloud platform approval.
- Avoid redeploying, reimaging, or deleting the VM until disk and data impact are reviewed.

## Validation Checks

- SSH or RDP succeeds from an approved source.
- Health probes recover.
- Network deny logs no longer show blocked expected traffic.
- Application or service running on the VM responds normally.

## Escalation Triggers

- Connectivity depends on shared firewall, route table, jump host, or production network policy.
- Redeploy, reimage, or disk-level recovery is being considered.
- VM hosts customer data or a production critical workload.

