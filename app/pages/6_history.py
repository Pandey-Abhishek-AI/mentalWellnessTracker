"""History and data management page."""

from datetime import date
from pathlib import Path

exec(  # noqa: S102
    (Path(__file__).resolve().parent.parent / "_bootstrap.py").read_text(encoding="utf-8"),
    {"__file__": str(Path(__file__).resolve().parent.parent / "_bootstrap.py")},
)

import streamlit as st

from app.context import ensure_session_state, get_repository
from app.styles import apply_styles

apply_styles()
user_id = ensure_session_state()

if not st.session_state.get("disclaimer_accepted"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

st.header("History")
st.markdown("Your wellness timeline and data management.")

repo = get_repository()
epoch = date(2000, 1, 1)
moods = repo.get_mood_entries_since(user_id, epoch)
journals = repo.get_journal_entries_since(user_id, epoch)
insights = repo.get_insights(user_id)

tab1, tab2, tab3 = st.tabs(["Mood Check-ins", "Journals", "AI Insights"])

with tab1:
    if moods:
        for m in moods:
            tags = ", ".join(m.tags) if m.tags else "none"
            st.markdown(
                f"**{m.entry_date}** — Mood {m.mood}/5, Energy {m.energy}/5, "
                f"Sleep {m.sleep_quality}/5 | Tags: {tags}"
            )
    else:
        st.info("No mood check-ins recorded yet.")

with tab2:
    if journals:
        for j in journals:
            preview = j.content[:80] + ("..." if len(j.content) > 80 else "")
            flag = " [crisis flagged]" if j.crisis_flagged else ""
            st.markdown(f"**{j.entry_date}**{flag}: {preview}")
    else:
        st.info("No journal entries recorded yet.")

with tab3:
    if insights:
        for ins in insights:
            period = f"{ins.period_start} to {ins.period_end}"
            st.markdown(f"**{ins.created_at.date()}** — Period: {period}")
            triggers = ins.summary_json.get("triggers", [])
            if triggers:
                st.markdown(f"  Triggers: {', '.join(triggers)}")
    else:
        st.info("No AI insights generated yet.")

st.markdown("---")
st.subheader("Data Management")
st.warning("This action permanently deletes all your wellness data on this device.")

if st.button("Clear All My Data", type="secondary"):
    st.session_state.confirm_clear = True

if st.session_state.get("confirm_clear"):
    st.markdown("**Are you sure?** This cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, delete everything", type="primary"):
            repo.clear_user_data(user_id)
            st.session_state.chat_messages = []
            st.session_state.chat_turns = 0
            st.session_state.confirm_clear = False
            st.success("All data cleared.")
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.session_state.confirm_clear = False
            st.rerun()
