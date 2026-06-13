"""Coping toolkit page."""

from pathlib import Path

exec(  # noqa: S102
    (Path(__file__).resolve().parent.parent / "_bootstrap.py").read_text(encoding="utf-8"),
    {"__file__": str(Path(__file__).resolve().parent.parent / "_bootstrap.py")},
)

import streamlit as st

from app.components.crisis_panel import render_crisis_panel
from app.context import ensure_session_state, get_coping_service
from app.styles import apply_styles
from src.services.coping_service import EXERCISE_TYPES

apply_styles()
user_id = ensure_session_state()

if not st.session_state.get("disclaimer_accepted"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

st.header("Coping Toolkit")
st.markdown("Generate personalized wellness exercises based on your exam prep context.")

coping_service = get_coping_service()

exercise_type = st.selectbox(
    "Exercise type",
    options=EXERCISE_TYPES,
    help="Choose the type of support you'd like right now.",
)
optional_context = st.text_area(
    "Additional context (optional)",
    placeholder="e.g., feeling anxious before tomorrow's mock test",
    help="Helps personalize the exercise.",
)

if st.button("Generate Exercise", type="primary"):
    with st.spinner("Creating your exercise..."):
        result = coping_service.generate(user_id, exercise_type, optional_context)

    if result.crisis:
        render_crisis_panel()
    elif result.error:
        st.error(result.error)
    elif result.content:
        st.markdown(result.content)
