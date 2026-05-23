from __future__ import annotations

import logging

from app.opsmind.config import Settings, load_settings
from app.opsmind.foundry_iq import FoundryIQClient
from app.opsmind.local_retriever import LocalMarkdownRetriever
from app.opsmind.models import ConfidenceLevel, IncidentInput, RetrievedSource, TroubleshootingResponse
from app.opsmind.safety import assess_risk, human_review_warnings


logger = logging.getLogger(__name__)


CATEGORY_KEYWORDS = {
    "kubernetes": [
        "pod", "crashloop", "crash", "kubernetes", "k8s", "deployment",
        "aks", "node", "notready", "not ready", "namespace", "helm",
        "kubectl", "evicted", "oomkilled", "pending", "imagepullbackoff",
        "container", "replicaset", "daemonset", "statefulset", "ingress",
    ],
    "database": [
        "sql", "database", "db", "connection", "timeout", "query",
        "postgres", "postgresql", "mysql", "cosmos", "cosmosdb",
        "deadlock", "transaction", "replication", "replica", "primary",
        "connection pool", "max connections", "azure sql", "rds",
        "slow query", "lock", "blocking", "dtus",
    ],
    "application": [
        "502", "503", "500", "gateway", "api", "app", "latency",
        "response time", "error rate", "exception", "crash", "oom",
        "memory", "heap", "service", "endpoint", "health check",
        "deployment", "release", "rollback", "version",
    ],
    "compute": [
        "cpu", "vm", "load", "unreachable", "ssh", "virtual machine",
        "high cpu", "spike", "throttle", "rdp", "boot", "reboot",
        "instance", "scale set", "vmss", "host", "hypervisor",
        "linux vm", "windows vm", "compute",
    ],
    "storage": [
        "disk", "space", "filesystem", "volume", "storage",
        "blob", "bucket", "s3", "iops", "throughput",
        "403", "forbidden", "access denied", "permission",
        "sas", "container", "quota", "inode", "full",
    ],
    "networking": [
        "dns", "resolve", "connectivity", "nsg", "route",
        "network", "firewall", "latency", "packet loss", "vnet",
        "subnet", "ip", "port", "tcp", "udp", "vpn",
        "expressroute", "load balancer", "traffic manager",
    ],
    "security": [
        "ssl", "certificate", "tls", "expiry", "expired",
        "auth", "unauthorized", "401", "403", "token",
        "secret", "key vault", "keyvault", "credential",
        "rotation", "rbac", "permission", "access",
    ],
}


class IncidentAnalyzer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self.local = LocalMarkdownRetriever(self.settings.kb_path)
        self.foundry = FoundryIQClient(self.settings)

    def analyze(self, incident: IncidentInput) -> TroubleshootingResponse:
        logger.info("Analyzing incident: %s", incident.description[:80])
        sources = self._retrieve(incident)
        logger.info("Retrieval mode: %s, results: %d", self.settings.retrieval_mode, len(sources))
        category = classify_incident(incident.description, sources)
        confidence = confidence_from_sources(sources)
        combined_text = "\n".join(source.content for source in sources)
        risk = assess_risk(incident.description, combined_text)
        citations = [source.citation() for source in sources]
        blast_radius = estimate_blast_radius(incident, category)
        rollback_plan = "Define rollback plan: [describe how to undo each remediation step]"
        similar_incidents = build_similar_incidents(sources)

        if not sources:
            logger.warning("No sources retrieved for: %s", incident.description[:80])
            return TroubleshootingResponse(
                incident_summary=summarize_incident(incident),
                likely_category=category,
                confidence=ConfidenceLevel.LOW,
                confidence_label=ConfidenceLevel.LOW.value.upper(),
                risk=risk,
                blast_radius=blast_radius,
                evidence=["No sufficiently relevant knowledge-base source was retrieved."],
                diagnosis=["Insufficient grounded evidence to provide a specific diagnosis."],
                remediation=["Collect logs, metrics, recent change history, and service ownership context before taking action."],
                validation=["Confirm whether the alert is still active and whether customer impact is ongoing."],
                escalation=["Escalate to the service owner if impact is production-facing or severity is high."],
                human_review_required=human_review_warnings(risk),
                rollback_plan=rollback_plan,
                similar_incidents=[],
                citations=[],
            )

        logger.debug("Category: %s, Confidence: %s", category, confidence)
        return TroubleshootingResponse(
            incident_summary=summarize_incident(incident),
            likely_category=category,
            confidence=confidence,
            confidence_label=confidence.value.upper(),
            risk=risk,
            blast_radius=blast_radius,
            evidence=build_evidence(sources),
            diagnosis=build_diagnosis(incident.description, category, sources),
            remediation=build_remediation(category, sources),
            validation=build_validation(category),
            escalation=build_escalation(incident, category),
            human_review_required=human_review_warnings(risk),
            rollback_plan=rollback_plan,
            similar_incidents=similar_incidents,
            citations=citations,
        )

    def _retrieve(self, incident: IncidentInput) -> list[RetrievedSource]:
        query = f"{incident.description} severity:{incident.severity} environment:{incident.environment}"
        if self.settings.retrieval_mode == "foundry":
            try:
                return self.foundry.search(query, top_k=self.settings.top_k)
            except Exception:
                return self.local.search(query, top_k=self.settings.top_k)
        return self.local.search(query, top_k=self.settings.top_k)


