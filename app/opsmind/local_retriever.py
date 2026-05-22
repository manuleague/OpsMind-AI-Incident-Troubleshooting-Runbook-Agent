from __future__ import annotations

import re
from pathlib import Path

from app.opsmind.models import RetrievedSource


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> set[str]:
    stopwords = {
        "the", "and", "for", "with", "that", "this", "after", "from", "into",
        "cannot", "issue", "alert", "service", "user", "users", "error",
    }
    return {token for token in TOKEN_RE.findall(text.lower()) if token not in stopwords}


class LocalMarkdownRetriever:
    def __init__(self, kb_path: Path) -> None:
        self.kb_path = kb_path

    def search(self, query: str, top_k: int = 4) -> list[RetrievedSource]:
        query_tokens = tokenize(query)
        results: list[RetrievedSource] = []

        for path in sorted(self.kb_path.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            tokens = tokenize(content)
            overlap = query_tokens & tokens
            score = len(overlap) / max(len(query_tokens), 1)
            if score <= 0:
                continue

            title = self._extract_title(content, path)
            source_id = path.stem
            results.append(
                RetrievedSource(
                    source_id=source_id,
                    title=title,
                    path=str(path),
                    content=content,
                    score=score,
                    metadata={"retriever": "local_markdown", **self._extract_metadata(content)},
                )
            )

        return sorted(results, key=lambda source: source.score, reverse=True)[:top_k]

    @staticmethod
    def _extract_title(content: str, path: Path) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ").strip()
        return path.stem

    @staticmethod
    def _extract_metadata(content: str) -> dict[str, str]:
        metadata: dict[str, str] = {}
        for line in content.splitlines():
            stripped = line.strip()
            if stripped in {"---", ""}:
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            if key in {
                "doc_id",
                "doc_type",
                "category",
                "severity",
                "service_area",
                "environment",
                "owner_team",
                "risk_level",
                "last_reviewed",
            }:
                metadata[key] = value.strip().lower()
        return metadata
