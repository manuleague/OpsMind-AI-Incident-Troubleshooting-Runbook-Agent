from pathlib import Path

from app.opsmind.local_retriever import LocalMarkdownRetriever


def test_local_retriever_finds_crashloop_runbook() -> None:
    retriever = LocalMarkdownRetriever(Path("knowledge_base/runbooks"))

    results = retriever.search("Kubernetes pod CrashLoopBackOff after deployment", top_k=2)

    assert results
    assert "CrashLoopBackOff" in results[0].content

