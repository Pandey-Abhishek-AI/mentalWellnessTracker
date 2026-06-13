"""Streamlit main entry point with onboarding."""

import runpy
from pathlib import Path

_caller = Path(__file__).resolve()
_bootstrap = _caller.parent / "streamlit_bootstrap.py"
if not _bootstrap.is_file():
    _bootstrap = _caller.parent.parent / "streamlit_bootstrap.py"
runpy.run_path(str(_bootstrap), init_globals={"_streamlit_caller": str(_caller)})

import streamlit as st

from app.config import get_settings
from app.context import ensure_session_state, get_repository
from app.styles import apply_styles
from src.safety import SafetyService

st.set_page_config(
    page_title="Mental Wellness Tracker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
settings = get_settings()
safety = SafetyService()
user_id = ensure_session_state()

st.title("Mental Wellness Tracker")
st.caption("Your empathetic companion for exam-prep wellness")

# Onboarding / disclaimer gate
if not st.session_state.disclaimer_accepted:
    st.markdown('<div class="disclaimer-box">', unsafe_allow_html=True)
    st.markdown(safety.get_disclaimer())
    st.markdown(safety.get_privacy_notice())
    st.markdown("</div>", unsafe_allow_html=True)

    with st.form("onboarding_form"):
        st.subheader("Tell us about your prep")
        exam_type = st.selectbox(
            "Exam you're preparing for",
            options=settings.exam_types,
            help="Used to personalize wellness support (not for exam advice).",
        )
        study_context = st.text_area(
            "Study context (optional)",
            placeholder="e.g., 6-hour study blocks, coaching classes on weekends",
            help="Helps the AI companion understand your routine.",
        )
        acknowledged = st.checkbox(
            "I understand this app is not a substitute for professional mental health care.",
        )
        submitted = st.form_submit_button("Get Started", type="primary")

    if submitted:
        if not acknowledged:
            st.error("Please acknowledge the safety disclaimer to continue.")
        else:
            repo = get_repository()
            repo.update_user_profile(
                user_id=user_id,
                exam_type=exam_type,
                study_context=study_context,
                disclaimer_accepted=True,
            )
            st.session_state.disclaimer_accepted = True
            st.rerun()
    st.stop()

# Main landing content
st.markdown("### Welcome back!")
st.markdown(
    "Use the sidebar to navigate:\n"
    "- **Check-in** — Log your daily mood\n"
    "- **Journal** — Write about your day\n"
    "- **Insights** — AI-powered pattern analysis\n"
    "- **Chat** — Talk to your wellness companion\n"
    "- **Coping** — Breathing exercises and mindfulness\n"
    "- **History** — View your wellness timeline"
)

repo = get_repository()
user = repo.get_user(user_id)
if user:
    st.info(f"Signed in as **{user.email}** · Preparing for **{user.exam_type}**")

if not settings.gemini_api_key.strip():
    st.warning(
        "AI features use mock responses until you set `GEMINI_API_KEY` from "
        "[Google AI Studio](https://aistudio.google.com/apikey). "
        "Mood and journal logging still work offline."
    )
elif not settings.llm_enabled:
    st.warning(
        "Your `GEMINI_API_KEY` is missing or invalid. "
        "Get a key from [Google AI Studio](https://aistudio.google.com/apikey). "
        "Using mock AI responses."
    )

st.markdown("---")
st.markdown(
    '<div class="disclaimer-box">'
    "<strong>Reminder:</strong> This app is not medical advice. "
    "If you're in crisis, visit the Chat or Journal page helplines, or call Tele-MANAS: 14416."
    "</div>",
    unsafe_allow_html=True,
)
