"""Accessibility-focused Streamlit CSS overrides."""

HIGH_CONTRAST_CSS = """
<style>
    /* Color-blind-safe mood palette references */
    :root {
        --mood-1: #4E79A7;
        --mood-2: #76B7B2;
        --mood-3: #F28E2B;
        --mood-4: #E15759;
        --mood-5: #B07AA1;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }

    .crisis-panel {
        background-color: #1a1a2e;
        border: 2px solid #e94560;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .crisis-panel h3 {
        color: #e94560;
        margin-top: 0;
    }

    .disclaimer-box {
        background-color: #16213e;
        border-left: 4px solid #0f3460;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    .insight-card {
        background-color: #1a1a2e;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .helpline-number {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4fc3f7;
    }

    /* Ensure minimum readable text size */
    p, li, label, span {
        font-size: 1rem;
        line-height: 1.6;
    }
</style>
"""


def apply_styles() -> None:
    import streamlit as st

    st.markdown(HIGH_CONTRAST_CSS, unsafe_allow_html=True)
