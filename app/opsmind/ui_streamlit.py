from __future__ import annotations

import streamlit as st

from app.opsmind.analyzer import IncidentAnalyzer
from app.opsmind.config import load_settings
from app.opsmind.models import IncidentInput, TroubleshootingResponse


GITHUB_URL = "https://github.com/manuleague/OpsMind-AI-Incident-Troubleshooting-Runbook-Agent"


def render_mode_badge(mode: str) -> None:
    color = "#15803d" if mode == "foundry" else "#c2410c"
    label = "Foundry IQ" if mode == "foundry" else "Local runbooks"
    st.markdown(
        f"""
        <div style="margin: 0.5rem 0 1rem 0;">
            <span style="
                background: {color};
                color: white;
                border-radius: 999px;
                padding: 0.25rem 0.7rem;
                font-size: 0.82rem;
                font-weight: 700;
            ">
                {label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def numbered(items: list[str]) -> str:
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_result(result: TroubleshootingResponse) -> None:
    st.subheader("Incident Summary")
    st.info(result.incident_summary)

    category_col, confidence_col = st.columns(2)
    category_col.metric("Category", result.likely_category.title())
    confidence_col.metric("Confidence", result.confidence.value.title())

    st.subheader("Risk Level")
    if result.risk.value == "high":
        st.warning(f"High risk incident. Risk level: {result.risk.value.upper()}")
    else:
        st.success(f"Risk level: {result.risk.value.upper()}")

    if result.human_review_required:
        st.subheader("⚠️ Human Review Required")
        st.error(
            bullets(result.human_review_required)
            + "\n\n**Do not proceed without human approval.**"
        )

    with st.expander("📄 Retrieved Evidence & Citations", expanded=False):
        st.markdown(bullets(result.evidence))
        st.divider()
        for citation in result.citations:
            st.markdown(f"- [{citation.source_id}] {citation.title} — `{citation.path}`")

    with st.expander("🔍 Diagnosis", expanded=True):
        st.markdown(numbered(result.diagnosis))

    with st.expander("🔧 Remediation", expanded=True):
        st.warning("⚠️ All steps are recommendations only. Validate before executing.")
        st.markdown(numbered(result.remediation))

    with st.expander("✅ Validation", expanded=False):
        st.markdown(bullets(result.validation))

    with st.expander("🚀 Escalation", expanded=False):
        st.markdown(bullets(result.escalation))


def main() -> None:
    st.set_page_config(
        page_title="OpsMind AI — Incident Troubleshooting Agent",
        page_icon="🧠",
        layout="wide",
    )

    settings = load_settings()

    with st.sidebar:
        st.title("OpsMind AI")
        st.caption("Powered by Microsoft Foundry IQ")
        render_mode_badge(settings.retrieval_mode)

        with st.expander("How to use", expanded=False):
            st.markdown(
                "1. Describe the operational incident.\n"
                "2. Select severity and environment.\n"
                "3. Analyze the incident and review cited guidance."
            )

        st.markdown(f"[GitHub repository]({GITHUB_URL})")

    st.title("OpsMind AI — Incident Troubleshooting Agent")
    st.caption("Grounded, cited troubleshooting guidance for cloud operations teams.")

    st.header("🚨 Describe Your Incident")
    description = st.text_area(
        "Incident description",
        placeholder="Linux VM CPU spike above 95% for 10 minutes, application response time degraded",
        height=180,
        label_visibility="collapsed",
    )

    severity_col, environment_col = st.columns(2)
    with severity_col:
        severity = st.selectbox("Severity", ["unknown", "sev1", "sev2", "sev3", "low"])
    with environment_col:
        environment = st.selectbox("Environment", ["unknown", "production", "staging", "development"])

    analyze = st.button("Analyze Incident", type="primary", use_container_width=True)

    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = None

    if analyze:
        if not description.strip():
            st.warning("Please describe the incident.")
        else:
            try:
                analyzer = IncidentAnalyzer(settings)
                st.session_state.last_analysis = analyzer.analyze(
                    IncidentInput(
                        description=description.strip(),
                        severity=severity,
                        environment=environment,
                    )
                )
            except Exception as exc:
                st.error(
                    "OpsMind could not analyze this incident. "
                    f"Check configuration and try again.\n\nError: {exc}"
                )

    if st.session_state.last_analysis:
        st.divider()
        render_result(st.session_state.last_analysis)

    st.markdown(
        "<p style='color:#6b7280; font-size:0.82rem; margin-top:2rem;'>"
        "OpsMind AI | Agents League Hackathon 2026 | Powered by Microsoft Foundry IQ"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
