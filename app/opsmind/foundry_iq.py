from __future__ import annotations

import logging
from typing import Any

from app.opsmind.config import Settings
from app.opsmind.models import RetrievedSource


logger = logging.getLogger(__name__)


class FoundryIQClient:
    """Retrieves grounded knowledge from the Foundry Agent (foundry-agent)
    using the azure-ai-agents SDK or REST fallback.

    Required .env variables:
        AZURE_AI_PROJECT_CONNECTION_STRING  - e.g.
            https://opsmind-foundry.services.ai.azure.com/api/projects/proj-default
        FOUNDRY_IQ_API_KEY                  - API key from Foundry Home
        FOUNDRY_IQ_AUTH_MODE                - "apikey" (recommended)
        FOUNDRY_IQ_API_VERSION              - keep at 2025-05-15-preview
    """

    AGENT_NAME = "foundry-agent"

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

        logger.info("Foundry IQ: querying agent '%s'", self.AGENT_NAME)
        logger.debug("Foundry IQ query: %s", query)

        try:
            return self._agents_sdk_search(query=query, top_k=top_k)
        except ImportError as exc:
            logger.warning("azure-ai-agents not installed; falling back to REST: %s", exc)
        except Exception:
            logger.exception("Foundry IQ agents SDK failed; falling back to REST")

        return self._rest_chat_search(query=query, top_k=top_k)

    # ------------------------------------------------------------------
    # Path A: azure-ai-agents SDK  (pip install azure-ai-agents)
    # ------------------------------------------------------------------

    def _agents_sdk_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        """Use AgentsClient with api-key header credential."""
        from azure.ai.agents import AgentsClient  # type: ignore
        from azure.ai.agents.models import MessageTextContent  # type: ignore
        from azure.core.credentials import AzureKeyCredential

        endpoint = self._base_endpoint()
        api_key = self.settings.foundry_iq_api_key

        # AgentsClient accepts keyword_only 'api_key' in azure-ai-agents >= 1.0
        # which sets the api-key header directly (no OAuth token needed).
        try:
            client = AgentsClient(endpoint=endpoint, api_key=api_key)
        except TypeError:
            # Older builds: pass a SyncTokenCredential shim
            client = AgentsClient(
                endpoint=endpoint,
                credential=_ApiKeyShim(api_key),
            )

        with client:
            agent = self._resolve_agent(client)

            thread = client.threads.create()
            client.messages.create(
                thread_id=thread.id,
                role="user",
                content=(
                    f"Retrieve the top {top_k} runbooks most relevant to this incident. "
                    f"For each, include: doc_id, title, diagnostic steps, remediation steps. "
                    f"Incident: {query}"
                ),
            )

            run = client.runs.create_and_process(
                thread_id=thread.id, agent_id=agent.id
            )
            logger.info("Agent run status: %s", run.status)

            messages = client.messages.list(thread_id=thread.id)
            for msg in messages:
                if msg.role == "assistant":
                    text = ""
                    for block in msg.content:
                        if isinstance(block, MessageTextContent):
                            text += block.text.value
                    if text:
                        return [RetrievedSource(
                            source_id="foundry-agent-response",
                            title="Foundry Agent Response",
                            path="foundry-agent",
                            content=text,
                            score=1.0,
                            metadata={"retriever": "foundry_iq_agents_sdk"},
                        )]
        return []

    def _resolve_agent(self, client: Any) -> Any:
        for agent in client.list_agents():
            if agent.name == self.AGENT_NAME:
                logger.info("Resolved agent id: %s", agent.id)
                return agent
        raise RuntimeError(
            f"Agent '{self.AGENT_NAME}' not found. "
            "Check Foundry portal > Build > Agents."
        )

    # ------------------------------------------------------------------
    # Path B: REST fallback — Azure OpenAI chat completions
    # ------------------------------------------------------------------

    def _rest_chat_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        import requests

        url = (
            f"{self._openai_endpoint()}/openai/deployments/gpt-4o/chat/completions"
            f"?api-version=2025-01-01-preview"
        )

        system_prompt = (
            "You are OpsMind AI, an expert incident troubleshooting assistant for "
            "cloud and DevOps engineers. When given an incident, retrieve and "
            "summarise the most relevant runbooks. Include doc_id, title, "
            "diagnostic steps, and remediation actions. Always cite your sources."
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
                            f"Top {top_k} runbooks for: {query}. "
                            "Include doc_id, title, diagnostic steps, remediation."
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
        logger.info("Foundry REST returned %d chars", len(content))

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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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


class _ApiKeyShim:
    """Minimal credential shim that injects api-key header for azure-ai-agents
    builds that expect a credential object instead of a bare api_key kwarg."""

    def __init__(self, key: str) -> None:
        self._key = key

    def get_token(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ARG002
        raise NotImplementedError("_ApiKeyShim does not support OAuth token flow")

    def update_request(self, request: Any) -> None:  # called by some pipeline policies
        request.http_request.headers["api-key"] = self._key