def classify_incident(description: str, sources: list[RetrievedSource]) -> str:
    if sources:
        top_category = sources[0].metadata.get("category")
        if top_category:
            return top_category

    text = " ".join([description, *[source.title for source in sources]]).lower()
    scores = {
        category: sum(1 for keyword in keywords if keyword in text)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best_category, best_score = max(scores.items(), key=lambda item: item[1])
    return best_category if best_score > 0 else "unknown"


def confidence_from_sources(sources: list[RetrievedSource]) -> ConfidenceLevel:
    if not sources:
        return ConfidenceLevel.LOW
    top_score = max(source.score for source in sources)
    if top_score >= 0.35 and len(sources) >= 2:
        return ConfidenceLevel.HIGH
    if top_score >= 0.12:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def summarize_incident(incident: IncidentInput) -> str:
    parts = [incident.description.strip()]
    if incident.severity != "unknown":
        parts.append(f"Severity: {incident.severity}.")
    if incident.environment != "unknown":
        parts.append(f"Environment: {incident.environment}.")
    return " ".join(parts)


def build_evidence(sources: list[RetrievedSource]) -> list[str]:
    return [
        f"Retrieved {source.title} with relevance score {source.score:.2f}. Cite [{source.source_id}]."
        for source in sources
    ]


def build_diagnosis(description: str, category: str, sources: list[RetrievedSource]) -> list[str]:
    cited = ", ".join(f"[{source.source_id}]" for source in sources[:2])
    root_causes = {
        "application": "Likely causes include bad deployment, unhealthy backend targets, dependency timeouts, or connection pool exhaustion.",
        "compute": "Likely causes include host saturation, VM boot or guest-agent issues, blocked management access, or runaway processes.",
        "database": "Likely causes include connection pool exhaustion, long-running queries, locks, deadlocks, or database resource pressure.",
        "kubernetes": "Likely causes include bad image, missing config or secret, failed probes, dependency failure, or resource limits.",
        "networking": "Likely causes include DNS record errors, resolver failures, NSG/firewall denies, route changes, or private zone link issues.",
        "security": "Likely causes include expired certificates, missing intermediates, incorrect bindings, or failed renewal automation.",
        "storage": "Likely causes include log growth, temporary files, inode exhaustion, backups, or application write amplification.",
    }
    alternatives = {
        "application": "This is probably not a pure network outage if backend health, deployment timing, or application logs match the retrieved runbook.",
        "compute": "This is probably not an application-only issue if host CPU, boot diagnostics, or VM health are abnormal.",
        "database": "This is probably not a frontend-only issue if connection pools, query latency, locks, or database health are degraded.",
        "kubernetes": "This is probably not a generic gateway issue if pod restarts, probe failures, or container logs show the failure.",
        "networking": "This is probably not an application deploy issue if DNS, routing, firewall, or resolver checks fail from impacted networks.",
        "security": "This is probably not a capacity issue if TLS validation, certificate expiry, or chain validation is failing.",
        "storage": "This is probably not a CPU issue if filesystem, inode, quota, or write checks are failing.",
    }
    return [
        f"Step 1 - Symptom identification: The description says '{description[:160]}', which aligns with the {category} incident pattern in {cited}.",
        f"Step 2 - Likely root causes: {root_causes.get(category, 'The retrieved sources indicate a known operational failure pattern.')}",
        f"Step 3 - Ruling out alternatives: {alternatives.get(category, 'Avoid assuming a root cause until telemetry and recent changes are checked.')}",
        "Step 4 - Diagnostic order: verify current impact, check recent changes, inspect telemetry/logs, validate dependencies, then choose the lowest-risk remediation.",
    ]


def build_remediation(category: str, sources: list[RetrievedSource]) -> list[str]:
    primary = sources[0].source_id
    common = [
        f"2. Follow the diagnostic order in [{primary}] before making changes.",
        "3. Prefer reversible actions and document every change in the incident timeline.",
        "4. Do not run destructive commands or modify production infrastructure without approval.",
    ]
    category_specific = {
        "kubernetes": "1. If a deployment caused the failure, consider rollback only after confirming image, config, probes, and dependency errors.",
        "database": "1. Check connection pool exhaustion, active queries, blocking locks, and DTU/vCore utilization before restarting services.",
        "application": "1. Check upstream health, gateway/backend pool status, deployment history, and application logs before restart or rollback.",
        "compute": "1. Check host metrics, boot diagnostics, network rules, and guest agent health before resizing or redeploying.",
        "storage": "1. Free safe temporary files only after identifying the consuming path and confirming retention requirements.",
        "networking": "1. Validate DNS records, resolver behavior, TTL, NSG rules, and route tables before changing records or firewall policy.",
        "security": "1. Validate certificate chain, expiry date, bindings, and renewal automation before replacing certificates.",
    }
    return [category_specific.get(category, "1. Gather additional evidence before remediation."), *common]


def build_validation(category: str) -> list[str]:
    checks = {
        "kubernetes": ["Pod restart count stops increasing.", "Readiness probes pass.", "Service error rate returns to baseline."],
        "database": ["Connection success rate returns to baseline.", "Query latency is within SLA.", "No blocking locks or deadlocks remain."],
        "application": ["HTTP 5xx rate drops.", "Synthetic transaction succeeds.", "Gateway/backend health is green."],
        "compute": ["CPU or connectivity metrics recover.", "SSH/RDP or health probes succeed.", "No new platform events appear."],
        "storage": ["Disk usage is below alert threshold.", "Application writes succeed.", "No inode or quota alerts remain."],
        "networking": ["DNS lookup returns expected records.", "Connectivity test passes from impacted subnet.", "No new firewall denies appear."],
        "security": ["Certificate chain validates.", "Expiry alert clears.", "TLS endpoint presents the expected certificate."],
    }
    return checks.get(category, ["Alert clears.", "Customer-facing symptoms are resolved.", "Monitoring stays healthy for one full check interval."])


def build_escalation(incident: IncidentInput, category: str) -> list[str]:
    triggers = [
        "Escalate if customer impact is confirmed and no owner is actively engaged.",
        "Escalate if the recommended action requires production rollback, secret rotation, or firewall/DNS change.",
    ]
    if incident.severity.lower() in {"sev1", "critical", "high"}:
        triggers.append("Severity indicates urgent human review and incident commander involvement.")
    if category == "unknown":
        triggers.append("Escalate because the incident category could not be grounded in the knowledge base.")
    return triggers


def estimate_blast_radius(incident: IncidentInput, category: str) -> str:
    text = f"{incident.description} {incident.severity} {incident.environment}".lower()
    if any(term in text for term in ["global", "all users", "every user", "all regions"]):
        return "Global or all users"
    if "region" in text:
        return "All users in region"
    if category == "kubernetes" and any(term in text for term in ["namespace", "all pods", "deployment"]):
        return "All pods in namespace or deployment"
    if category == "compute" and "vm" in text:
        return "Single VM or VM scale set instance"
    if category == "database":
        return "Services sharing the database"
    if incident.severity.lower() in {"sev1", "critical"}:
        return "Production critical path"
    return "Limited service scope"


def build_similar_incidents(sources: list[RetrievedSource]) -> list[str]:
    incidents: list[str] = []
    for source in sources[:3]:
        category = source.metadata.get("category", "unknown")
        doc_id = source.metadata.get("doc_id", source.source_id)
        incidents.append(f"{doc_id}: {source.title} ({category} pattern)")
    return incidents
