from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class IncidentInput:
    description: str
    severity: str = "unknown"
    environment: str = "unknown"


@dataclass(frozen=True)
class Citation:
    source_id: str
    title: str
    path: str
    snippet: str


@dataclass(frozen=True)
class RetrievedSource:
    source_id: str
    title: str
    path: str
    content: str
    score: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)

    def citation(self) -> Citation:
        snippet = " ".join(self.content.split())[:260]
        return Citation(
            source_id=self.source_id,
            title=self.title,
            path=self.path,
            snippet=snippet,
        )


@dataclass(frozen=True)
class TroubleshootingResponse:
    incident_summary: str
    likely_category: str
    confidence: ConfidenceLevel
    risk: RiskLevel
    evidence: list[str]
    diagnosis: list[str]
    remediation: list[str]
    validation: list[str]
    escalation: list[str]
    human_review_required: list[str]
    citations: list[Citation]

