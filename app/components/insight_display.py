"""Insight display component."""

import streamlit as st

from src.llm.schemas import InsightPayload


def render_insight(payload: InsightPayload, cached: bool = False) -> None:
    if cached:
        st.info("Showing your last saved insight (AI temporarily unavailable).")

    sections = [
        ("Stress Triggers", payload.triggers),
        ("Patterns", payload.patterns),
        ("Emotional Themes", payload.themes),
        ("Suggestions", payload.suggestions),
    ]

    for title, items in sections:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.subheader(title)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.markdown("_No items identified._")
        st.markdown("</div>", unsafe_allow_html=True)

    # Text alternative for visual data
    st.markdown("**Text summary:**")
    summary_parts = []
    if payload.triggers:
        summary_parts.append(f"Triggers: {', '.join(payload.triggers)}")
    if payload.patterns:
        summary_parts.append(f"Patterns: {', '.join(payload.patterns)}")
    if payload.themes:
        summary_parts.append(f"Themes: {', '.join(payload.themes)}")
    st.markdown(" | ".join(summary_parts) if summary_parts else "_No summary available._")
