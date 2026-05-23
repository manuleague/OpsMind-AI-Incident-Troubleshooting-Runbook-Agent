from __future__ import annotations

from app.opsmind.models import RiskLevel
from app.opsmind.safety import assess_risk


def test_assess_risk_high_for_destructive_action() -> None:
    assert assess_risk("delete production database table", "") == RiskLevel.HIGH


def test_assess_risk_high_for_blast_radius_keyword() -> None:
    assert assess_risk("all users in region cannot reach service", "") == RiskLevel.HIGH


def test_assess_risk_medium_for_operational_change() -> None:
    assert assess_risk("certificate warning on staging endpoint", "") == RiskLevel.MEDIUM


def test_assess_risk_low_for_low_impact_alert() -> None:
    assert assess_risk("minor informational alert on dev endpoint", "") == RiskLevel.LOW
