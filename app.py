import streamlit as st

from src.state import init_state
from src.ui_inputs import render_inputs
from src.ui_reports import (
    render_saved_inputs,
    render_game_report,
    render_saved_game_reports,
    render_clan_report,
    render_saved_clan_reports,
)

st.set_page_config(
    page_title="Weekly Report Agent",
    layout="wide",
)

init_state()

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-size: 14px;
    }

    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 0.4rem !important;
    }

    h2, h3 {
        font-size: 1.2rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.5rem !important;
    }

    .stButton > button {
        padding-top: 0.35rem !important;
        padding-bottom: 0.35rem !important;
        font-size: 0.95rem !important;
    }

    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        font-size: 0.95rem !important;
    }

    div[data-testid="stExpander"] {
        margin-bottom: 0.4rem !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Weekly Report Agent")

tab_inputs, tab_game, tab_clan = st.tabs(
    ["Inputs", "Game Report", "Clan Report"]
)

with tab_inputs:
    col_left, col_right = st.columns([1.0, 1.0], gap="medium")

    with col_left:
        render_inputs()

    with col_right:
        render_saved_inputs(
            title="Saved Inputs",
            key_prefix="tab_inputs_saved"
        )

with tab_game:
    col_left, col_center, col_right = st.columns([0.95, 0.95, 1.1], gap="medium")

    with col_left:
        render_saved_inputs(
            title="Inputs to Use",
            key_prefix="tab_game_inputs"
        )

    with col_center:
        render_saved_game_reports(
            title="Saved Game Reports",
            key_prefix="tab_game_reports"
        )

    with col_right:
        render_game_report()

with tab_clan:
    col_left, col_center, col_right = st.columns([0.95, 0.95, 1.1], gap="medium")

    with col_left:
        render_saved_game_reports(
            title="Weekly Reports to Use",
            key_prefix="tab_clan_source_reports"
        )

    with col_center:
        render_saved_clan_reports(
            title="Saved Clan Reports",
            key_prefix="tab_clan_reports"
        )

    with col_right:
        render_clan_report()
