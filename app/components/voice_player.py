"""Streamlit voice playback for chat assistant messages."""

import streamlit as st

from src.voice.client import VoiceClient


def render_listen_button(
    message_index: int,
    text: str,
    voice_client: VoiceClient,
    *,
    enabled: bool = True,
) -> None:
    """Show a Listen control and audio player for an assistant message."""
    if not enabled:
        return

    audio_key = f"chat_audio_{message_index}"
    error_key = f"chat_audio_error_{message_index}"

    if st.button("Listen", key=f"listen_{message_index}", help="Read this response aloud"):
        with st.spinner("Generating audio..."):
            result = voice_client.synthesize(text)
        if result.audio:
            st.session_state[audio_key] = result.audio
            st.session_state.pop(error_key, None)
        else:
            st.session_state[error_key] = result.error or "Voice playback failed."
            st.session_state.pop(audio_key, None)

    if audio_key in st.session_state:
        st.audio(st.session_state[audio_key], format="audio/mpeg")

    if error_key in st.session_state:
        st.caption(st.session_state[error_key])
