from __future__ import annotations

from typing import Any

from app.opsmind.config import Settings
from app.opsmind.models import RetrievedSource


class FoundryIQClient:
    """Thin adapter for Foundry IQ knowledge-base retrieval.

    Foundry IQ is in preview, so this adapter intentionally isolates the REST
    request and response mapping. Update `_build_url`, `_build_payload`, and
    `_normalize_results` if your tenant exposes a different preview shape.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return bool(
            self.settings.foundry_iq_endpoint
            and self.settings.foundry_iq_knowledge_base_id
            and self.settings.foundry_iq_api_key
        )

    def search(self, query: str, top_k: int = 4) -> list[RetrievedSource]:
        if not self.is_configured():
            raise ValueError("Foundry IQ is not configured. Set endpoint, knowledge base ID, and API key.")

        try:
            import requests
        except ImportError as exc:  # pragma: no cover - depends on local environment
            raise RuntimeError("Install requests to use Foundry IQ retrieval mode.") from exc

        response = requests.post(
            self._build_url(),
            headers={
                "api-key": self.settings.foundry_iq_api_key,
                "content-type": "application/json",
            },
            json=self._build_payload(query, top_k),
            timeout=30,
        )
        response.raise_for_status()
        return self._normalize_results(response.json())

    def _build_url(self) -> str:
        kb_id = self.settings.foundry_iq_knowledge_base_id
        version = self.settings.foundry_iq_api_version
        return f"{self.settings.foundry_iq_endpoint}/knowledgebases/{kb_id}:retrieve?api-version={version}"

    @staticmethod
    def _build_payload(query: str, top_k: int) -> dict[str, Any]:
        return {
            "query": query,
            "top": top_k,
            "retrievalMode": "hybrid",
            "includeCitations": True,
        }

    @staticmethod
    def _normalize_results(payload: dict[str, Any]) -> list[RetrievedSource]:
        raw_items = payload.get("results") or payload.get("value") or payload.get("citations") or []
        sources: list[RetrievedSource] = []

        for index, item in enumerate(raw_items, start=1):
            title = item.get("title") or item.get("sourceName") or f"Foundry IQ Source {index}"
            content = item.get("content") or item.get("text") or item.get("snippet") or ""
            path = item.get("url") or item.get("path") or item.get("source") or "foundry-iq"
            source_id = item.get("id") or item.get("sourceId") or f"fiq-{index}"
            score = float(item.get("score") or item.get("@search.score") or 0.0)
            if content:
                sources.append(
                    RetrievedSource(
                        source_id=source_id,
                        title=title,
                        path=path,
                        content=content,
                        score=score,
                        metadata={"retriever": "foundry_iq"},
                    )
                )

        return sources
