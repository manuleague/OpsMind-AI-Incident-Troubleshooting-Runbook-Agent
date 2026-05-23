from __future__ import annotations

import logging
from typing import Any

from app.opsmind.config import Settings
from app.opsmind.models import RetrievedSource


logger = logging.getLogger(__name__)

ENDPOINT = "https://opsmind-foundry.services.ai.azure.com/api/projects/proj-default"
AGENT_NAME = "foundry-agent"
AGENT_VERSION = "3"

class FoundryIQClient:
    """Foundry IQ retrieves grounded knowledge-base content for agent responses.

    Configure with `AZURE_AI_PROJECT_CONNECTION_STRING`,
    `FOUNDRY_IQ_KNOWLEDGE_BASE_ID`, `FOUNDRY_IQ_AUTH_MODE`,
    `FOUNDRY_IQ_ENDPOINT`, `FOUNDRY_IQ_API_KEY`, and
    `FOUNDRY_IQ_API_VERSION`. SDK mode uses `DefaultAzureCredential` by
    default, or `AzureKeyCredential` when `FOUNDRY_IQ_AUTH_MODE=apikey`.
    If the `azure-ai-projects` SDK is unavailable or SDK authentication cannot
    be initialized, the client falls back to the REST retrieval endpoint using
    `requests.post()` and the `api-key` header.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        if not self.settings.foundry_iq_knowledge_base_id:
            return False
        if self.settings.azure_ai_project_connection_string:
            return True
        return bool(self.settings.foundry_iq_endpoint and self.settings.foundry_iq_api_key)

    def search(self, query: str, top_k: int = 4) -> list[RetrievedSource]:
        if not self.is_configured():
            raise ValueError(
                "Foundry IQ is not configured. Set AZURE_AI_PROJECT_CONNECTION_STRING "
                "and FOUNDRY_IQ_KNOWLEDGE_BASE_ID, or configure REST fallback variables."
            )

        logger.info(
            "Searching Foundry IQ knowledge base '%s' with auth mode '%s'",
            self.settings.foundry_iq_knowledge_base_id,
            self.settings.foundry_iq_auth_mode,
        )
        logger.debug("Foundry IQ query: %s", query)

        sdk_auth_error: ValueError | None = None
        try:
            results = self._sdk_search(query=query, top_k=top_k)
            logger.info("Foundry IQ SDK returned %d result(s)", len(results))
            return results
        except ImportError as exc:
            logger.warning("azure-ai-projects SDK not installed; falling back to REST: %s", exc)
        except ValueError as exc:
            sdk_auth_error = exc
            logger.exception("Foundry IQ SDK authentication failed; attempting REST fallback")
        except TimeoutError:
            logger.exception("Foundry IQ SDK request timed out")
            raise
        except Exception as exc:
            if self._is_azure_exception(exc, "HttpResponseError"):
                logger.exception("Foundry IQ SDK HTTP response error")
                raise
            if self._is_azure_exception(exc, "ClientAuthenticationError"):
                logger.exception("Foundry IQ SDK client authentication error")
                raise ValueError("Azure authentication failed. Run `az login` or check credentials.") from exc
            logger.exception("Foundry IQ SDK retrieval failed; falling back to REST")

        if sdk_auth_error and not (self.settings.foundry_iq_endpoint and self.settings.foundry_iq_api_key):
            raise sdk_auth_error

        results = self._rest_search(query=query, top_k=top_k)
        logger.info("Foundry IQ REST fallback returned %d result(s)", len(results))
        return results

    def _sdk_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        try:
            from azure.ai.projects import AIProjectClient
            from azure.core.credentials import AzureKeyCredential
            from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
            from azure.identity import DefaultAzureCredential
        except ImportError:
            raise

        if not self.settings.azure_ai_project_connection_string:
            raise RuntimeError("AZURE_AI_PROJECT_CONNECTION_STRING is not set for SDK mode.")

        try:
            if self.settings.foundry_iq_auth_mode == "apikey":
                if not self.settings.foundry_iq_api_key:
                    raise ValueError("FOUNDRY_IQ_API_KEY is required when FOUNDRY_IQ_AUTH_MODE=apikey.")
                credential = AzureKeyCredential(self.settings.foundry_iq_api_key)
                logger.info("Using AzureKeyCredential for Foundry IQ SDK authentication")
            else:
                credential = DefaultAzureCredential()
                logger.info("Using DefaultAzureCredential for Foundry IQ SDK authentication")

            client = AIProjectClient.from_connection_string(
                credential=credential,
                conn_str=self.settings.azure_ai_project_connection_string,
            )
        except ClientAuthenticationError as exc:
            logger.exception("DefaultAzureCredential could not authenticate to Azure AI Foundry")
            raise ValueError("Azure authentication failed. Run `az login` or check credentials.") from exc

        try:
            payload = self._build_sdk_payload(query=query, top_k=top_k)
            raw_results = self._invoke_sdk_knowledge_retrieval(client=client, payload=payload)
            return self._normalize_results(raw_results)
        except ClientAuthenticationError:
            logger.exception("Azure AI Foundry rejected SDK credentials")
            raise
        except HttpResponseError:
            logger.exception("Azure AI Foundry returned an HTTP error")
            raise
        except TimeoutError:
            logger.exception("Azure AI Foundry SDK retrieval timed out")
            raise

    def _invoke_sdk_knowledge_retrieval(self, client: Any, payload: dict[str, Any]) -> Any:
        agents = getattr(client, "agents", None)
        if agents is None:
            raise AttributeError("AIProjectClient does not expose an agents client.")

        knowledge_retrieval = getattr(agents, "knowledge_retrieval", None)
        if knowledge_retrieval is not None:
            for method_name in ("retrieve", "search", "query", "run"):
                method = getattr(knowledge_retrieval, method_name, None)
                if callable(method):
                    logger.debug("Invoking client.agents.knowledge_retrieval.%s", method_name)
                    return method(**payload)

        for method_name in ("knowledge_retrieval", "retrieve_knowledge", "retrieve_from_knowledge_base"):
            method = getattr(agents, method_name, None)
            if callable(method):
                logger.debug("Invoking client.agents.%s", method_name)
                return method(**payload)

        raise AttributeError(
            "Installed azure-ai-projects SDK does not expose a supported Foundry IQ "
            "knowledge retrieval method. Update azure-ai-projects or use REST fallback."
        )

    def _rest_search(self, query: str, top_k: int) -> list[RetrievedSource]:
        if not self.settings.foundry_iq_endpoint or not self.settings.foundry_iq_api_key:
            raise ValueError(
                "REST fallback requires FOUNDRY_IQ_ENDPOINT and FOUNDRY_IQ_API_KEY."
            )

        try:
            import requests
            from requests import Timeout
        except ImportError as exc:
            raise RuntimeError("Install requests to use Foundry IQ REST fallback.") from exc

        try:
            response = requests.post(
                self._build_rest_url(),
                headers={
                    "api-key": self.settings.foundry_iq_api_key,
                    "content-type": "application/json",
                },
                json=self._build_rest_payload(query, top_k),
                timeout=30,
            )
            response.raise_for_status()
        except Timeout:
            logger.exception("Foundry IQ REST fallback request timed out")
            raise
        except Exception as exc:
            logger.exception("Foundry IQ REST fallback request failed")
            raise exc

        return self._normalize_results(response.json())

    def _build_rest_url(self) -> str:
        kb_id = self.settings.foundry_iq_knowledge_base_id
        version = self.settings.foundry_iq_api_version
        return f"{self.settings.foundry_iq_endpoint}/knowledgebases/{kb_id}:retrieve?api-version={version}"

    def _build_sdk_payload(self, query: str, top_k: int) -> dict[str, Any]:
        return {
            "knowledge_base_id": self.settings.foundry_iq_knowledge_base_id,
            "query": query,
            "top_k": top_k,
            "retrieval_mode": "hybrid",
            "include_citations": True,
        }

    @staticmethod
    def _build_rest_payload(query: str, top_k: int) -> dict[str, Any]:
        return {
            "query": query,
            "top": top_k,
            "retrievalMode": "hybrid",
            "includeCitations": True,
        }

    @staticmethod
    def _normalize_results(payload: Any) -> list[RetrievedSource]:
        if hasattr(payload, "as_dict"):
            payload = payload.as_dict()
        elif hasattr(payload, "__dict__") and not isinstance(payload, dict):
            payload = vars(payload)

        if isinstance(payload, list):
            raw_items = payload
        elif isinstance(payload, dict):
            raw_items = (
                payload.get("results")
                or payload.get("value")
                or payload.get("citations")
                or payload.get("documents")
                or []
            )
        else:
            raw_items = []

        sources: list[RetrievedSource] = []
        for index, item in enumerate(raw_items, start=1):
            if hasattr(item, "as_dict"):
                item = item.as_dict()
            elif hasattr(item, "__dict__") and not isinstance(item, dict):
                item = vars(item)
            if not isinstance(item, dict):
                continue

            title = item.get("title") or item.get("sourceName") or item.get("source_name") or f"Foundry IQ Source {index}"
            content = item.get("content") or item.get("text") or item.get("snippet") or item.get("summary") or ""
            path = item.get("url") or item.get("path") or item.get("source") or item.get("source_url") or "foundry-iq"
            source_id = item.get("id") or item.get("sourceId") or item.get("source_id") or f"fiq-{index}"
            score = float(item.get("score") or item.get("@search.score") or item.get("reranker_score") or 0.0)

            if content:
                sources.append(
                    RetrievedSource(
                        source_id=str(source_id),
                        title=str(title),
                        path=str(path),
                        content=str(content),
                        score=score,
                        metadata={"retriever": "foundry_iq"},
                    )
                )

        return sources

    @staticmethod
    def _is_azure_exception(exc: Exception, name: str) -> bool:
        return exc.__class__.__name__ == name
