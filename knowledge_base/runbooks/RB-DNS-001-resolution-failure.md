---
doc_id: RB-DNS-001
doc_type: runbook
title: DNS Resolution Failure
category: networking
severity: high
service_area: dns and private networking
environment: all
owner_team: network platform
risk_level: high
last_reviewed: 2026-05-22
---

# RB-DNS-001 DNS Resolution Failure

## Retrieval Keywords

dns failure, nxdomain, servfail, stale dns, resolver timeout, private dns zone, hostname resolution, api hostname unreachable

## Symptoms

- Clients cannot resolve a service hostname.
- DNS responses include NXDOMAIN, SERVFAIL, timeout, or stale IP address.
- Impact is limited to specific regions, virtual networks, resolvers, or client groups.
- Applications fail when using hostname but may work with direct IP.

## Diagnostic Steps

1. Query authoritative DNS and recursive DNS separately.
2. Compare resolution from impacted and healthy networks.
3. Check recent DNS record changes, zone delegation, and TTL values.
4. Validate private DNS zone links, resolver forwarding rules, and network firewall rules for DNS traffic.
5. Confirm whether the expected record value matches current service endpoint inventory.

## Likely Causes

- Incorrect DNS record or accidental deletion.
- Private DNS zone not linked to the impacted virtual network.
- Resolver forwarding or firewall rule blocks DNS queries.
- TTL propagation delay after a recent record change.

## Safe Remediation

- Revert an incorrect record only after confirming the previous value and current endpoint owner.
- For private DNS, validate zone links before editing records.
- Avoid emergency TTL changes unless approved by the network owner.
- Do not change DNS for production critical paths without rollback and validation steps.

## Validation Checks

- Hostname resolves to expected records from impacted networks.
- Application connectivity succeeds using the hostname.
- Resolver and firewall logs show successful DNS traffic.
- No new NXDOMAIN, SERVFAIL, or timeout errors appear.

## Escalation Triggers

- Authoritative DNS, private zone links, firewall, or resolver infrastructure must be changed.
- The hostname supports production authentication, payment, or customer traffic.
- Multiple regions or virtual networks are impacted.

