from __future__ import annotations

from app.opsmind.models import TroubleshootingResponse


def to_markdown(response: TroubleshootingResponse) -> str:
    citations_by_id = {citation.source_id: citation for citation in response.citations}

    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- No grounded item available."

    citation_lines = []
    for citation in citations_by_id.values():
        citation_lines.append(
            f"- [{citation.source_id}] {citation.title} - {citation.path}\n"
            f"  Snippet: {citation.snippet}"
        )

    return "\n\n".join(
        [
            f"## Incident Summary\n{response.incident_summary}",
            f"## Classification\n- Category: {response.likely_category}\n- Confidence: {response.confidence_label}\n- Risk: {response.risk.value}\n- Blast radius: {response.blast_radius}",
            f"## Grounded Evidence\n{bullets(response.evidence)}",
            f"## Likely Diagnosis\n{bullets(response.diagnosis)}",
            f"## Recommended Remediation\n{bullets(response.remediation)}",
            f"## Validation Checks\n{bullets(response.validation)}",
            f"## Escalation Triggers\n{bullets(response.escalation)}",
            f"## Rollback Plan\n{response.rollback_plan}",
            f"## Similar Incidents\n{bullets(response.similar_incidents)}",
            f"## Requires Human Review\n{bullets(response.human_review_required)}",
            f"## Citations\n{chr(10).join(citation_lines) if citation_lines else '- No citations available.'}",
        ]
    )
