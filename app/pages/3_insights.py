"""AI insights dashboard page."""

import runpy
from pathlib import Path

_caller = Path(__file__).resolve()
_bootstrap = _caller.parent / "streamlit_bootstrap.py"
if not _bootstrap.is_file():
    _bootstrap = _caller.parent.parent / "streamlit_bootstrap.py"
runpy.run_path(str(_bootstrap), init_globals={"_streamlit_caller": str(_caller)})

import altair as alt
import pandas as pd
import streamlit as st

from app.components.crisis_panel import render_crisis_panel
from app.components.insight_display import render_insight
from app.context import ensure_session_state, get_insight_service, get_mood_service
from app.styles import apply_styles
from src.llm.schemas import InsightPayload
from src.utils.dates import days_ago

apply_styles()
user_id = ensure_session_state()

if not st.session_state.get("disclaimer_accepted"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

st.header("Insights")
st.markdown("AI-powered analysis of your mood and journal patterns from the last 7 days.")

insight_service = get_insight_service()
mood_service = get_mood_service()

# Mood trend chart
moods = mood_service.get_recent(user_id, days_ago(30))
if moods:
    df = pd.DataFrame([
        {
            "date": str(m.entry_date),
            "mood": m.mood,
            "energy": m.energy,
            "sleep": m.sleep_quality,
        }
        for m in reversed(moods)
    ])
    chart = (
        alt.Chart(df)
        .transform_fold(["mood", "energy", "sleep"], as_=["metric", "value"])
        .mark_line(point=True)
        .encode(
            x=alt.X("date:N", title="Date"),
            y=alt.Y("value:Q", title="Score (1-5)", scale=alt.Scale(domain=[1, 5])),
            color=alt.Color(
                "metric:N",
                scale=alt.Scale(
                    range=["#4E79A7", "#F28E2B", "#76B7B2"],
                ),
                title="Metric",
            ),
            tooltip=["date", "metric", "value"],
        )
        .properties(height=300, title="Wellness Trends (30 days)")
    )
    st.altair_chart(chart, use_container_width=True)

    avg_mood = df["mood"].mean()
    st.markdown(
        f"**Text summary:** Average mood: {avg_mood:.1f}/5 over {len(df)} check-ins. "
        f"Latest mood: {df['mood'].iloc[-1]}/5."
    )
else:
    st.info("Log mood check-ins to see trends here.")

st.markdown("---")

if st.button("Generate AI Insight", type="primary"):
    with st.spinner("Analyzing your wellness data..."):
        result = insight_service.generate(user_id)

    if result.crisis:
        render_crisis_panel()
    elif result.error and not result.insight:
        st.warning(result.error)
    elif result.insight:
        if result.error:
            st.warning(f"Using cached insight. ({result.error})")
        render_insight(result.insight, cached=result.cached)
    else:
        st.warning(result.error or "Could not generate insight.")

# Show latest saved insight
latest = insight_service.get_latest(user_id)
if latest and not st.session_state.get("_insight_just_generated"):
    st.subheader("Latest Saved Insight")
    payload = InsightPayload.model_validate(latest.summary_json)
    st.caption(f"Period: {latest.period_start} to {latest.period_end}")
    render_insight(payload)
