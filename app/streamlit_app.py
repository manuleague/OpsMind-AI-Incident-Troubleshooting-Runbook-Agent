from __future__ import annotations

import time

import streamlit as st

from app.opsmind.analyzer import IncidentAnalyzer
from app.opsmind.config import load_settings
from app.opsmind.models import IncidentInput, TroubleshootingResponse


GITHUB_URL = "https://github.com/manuleague/OpsMind-AI-Incident-Troubleshooting-Runbook-Agent"

SEVERITY_COLORS = {
    "sev1": "#dc2626",
    "sev2": "#ea580c",
    "sev3": "#ca8a04",
    "sev4": "#16a34a",
    "low": "#16a34a",
    "unknown": "#64748b",
}


def badge(label: str, color: str) -> str:
    return (
        f"<span style='display:inline-block;background:{color};color:white;"
        "border-radius:999px;padding:0.22rem 0.65rem;font-size:0.8rem;"
        "font-weight:700;margin-left:0.35rem;'>"
        f"{label}</span>"
    )


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def render_sidebar() -> None:
    settings = load_settings()
    mode_color = "#15803d" if settings.retrieval_mode == "foundry" else "#c2410c"

    st.sidebar.title("OpsMind AI")
    st.sidebar.caption("Powered by Microsoft Foundry IQ")
    st.sidebar.markdown(badge(settings.retrieval_mode.upper(), mode_color), unsafe_allow_html=True)

    with st.sidebar.expander("How It Works", expanded=False):
        st.markdown(
            "1. OpsMind sends the incident to Foundry IQ or local runbooks.\n"
            "2. Retrieved runbook chunks become cited evidence.\n"
            "3. The analyzer classifies, reasons, recommends, validates, and flags risk."
        )

    st.sidebar.markdown(f"[GitHub repository]({GITHUB_URL})")
    st.sidebar.divider()
    st.sidebar.subheader("Recent Incidents")
    recent_incidents = st.session_state.get("recent_incidents", [])
    if recent_incidents:
        for item in recent_incidents[-3:][::-1]:
            st.sidebar.caption(item)
    else:
        st.sidebar.caption("No incidents analyzed yet.")


def render_summary(result: TroubleshootingResponse, severity: str) -> None:
    severity_color = SEVERITY_COLORS.get(severity, "#64748b")
    st.markdown(
        f"### Incident Summary {badge(severity.upper(), severity_color)}",
        unsafe_allow_html=True,
    )
    st.info(result.incident_summary)
    st.warning(f"Blast radius: {result.blast_radius}")


def render_result(result: TroubleshootingResponse, severity: str) -> None:
    render_summary(result, severity)

    category_col, confidence_col, risk_col = st.columns(3)
    category_col.metric("Category", result.likely_category.title())
    confidence_col.metric("Confidence", result.confidence_label)
    risk_col.metric("Risk", result.risk.value.upper())

    if result.human_review_required:
        st.error(
            bullets(result.human_review_required)
            + "\n\n**Do not proceed without human approval.**"
        )

    with st.expander("📄 Retrieved Evidence & Citations", expanded=False):
        st.markdown(bullets(result.evidence))
        st.divider()
        for citation in result.citations:
            st.markdown(f"- [{citation.source_id}] {citation.title} - `{citation.path}`")

    with st.expander("🔍 Diagnosis", expanded=True):
        st.markdown(bullets(result.diagnosis))

    with st.expander("🔧 Remediation Steps", expanded=True):
        st.warning("All steps are recommendations only. Validate before executing.")
        st.markdown("\n".join(result.remediation))

    with st.expander("✅ Validation Checks", expanded=False):
        st.markdown(bullets(result.validation))

    with st.expander("🚀 Escalation Triggers", expanded=False):
        st.markdown(bullets(result.escalation))

    with st.expander("↩️ Rollback Plan", expanded=True):
        st.info(result.rollback_plan)

    with st.expander("🧩 Similar Incidents", expanded=False):
        st.markdown(bullets(result.similar_incidents))


def analyze_incident(description: str, severity: str, environment: str) -> TroubleshootingResponse:
    settings = load_settings()
    analyzer = IncidentAnalyzer(settings)

    with st.status("🔍 Querying Foundry IQ knowledge base...", expanded=True) as status:
        time.sleep(0.2)
        status.update(label="🧠 Classifying incident...", state="running")
        result = analyzer.analyze(
            IncidentInput(
                description=description,
                severity=severity,
                environment=environment,
            )
        )
        status.update(label="⚙️ Building remediation plan...", state="running")
        time.sleep(0.2)
        status.update(label="Analysis complete.", state="complete")
    return result


def main() -> None:
    st.set_page_config(
        page_title="OpsMind AI | Incident Agent",
        page_icon="🧠",
        layout="wide",
    )

    if "recent_incidents" not in st.session_state:
        st.session_state.recent_incidents = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_severity" not in st.session_state:
        st.session_state.last_severity = "unknown"

    render_sidebar()

    st.title("OpsMind AI | Incident Agent")
    st.caption("Grounded incident troubleshooting with cited runbook guidance.")

    st.header("Describe Your Incident")
    description = st.text_area(
        "Incident description",
        placeholder="Linux VM CPU spike above 95% for 10 minutes, application response time degraded",
        height=170,
    )

    severity_col, environment_col = st.columns(2)
    with severity_col:
        severity = st.selectbox("Severity", ["unknown", "sev1", "sev2", "sev3", "sev4", "low"])
    with environment_col:
        environment = st.selectbox("Environment", ["unknown", "production", "staging", "development"])

    if st.button("Analyze Incident", type="primary", use_container_width=True):
        if len(description.strip()) < 10:
            st.error("Incident description must be at least 10 characters.")
        else:
            try:
                result = analyze_incident(description.strip(), severity, environment)
                st.session_state.last_result = result
                st.session_state.last_severity = severity
                st.session_state.recent_incidents.append(description.strip()[:90])
                st.session_state.recent_incidents = st.session_state.recent_incidents[-3:]
            except Exception as exc:
                st.error(f"OpsMind could not analyze this incident: {exc}")

    if st.session_state.last_result:
        st.divider()
        render_result(st.session_state.last_result, st.session_state.last_severity)

    st.markdown(
        "<p style='color:#6b7280;font-size:0.82rem;margin-top:2rem;'>"
        "OpsMind AI | Agents League Hackathon 2026 | Powered by Microsoft Foundry IQ"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
