"""Journal entry page."""

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
from app.context import ensure_session_state, get_journal_service
from app.styles import apply_styles
from src.utils.dates import days_ago
from src.utils.validation import ValidationError

apply_styles()
settings = get_settings()
user_id = ensure_session_state()

if not st.session_state.get("disclaimer_accepted"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

st.header("Journal")
st.markdown(
    f"Write freely about your day, feelings, or study experience. "
    f"({settings.min_journal_chars}–{settings.max_journal_chars} characters)"
)

journal_service = get_journal_service()

with st.form("journal_form"):
    content = st.text_area(
        "Today's journal",
        height=200,
        placeholder="What's on your mind today? How did prep go?",
        help=f"Minimum {settings.min_journal_chars} characters required.",
        label_visibility="visible",
    )
    char_count = len(content.strip())
    st.caption(f"Characters: {char_count} / {settings.max_journal_chars}")
    submitted = st.form_submit_button("Save Journal", type="primary")

if submitted:
    try:
        result = journal_service.save_entry(user_id, content)
        st.success("Journal entry saved.")
        if result.crisis.is_crisis:
            render_crisis_panel()
    except ValidationError as exc:
        st.error(str(exc))

recent = journal_service.get_recent(user_id, days_ago(30))
if recent:
    st.subheader("Recent entries")
    for entry in recent[:5]:
        preview = entry.content[:100] + ("..." if len(entry.content) > 100 else "")
        flag = " ⚠️" if entry.crisis_flagged else ""
        st.markdown(f"**{entry.entry_date}**{flag}: {preview}")
else:
    st.info("No journal entries yet. Writing regularly helps unlock AI insights.")
