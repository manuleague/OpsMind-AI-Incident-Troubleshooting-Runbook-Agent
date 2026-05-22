from __future__ import annotations

from app.opsmind.models import RiskLevel


HIGH_RISK_TERMS = {
    "delete",
    "drop",
    "purge",
    "terminate",
    "reimage",
    "rotate secret",
    "disable firewall",
    "production",
    "payment",
}


def assess_risk(description: str, retrieved_text: str) -> RiskLevel:
    text = f"{description} {retrieved_text}".lower()
    if any(term in text for term in HIGH_RISK_TERMS):
        return RiskLevel.HIGH
    if any(term in text for term in ["restart", "rollback", "scale", "certificate", "dns", "connectivity"]):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def human_review_warnings(risk: RiskLevel) -> list[str]:
    if risk == RiskLevel.HIGH:
        return [
            "Human approval required before production changes, destructive commands, secret rotation, or rollback.",
            "Validate customer impact, blast radius, and rollback plan with the incident commander.",
        ]
    if risk == RiskLevel.MEDIUM:
        return [
            "Human validation required before restarting services, changing DNS, rolling back, or modifying certificates.",
        ]
    return ["Human review recommended before making infrastructure changes."]

