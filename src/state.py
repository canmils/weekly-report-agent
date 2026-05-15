import streamlit as st


def init_state():
    defaults = {
        "saved_inputs": [],
        "saved_inputs_loaded_from_disk": False,
        "game_report_sources": [],
        "game_report_draft_editor": "",
        "saved_game_reports": [],
        "selected_saved_game_report_id": None,
        "pending_game_report_update": None,
        "clan_report_sources": [],
        "clan_report_draft_editor": "",
        "saved_clan_reports": [],
        "selected_saved_clan_report_id": None,
        "pending_clan_report_update": None,
        "input_doc_type": "Weekly Status",
        "input_description": "",
        "input_content": "",
        "pending_input_form_reset": False,
        "pending_delete_input_id": None,
        "pending_delete_game_report_id": None,
        "pending_delete_clan_report_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
