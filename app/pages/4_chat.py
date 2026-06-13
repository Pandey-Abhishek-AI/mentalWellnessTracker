"""Wellness companion chat page."""

import runpy
from pathlib import Path

_caller = Path(__file__).resolve()
_bootstrap = _caller.parent / "streamlit_bootstrap.py"
if not _bootstrap.is_file():
    _bootstrap = _caller.parent.parent / "streamlit_bootstrap.py"
runpy.run_path(str(_bootstrap), init_globals={"_streamlit_caller": str(_caller)})

import streamlit as st

from app.components.crisis_panel import render_crisis_panel
from app.components.voice_player import render_listen_button
from app.config import get_settings
from app.context import ensure_session_state, get_chat_service, get_voice_client_cached
from app.styles import apply_styles
from src.llm.schemas import ChatTurn

apply_styles()
settings = get_settings()
user_id = ensure_session_state()

if not st.session_state.get("disclaimer_accepted"):
    st.warning("Please complete onboarding on the Home page first.")
    st.stop()

st.header("Wellness Companion")
st.markdown(
    f"Chat with your empathetic AI companion. "
    f"Max {settings.max_chat_turns} messages per session."
)
if settings.voice_enabled and not settings.voice_available:
    st.caption("Voice: add `ELEVENLABS_API_KEY` to `.env` to hear responses aloud.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_turns" not in st.session_state:
    st.session_state.chat_turns = 0

chat_service = get_chat_service()
voice_client = get_voice_client_cached()
turns_left = settings.max_chat_turns - st.session_state.chat_turns
st.caption(f"Messages remaining this session: {max(0, turns_left)}")

if st.button("New Session"):
    st.session_state.chat_messages = []
    st.session_state.chat_turns = 0
    st.rerun()

for index, msg in enumerate(st.session_state.chat_messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and settings.voice_enabled:
            render_listen_button(index, msg["content"], voice_client)

user_input = st.chat_input("Share how you're feeling...")
if user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})

    history = [
        ChatTurn(role=m["role"], content=m["content"])
        for m in st.session_state.chat_messages[:-1]
    ]

    with st.spinner("Thinking..."):
        result = chat_service.send_message(
            user_id=user_id,
            user_message=user_input,
            session_turns=st.session_state.chat_turns,
            session_history=history,
        )

    if result.crisis:
        render_crisis_panel()
    elif result.error:
        st.error(result.error)
    elif result.message:
        st.session_state.chat_messages.append({"role": "assistant", "content": result.message})
        st.session_state.chat_turns += 1
        st.rerun()
