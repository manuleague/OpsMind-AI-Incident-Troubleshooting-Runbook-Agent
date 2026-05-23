from __future__ import annotations

import logging
from typing import Any

from app.opsmind.config import Settings
from app.opsmind.models import RetrievedSource


logger = logging.getLogger(__name__)


class FoundryIQClient:
    """Retrieves grounded knowledge from the Foundry Agent (foundry-agent)
    using the azure-ai-agents SDK (AgentsClient + threads/messages API).

    Falls back to direct REST against the Foundry project endpoint if the
    azure-ai-agents package is not installed.

    Required .env variables:
        AZURE_AI_PROJECT_CONNECTION_STRING  - project endpoint, e.g.
            https://opsmind-foundry.services.ai.azure.com/api/projects/proj-default
        FOUNDRY_IQ_API_KEY                  - API key from Foundry Home
        FOUNDRY_IQ_KNOWLEDGE_BASE_ID        - agent ID shown in Foundry portal
                                              (use the agent name: foundry-agent)
        FOUNDRY_IQ_AUTH_MODE                - "apikey" (recommended) or "credential"
        FOUNDRY_IQ_API_VERSION              - keep at 2025-05-15-preview
    """

    # The agent name as it appears in Foundry portal
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
            logger.warning(
                "azure-ai-agents SDK not installed; falling back to REST: %s", exc
            )
        except Exception:
            logger.exception("Foundry IQ agents SDK failed; falling back to REST")

        return self._rest_chat_search(query=query, top_k=top_k)

    # ------------------------------------------------------------------
    # Path A: azure-ai-agents SDK  (pip install azure-ai-agents)
    # ------------------------------------------------------------------

    def _agents_sdk_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        """Use AgentsClient to create a thread, run the foundry-agent,
        and parse its reply as retrieved sources."""
        from azure.ai.agents import AgentsClient  # type: ignore
        from azure.ai.agents.models import MessageTextContent  # type: ignore
        from azure.core.credentials import AzureKeyCredential

        endpoint = self._base_endpoint()
        credential = AzureKeyCredential(self.settings.foundry_iq_api_key)

        with AgentsClient(endpoint=endpoint, credential=credential) as client:
            # Resolve agent by name
            agent = self._resolve_agent(client)

            # Create thread + message
            thread = client.threads.create()
            client.messages.create(
                thread_id=thread.id,
                role="user",
                content=(
                    f"Retrieve the top {top_k} runbook(s) most relevant to this "
                    f"incident. Return each runbook title, its doc_id, and a "
                    f"diagnostic summary. Incident: {query}"
                ),
            )

            # Run and wait
            run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            logger.info("Agent run status: %s", run.status)

            # Extract text from last assistant message
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
        """Find the foundry-agent by name from the agents list."""
        for agent in client.list_agents():
            if agent.name == self.AGENT_NAME:
                logger.info("Resolved agent id: %s", agent.id)
                return agent
        raise RuntimeError(
            f"Agent '{self.AGENT_NAME}' not found in Foundry project. "
            "Check the agent name in Foundry portal > Build > Agents."
        )

    # ------------------------------------------------------------------
    # Path B: REST fallback via Azure OpenAI chat completions endpoint
    # ------------------------------------------------------------------

    def _rest_chat_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        """Call the Azure OpenAI chat completions endpoint that backs the
        Foundry project. Uses the project's OpenAI endpoint derived from
        AZURE_AI_PROJECT_CONNECTION_STRING."""
        import requests

        openai_endpoint = self._openai_endpoint()
        url = (
            f"{openai_endpoint}/openai/deployments/gpt-4o/chat/completions"
            f"?api-version=2025-01-01-preview"
        )

        system_prompt = (
            "You are OpsMind AI, an expert incident troubleshooting assistant. "
            "When given an incident description, retrieve and summarise the most "
            "relevant runbooks. Include doc_id, title, diagnostic steps, and "
            "remediation actions. Always cite your sources."
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Retrieve top {top_k} runbooks for: {query}. "
                        "Return title, doc_id, and a brief diagnostic + remediation summary."
                    ),
                },
            ],
            "max_tokens": 1200,
            "temperature": 0.1,
        }

        response = requests.post(
            url,
            headers={
                "api-key": self.settings.foundry_iq_api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        logger.info("Foundry REST chat fallback returned %d chars", len(content))

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
        """Return base Foundry endpoint (no /api/projects path)."""
        raw = (self.settings.azure_ai_project_connection_string or "").rstrip("/")
        return raw.split("/api/projects")[0] if "/api/projects" in raw else raw

    def _openai_endpoint(self) -> str:
        """Return the Azure OpenAI endpoint for REST fallback.
        Converts https://opsmind-foundry.services.ai.azure.com
        to      https://opsmind-foundry.openai.azure.com
        """
        base = self._base_endpoint()
        # Replace .services.ai.azure.com with .openai.azure.com
        if ".services.ai.azure.com" in base:
            return base.replace(".services.ai.azure.com", ".openai.azure.com")
        return base

    @staticmethod
    def _is_azure_exception(exc: Exception, name: str) -> bool:
        return exc.__class__.__name__ == name
