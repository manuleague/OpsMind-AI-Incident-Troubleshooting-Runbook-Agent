from __future__ import annotations

import logging

import requests

from app.opsmind.config import Settings
from app.opsmind.models import RetrievedSource


logger = logging.getLogger(__name__)


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

        response = requests.post(
            url,
            headers={
                "api-key": self.settings.foundry_iq_api_key,
                "Content-Type": "application/json",
            },
            json={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Retrieve the top {top_k} runbooks most relevant to "
                            f"this incident. Include doc_id, title, diagnostic steps, "
                            f"and remediation for each.\n\nIncident: {query}"
                        ),
                    },
                ],
                "max_tokens": 1500,
                "temperature": 0.1,
            },
            timeout=30,
        )
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        logger.info("Foundry IQ REST returned %d chars", len(content))

        return [
            RetrievedSource(
                source_id="foundry-rest-response",
                title="Foundry gpt-4o Response",
                path="foundry-rest",
                content=content,
                score=1.0,
                metadata={"retriever": "foundry_iq_rest"},
            )
        ]

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
