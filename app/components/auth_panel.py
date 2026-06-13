"""Login and registration UI."""

import streamlit as st

from app.config import get_settings
from app.context import get_auth_service, get_repository
from src.services.auth_service import AuthError


def render_auth_gate() -> None:
    """Block the app until the user logs in or registers."""
    if st.session_state.get("authenticated") and st.session_state.get("user_id"):
        user = get_repository().get_user(st.session_state.user_id)
        if user and user.email and user.user_uuid:
            return
        _clear_auth_session()

    st.subheader("Sign in")
    st.caption("Your account UUID is derived from your email and scopes your daily AI token limit.")

    tab_login, tab_register = st.tabs(["Log in", "Create account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", type="primary")
        if submitted:
            _handle_login(email, password)

    with tab_register:
        with st.form("register_form"):
            email = st.text_input("Email ", placeholder="you@example.com", key="register_email")
            password = st.text_input("Password ", type="password", key="register_password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", type="primary")
        if submitted:
            if password != confirm:
                st.error("Passwords do not match.")
            else:
                _handle_register(email, password)

    st.stop()


def render_user_sidebar() -> None:
    """Show account info, token usage, and logout."""
    if not st.session_state.get("authenticated"):
        return

    settings = get_settings()
    repo = get_repository()
    user_uuid = st.session_state.get("user_uuid", "")
    used = repo.estimate_chat_tokens_since_uuid(user_uuid, _start_of_today()) if user_uuid else 0
    budget = settings.daily_chat_token_budget

    st.sidebar.markdown("### Account")
    st.sidebar.markdown(f"**{st.session_state.get('user_email', '')}**")
    st.sidebar.caption(f"UUID: `{user_uuid}`")
    st.sidebar.progress(min(1.0, used / budget) if budget else 0.0)
    st.sidebar.caption(f"Chat tokens today: {used} / {budget}")

    if st.sidebar.button("Log out", use_container_width=True):
        _clear_auth_session()
        st.rerun()


def _handle_login(email: str, password: str) -> None:
    try:
        result = get_auth_service().login(email, password)
        _set_auth_session(result.user)
        st.success("Logged in successfully.")
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))


def _handle_register(email: str, password: str) -> None:
    try:
        result = get_auth_service().register(email, password)
        _set_auth_session(result.user)
        st.success("Account created. Complete onboarding on the Home page.")
        st.rerun()
    except AuthError as exc:
        st.error(str(exc))


def _set_auth_session(user) -> None:
    st.session_state.authenticated = True
    st.session_state.user_id = user.id
    st.session_state.user_uuid = user.user_uuid
    st.session_state.user_email = user.email
    st.session_state.disclaimer_accepted = user.disclaimer_accepted_at is not None
    st.session_state.chat_turns = 0
    st.session_state.chat_messages = []


def _clear_auth_session() -> None:
    for key in (
        "authenticated",
        "user_id",
        "user_uuid",
        "user_email",
        "disclaimer_accepted",
        "chat_turns",
        "chat_messages",
        "confirm_clear",
    ):
        st.session_state.pop(key, None)


def _start_of_today():
    from src.utils.dates import start_of_today_utc

    return start_of_today_utc()
