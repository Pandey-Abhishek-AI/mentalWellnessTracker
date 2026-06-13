"""Crisis helpline panel component."""

import streamlit as st

from src.safety import SafetyService


def render_crisis_panel(safety: SafetyService | None = None) -> None:
    svc = safety or SafetyService()
    st.markdown('<div class="crisis-panel">', unsafe_allow_html=True)
    st.markdown(svc.get_crisis_message())
    st.markdown("**India Mental Health Helplines:**")
    for helpline in svc.get_helplines():
        numbers = ", ".join(helpline.numbers)
        st.markdown(
            f"- **{helpline.name}**: "
            f'<span class="helpline-number">{numbers}</span> — {helpline.description}',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
