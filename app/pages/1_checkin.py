"""Daily mood check-in page."""

import runpy
from pathlib import Path

_caller = Path(__file__).resolve()
_bootstrap = _caller.parent / "streamlit_bootstrap.py"
if not _bootstrap.is_file():
    _bootstrap = _caller.parent.parent / "streamlit_bootstrap.py"
runpy.run_path(str(_bootstrap), init_globals={"_streamlit_caller": str(_caller)})

import streamlit as st

from app.components.crisis_panel import render_crisis_panel
from app.config import get_settings
from app.context import ensure_session_state, get_mood_service, get_safety
from app.styles import apply_styles
from src.utils.dates import days_ago
from src.utils.validation import ValidationError

apply_styles()
settings = get_settings()
user_id = ensure_session_state()

if not st.session_state.get("disclaimer_accepted"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

st.header("Daily Check-in")
st.markdown(
    "Rate how you're feeling today. All scales are 1 (low) to 5 (high).",
    help="Mood: overall feeling. Energy: physical/mental energy. Sleep: last night's rest.",
)

mood_service = get_mood_service()

with st.form("mood_form", clear_on_submit=False):
    mood = st.slider("Mood", min_value=1, max_value=5, value=3, help="1 = very low, 5 = great")
    energy = st.slider("Energy", min_value=1, max_value=5, value=3)
    sleep_quality = st.slider("Sleep quality", min_value=1, max_value=5, value=3)
    tags = st.multiselect(
        "Tags (optional)",
        options=settings.mood_tags,
        help="Select any stress factors relevant today.",
    )
    notes = st.text_area(
        "Quick notes (optional)",
        placeholder="Anything on your mind?",
        help="Short notes only — use Journal for longer entries.",
    )
    submitted = st.form_submit_button("Save Check-in", type="primary")

if submitted:
    try:
        mood_service.save_checkin(
            user_id=user_id,
            mood=mood,
            energy=energy,
            sleep_quality=sleep_quality,
            tags=tags,
        )
        st.success("Check-in saved!")

        if notes.strip():
            safety = get_safety()
            crisis = safety.check_text(notes)
            if crisis.is_crisis:
                render_crisis_panel(safety)
            else:
                from app.context import get_journal_service
                get_journal_service().save_entry(user_id, notes)
    except ValidationError as exc:
        st.error(str(exc))

# Show recent check-ins
recent = mood_service.get_recent(user_id, days_ago(7))
if recent:
    st.subheader("Last 7 days")
    for entry in recent:
        tag_str = ", ".join(entry.tags) if entry.tags else "none"
        st.markdown(
            f"**{entry.entry_date}** — Mood: {entry.mood}/5, "
            f"Energy: {entry.energy}/5, Sleep: {entry.sleep_quality}/5 | Tags: {tag_str}"
        )
else:
    st.info("No check-ins yet. Log your first mood above!")
