from __future__ import annotations

import logging
import re
import time
from typing import Any

from app.opsmind.config import Settings
from app.opsmind.models import RetrievedSource


logger = logging.getLogger(__name__)

DOC_ID_RE = re.compile(r"\[([A-Za-z0-9_.:-]+)\]")

# Patterns to extract the real runbook title from Foundry markdown responses
_TITLE_PATTERNS = [
    re.compile(r"\*\*Title:\*\*\s*(.+?)(?:\n|$)"),
    re.compile(r"Runbook Title[:\*\s]+(.+?)(?:\n|$)"),
    re.compile(r"###\s+\*\*(.+?)\*\*"),
    re.compile(r"#{1,3}\s+(.+?)(?:\n|$)"),
]


def _extract_title_from_snippet(snippet: str, fallback: str) -> str:
    """Parse the human-readable runbook title from a Foundry markdown snippet."""
    for pattern in _TITLE_PATTERNS:
        match = pattern.search(snippet)
        if match:
            candidate = match.group(1).strip().rstrip("*")
            # Skip generic or very short matches
            if len(candidate) > 6 and candidate.lower() not in {"runbook", "title", "summary"}:
                return candidate
    return fallback


class FoundryIQClient:
    """Retrieves grounded knowledge from Azure Foundry via REST.

    Uses the Azure OpenAI chat completions endpoint that backs the
    Foundry project (gpt-4o deployment).

    Required .env variables:
        AZURE_AI_PROJECT_CONNECTION_STRING  - project endpoint, e.g.
            https://opsmind-foundry.services.ai.azure.com/api/projects/proj-default
        FOUNDRY_IQ_API_KEY                  - API key from Foundry Home
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return bool(
            self.settings.azure_ai_project_connection_string
            and self.settings.foundry_iq_api_key
        )

    def search(self, query: str, top_k: int = 4) -> list[RetrievedSource]:
        if not self.is_configured():
            raise ValueError(
                "Foundry IQ is not configured. Set AZURE_AI_PROJECT_CONNECTION_STRING "
                "and FOUNDRY_IQ_API_KEY in .env."
            )
        logger.info("Foundry IQ REST: querying gpt-4o for '%s'", query[:60])
        return self._rest_chat_search(query=query, top_k=top_k)

    def _rest_chat_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        url = (
            f"{self._openai_endpoint()}/openai/deployments/gpt-4o/chat/completions"
            "?api-version=2025-01-01-preview"
        )

        system_prompt = (
            "You are OpsMind AI, an expert incident troubleshooting assistant for "
            "cloud and DevOps engineers. When given an incident description, retrieve "
            "and summarise the most relevant runbooks. For each runbook include: "
            "doc_id, title, diagnostic steps, and remediation actions. "
            "Always cite your sources with [doc_id] references."
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Retrieve the top {top_k} runbooks most relevant to "
                        f"this incident. Include doc_id, title, diagnostic steps, "
                        f"chunk text, relevance score, and remediation for each.\n\n"
                        f"Incident: {query}"
                    ),
                },
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
        }
        headers = {
            "api-key": self.settings.foundry_iq_api_key,
            "Content-Type": "application/json",
        }

        response = self._post_with_rate_limit_retry(url=url, headers=headers, payload=payload)
        response.raise_for_status()
        body = response.json()
        content = self._extract_message_content(body)
        logger.info("Foundry IQ REST returned %d chars", len(content))

        sources = self._extract_sources_from_payload(body, fallback_content=content, top_k=top_k)
        logger.info("Foundry IQ REST extracted %d cited source(s)", len(sources))
        return sources

    def _post_with_rate_limit_retry(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> Any:
        import requests

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 429:
            return response

        logger.warning("Foundry IQ REST returned HTTP 429. Retrying once after 3 seconds.")
        time.sleep(3)
        return requests.post(url, headers=headers, json=payload, timeout=30)

    @staticmethod
    def _extract_message_content(payload: dict[str, Any]) -> str:
        choices = payload.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            return "\n".join(str(part.get("text", part)) for part in content)
        return str(content)

    def _extract_sources_from_payload(
        self,
        payload: dict[str, Any],
        fallback_content: str,
        top_k: int,
    ) -> list[RetrievedSource]:
        citations = self._extract_structured_citations(payload)
        if citations:
            return citations[:top_k]

        doc_ids = list(dict.fromkeys(DOC_ID_RE.findall(fallback_content)))
        if doc_ids:
            return [
                RetrievedSource(
                    source_id=doc_id,
                    title=_extract_title_from_snippet(
                        fallback_content, self._title_from_doc_id(doc_id)
                    ),
                    path="foundry-rest",
                    content=fallback_content,
                    score=1.0,
                    metadata={"retriever": "foundry_iq_rest", "doc_id": doc_id},
                )
                for doc_id in doc_ids[:top_k]
            ]

        return [
            RetrievedSource(
                source_id="foundry-grounded-answer",
                title="Foundry IQ grounded answer",
                path="foundry-rest",
                content=fallback_content,
                score=1.0,
                metadata={"retriever": "foundry_iq_rest"},
            )
        ]

    def _extract_structured_citations(self, payload: dict[str, Any]) -> list[RetrievedSource]:
        citation_items: list[dict[str, Any]] = []
        for choice in payload.get("choices", []):
            message = choice.get("message", {})
            context = message.get("context", {})
            citation_items.extend(context.get("citations", []))
            citation_items.extend(message.get("citations", []))
            for annotation in message.get("annotations", []):
                citation = annotation.get("citation") or annotation.get("file_citation")
                if isinstance(citation, dict):
                    citation_items.append(citation)

        sources: list[RetrievedSource] = []
        for index, item in enumerate(citation_items, start=1):
            doc_id = (
                item.get("doc_id")
                or item.get("source_id")
                or item.get("chunk_id")
                or item.get("id")
                or f"foundry-source-{index}"
            )
            chunk_text = (
                item.get("content")
                or item.get("chunk")
                or item.get("text")
                or item.get("snippet")
                or item.get("quote")
                or ""
            )
            raw_title = (
                item.get("title")
                or item.get("filepath")
                or item.get("file_name")
                or item.get("url")
                or self._title_from_doc_id(str(doc_id))
            )
            # Prefer the human-readable title embedded in the chunk text
            title = _extract_title_from_snippet(chunk_text, str(raw_title))
            score = self._coerce_score(
                item.get("score")
                or item.get("relevance_score")
                or item.get("rerank_score")
                or item.get("@search.score")
            )
            path = item.get("url") or item.get("filepath") or item.get("path") or "foundry-rest"
            if not chunk_text:
                continue
            sources.append(
                RetrievedSource(
                    source_id=str(doc_id),
                    title=title,
                    path=str(path),
                    content=str(chunk_text),
                    score=score,
                    metadata={"retriever": "foundry_iq_rest", "doc_id": str(doc_id)},
                )
            )
        return sources

    @staticmethod
    def _coerce_score(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 1.0

    @staticmethod
    def _title_from_doc_id(doc_id: str) -> str:
        clean = doc_id.replace("_", "-").replace(".", "-")
        return clean.replace("-", " ").title()

    def _base_endpoint(self) -> str:
        raw = (self.settings.azure_ai_project_connection_string or "").rstrip("/")
        return raw.split("/api/projects")[0] if "/api/projects" in raw else raw

    def _openai_endpoint(self) -> str:
        base = self._base_endpoint()
        if ".services.ai.azure.com" in base:
            return base.replace(".services.ai.azure.com", ".openai.azure.com")
        return base

    @staticmethod
    def _is_azure_exception(exc: Exception, name: str) -> bool:
        return exc.__class__.__name__ == name
