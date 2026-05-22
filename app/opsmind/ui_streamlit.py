from __future__ import annotations

import streamlit as st

from app.opsmind.analyzer import IncidentAnalyzer
from app.opsmind.formatter import to_markdown
from app.opsmind.models import IncidentInput


st.set_page_config(page_title="OpsMind AI", page_icon="OM", layout="wide")

st.title("OpsMind AI")
st.caption("Incident troubleshooting and runbook reasoning agent powered by Foundry IQ.")

with st.sidebar:
    st.header("Incident Context")
    severity = st.selectbox("Severity", ["unknown", "low", "medium", "high", "critical", "sev1"], index=3)
    environment = st.selectbox("Environment", ["unknown", "prod", "staging", "dev"], index=1)
    st.info("OpsMind recommends actions only. It does not execute infrastructure changes.")

default_incident = "Checkout API is returning 502 after deployment and users cannot complete payment."
description = st.text_area("Describe the incident", value=default_incident, height=140)

if st.button("Analyze Incident", type="primary"):
    if not description.strip():
        st.warning("Enter an incident description first.")
    else:
        analyzer = IncidentAnalyzer()
        response = analyzer.analyze(
            IncidentInput(description=description, severity=severity, environment=environment)
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Category", response.likely_category)
        c2.metric("Confidence", response.confidence.value)
        c3.metric("Risk", response.risk.value)

        st.markdown(to_markdown(response))

        with st.expander("Raw citations"):
            for citation in response.citations:
                st.write(f"[{citation.source_id}] {citation.title}")
                st.code(citation.snippet)

