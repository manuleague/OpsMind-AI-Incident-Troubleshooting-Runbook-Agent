from app.opsmind.analyzer import IncidentAnalyzer
from app.opsmind.config import Settings
from app.opsmind.models import IncidentInput


def test_analyzer_returns_cited_response() -> None:
    settings = Settings(
        retrieval_mode="local",
        kb_path=__import__("pathlib").Path("knowledge_base/runbooks"),
        foundry_iq_endpoint="",
        foundry_iq_knowledge_base_id="",
        foundry_iq_api_key="",
        foundry_iq_api_version="2025-11-01-preview",
    )
    analyzer = IncidentAnalyzer(settings)

    response = analyzer.analyze(
        IncidentInput(
            description="Checkout API returns 502 after deployment",
            severity="high",
            environment="prod",
        )
    )

    assert response.citations
    assert response.likely_category in {"application", "kubernetes"}
    assert response.remediation
