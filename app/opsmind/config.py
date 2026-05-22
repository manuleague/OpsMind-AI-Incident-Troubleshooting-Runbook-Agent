from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience dependency
    load_dotenv = None


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    retrieval_mode: str
    kb_path: Path
    foundry_iq_endpoint: str
    foundry_iq_knowledge_base_id: str
    foundry_iq_api_key: str
    foundry_iq_api_version: str
    top_k: int = 4


def load_settings() -> Settings:
    if load_dotenv:
        load_dotenv(ROOT / ".env")

    return Settings(
        retrieval_mode=os.getenv("OPSMIND_RETRIEVAL_MODE", "local").lower(),
        kb_path=(ROOT / os.getenv("OPSMIND_KB_PATH", "knowledge_base/runbooks")).resolve(),
        foundry_iq_endpoint=os.getenv("FOUNDRY_IQ_ENDPOINT", "").rstrip("/"),
        foundry_iq_knowledge_base_id=os.getenv("FOUNDRY_IQ_KNOWLEDGE_BASE_ID", ""),
        foundry_iq_api_key=os.getenv("FOUNDRY_IQ_API_KEY", ""),
        foundry_iq_api_version=os.getenv("FOUNDRY_IQ_API_VERSION", "2025-11-01-preview"),
        top_k=int(os.getenv("OPSMIND_TOP_K", "4")),
    )

