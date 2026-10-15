import uuid
from copy import deepcopy
import time
import streamlit as st
from datetime import datetime
from pathlib import Path

from src.ai_writer import generate_weekly_report_by_game, generate_clan_report

REPORTS_DIR = Path("reports")
GAME_REPORTS_DIR = REPORTS_DIR / "game_reports"
CLAN_REPORTS_DIR = REPORTS_DIR / "clan_reports"
INPUT_SNAPSHOTS_DIR = REPORTS_DIR / "input_snapshots"

GAME_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CLAN_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
INPUT_SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_ui_timing_state():
    if "last_game_report_generation_seconds" not in st.session_state:
        st.session_state.last_game_report_generation_seconds = None

    if "last_clan_report_generation_seconds" not in st.session_state:
        st.session_state.last_clan_report_generation_seconds = None


def parse_saved_game_report_file(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8", errors="ignore")

    return {
        "id": str(uuid.uuid4()),
        "name": file_path.stem,
        "content": content,
        "sources": [],
        "created": file_path.stem.replace("weekly_report_", ""),
        "file_path": str(file_path),
        "file_name": file_path.name,
        "selected": False,
    }


def load_saved_game_reports_from_disk():
    existing_file_names = {
        item.get("file_name")
        for item in st.session_state.saved_game_reports
        if item.get("file_name")
    }

    for file_path in sorted(GAME_REPORTS_DIR.glob("*.md")):
        if file_path.name in existing_file_names:
            continue

        try:
            parsed = parse_saved_game_report_file(file_path)
            st.session_state.saved_game_reports.append(parsed)
        except Exception:
            continue


def parse_saved_clan_report_file(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8", errors="ignore")

    return {
        "id": str(uuid.uuid4()),
        "name": file_path.stem,
        "content": content,
        "sources": [],
        "created": file_path.stem.replace("clan_report_", ""),
        "file_path": str(file_path),
        "file_name": file_path.name,
        "selected": False,
    }


def load_saved_clan_reports_from_disk():
    existing_file_names = {
        item.get("file_name")
        for item in st.session_state.saved_clan_reports
        if item.get("file_name")
    }

    for file_path in sorted(CLAN_REPORTS_DIR.glob("*.md")):
        if file_path.name in existing_file_names:
            continue

        try:
            parsed = parse_saved_clan_report_file(file_path)
            st.session_state.saved_clan_reports.append(parsed)
        except Exception:
            continue


def render_saved_inputs(title="Saved Inputs", key_prefix="inputs_main"):
    st.subheader(title)

    if not st.session_state.saved_inputs:
        st.info("No inputs saved yet.")
        return

    for i, item in enumerate(st.session_state.saved_inputs):
        item_id = item["id"]
        file_name = item.get("file_name", f"[{item['type']}] {item['description']}")

        col1, col2 = st.columns([6, 1])

        with col1:
            st.session_state.saved_inputs[i]["selected"] = st.checkbox(
                file_name,
                value=item["selected"],
                key=f"{key_prefix}_selected_{item_id}",
            )

            with st.expander("View content"):
                st.text(item["content"])

        with col2:
            if st.button("Delete", key=f"{key_prefix}_delete_input_{item_id}"):
                st.session_state.pending_delete_input_id = item_id
                st.rerun()

        if st.session_state.pending_delete_input_id == item_id:
            st.warning(f"Are you sure you want to delete {file_name}?")

            confirm_col1, confirm_col2 = st.columns(2)

            with confirm_col1:
                if st.button("Yes", key=f"{key_prefix}_confirm_delete_input_{item_id}"):
                    file_path = item.get("file_path")

                    if file_path:
                        path_obj = Path(file_path)
                        if path_obj.exists():
                            path_obj.unlink()

                    st.session_state.saved_inputs = [
                        x for x in st.session_state.saved_inputs
                        if x["id"] != item_id
                    ]

                    st.session_state.pending_delete_input_id = None
                    st.success(f"Deleted {file_name}")
                    st.rerun()

            with confirm_col2:
                if st.button("Cancel", key=f"{key_prefix}_cancel_delete_input_{item_id}"):
                    st.session_state.pending_delete_input_id = None
                    st.rerun()


def generate_draft():
    selected_inputs = [
        x for x in st.session_state.saved_inputs if x["selected"]
    ]

    if not selected_inputs:
        st.warning("Please select at least one input.")
        return

    start = time.perf_counter()

    with st.spinner("Generating weekly report with OpenAI..."):
        try:
            report_text = generate_weekly_report_by_game(selected_inputs)
        except Exception as error:
            st.error(str(error))
            return

    end = time.perf_counter()

    st.session_state.last_game_report_generation_seconds = round(end - start, 2)

    st.session_state.game_report_sources = [
        f"[{x['type']}] {x['description']}" for x in selected_inputs
    ]

    st.session_state.game_report_input_snapshot = deepcopy(selected_inputs)
    st.session_state.game_report_draft_editor = report_text


def generate_clan_draft():
    selected_report = None
    selected_report_id = st.session_state.selected_saved_game_report_id

    if selected_report_id:
        selected_report = next(
            (
                x for x in st.session_state.saved_game_reports
                if x["id"] == selected_report_id
            ),
            None
        )

    if not selected_report:
        st.warning("Select a saved game report before generating a clan report.")
        return

    selected_inputs = [
        {
            "type": "Weekly Report by Game",
            "description": f"Saved weekly report by game - {selected_report.get('file_name', selected_report['name'])}",
            "content": selected_report["content"],
            "selected": True,
        }
    ]

    start = time.perf_counter()

    with st.spinner("Generating clan report with OpenAI..."):
        try:
            report_text = generate_clan_report(selected_inputs)
        except Exception as error:
            st.error(str(error))
            return

    end = time.perf_counter()

    st.session_state.last_clan_report_generation_seconds = round(end - start, 2)

    st.session_state.clan_report_sources = [
        selected_report.get("file_name", selected_report["name"])
    ]

    st.session_state.clan_report_draft_editor = report_text


def render_game_report():
    ensure_ui_timing_state()
    load_saved_game_reports_from_disk()

    st.subheader("Generate Weekly Report")

    if st.button("Generate Weekly Report", use_container_width=True, key="generate_game_report_btn"):
        generate_draft()

    if st.session_state.last_game_report_generation_seconds is not None:
        st.caption(f"Last generation time: {st.session_state.last_game_report_generation_seconds} sec")

    if st.session_state.pending_game_report_update is not None:
        st.session_state.game_report_draft_editor = st.session_state.pending_game_report_update
        st.session_state.game_report_input_snapshot = []
        st.session_state.game_report_sources = []
        st.session_state.pending_game_report_update = None

    st.text_area(
        "Draft",
        key="game_report_draft_editor",
        height=260,
        placeholder="The generated weekly report will appear here..."
    )

    if st.session_state.game_report_sources:
        with st.expander("Sources used", expanded=False):
            for source in st.session_state.game_report_sources:
                st.write(f"- {source}")

    if st.button("Save Weekly Report", use_container_width=True, key="save_game_report_btn"):
        if not st.session_state.game_report_draft_editor.strip():
            st.warning("No report to save.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        report_name = f"weekly_report_{timestamp}"

        snapshot_dir = INPUT_SNAPSHOTS_DIR / report_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        selected_inputs = st.session_state.game_report_input_snapshot
        if selected_inputs is None:
            selected_inputs = [x for x in st.session_state.saved_inputs if x["selected"]]

        for i, item in enumerate(selected_inputs, start=1):
            safe_type = item["type"].replace(" ", "_").lower()
            input_file = snapshot_dir / f"{i:02d}_{safe_type}.md"

            content = f"""# Input Source

Type: {item['type']}
Description: {item['description']}

---

{item['content']}
"""

            input_file.write_text(content, encoding="utf-8")

        file_path = GAME_REPORTS_DIR / f"{report_name}.md"

        file_path.write_text(
            st.session_state.game_report_draft_editor,
            encoding="utf-8"
        )

        st.session_state.saved_game_reports.append(
            {
                "id": str(uuid.uuid4()),
                "name": report_name,
                "content": st.session_state.game_report_draft_editor,
                "sources": st.session_state.game_report_sources,
                "created": timestamp,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "selected": False,
            }
        )

        st.success(f"Report saved as {report_name}")
        st.rerun()


def render_saved_game_reports(title="Saved Weekly Reports", key_prefix="game_reports_main"):
    load_saved_game_reports_from_disk()

    st.subheader(title)

    if not st.session_state.saved_game_reports:
        st.info("No saved weekly reports found.")
        return

    for report in reversed(st.session_state.saved_game_reports):
        report_id = report["id"]
        file_name = report.get("file_name", report["name"])

        col1, col2, col3 = st.columns([7, 1.2, 1.3])

        with col1:
            st.write(file_name)

        with col2:
            if st.button("View", key=f"{key_prefix}_view_game_report_{report_id}", use_container_width=True):
                st.session_state.pending_game_report_update = report["content"]
                st.rerun()

        with col3:
            if st.button("Delete", key=f"{key_prefix}_delete_game_report_{report_id}", use_container_width=True):
                st.session_state.pending_delete_game_report_id = report_id
                st.rerun()

        if st.session_state.pending_delete_game_report_id == report_id:
            st.warning(f"Are you sure you want to delete {file_name}?")

            confirm_col1, confirm_col2 = st.columns(2)

            with confirm_col1:
                if st.button("Yes", key=f"{key_prefix}_confirm_delete_game_report_{report_id}", use_container_width=True):
                    file_path = report.get("file_path")

                    if file_path:
                        path_obj = Path(file_path)
                        if path_obj.exists():
                            path_obj.unlink()

                    st.session_state.saved_game_reports = [
                        x for x in st.session_state.saved_game_reports
                        if x["id"] != report_id
                    ]

                    if st.session_state.selected_saved_game_report_id == report_id:
                        st.session_state.selected_saved_game_report_id = None

                    st.session_state.pending_delete_game_report_id = None
                    st.success(f"Deleted {file_name}")
                    st.rerun()

            with confirm_col2:
                if st.button("Cancel", key=f"{key_prefix}_cancel_delete_game_report_{report_id}", use_container_width=True):
                    st.session_state.pending_delete_game_report_id = None
                    st.rerun()

        with st.expander("Preview", expanded=False):
            st.text(report["content"])


def render_saved_clan_reports(title="Saved Clan Weekly Reports", key_prefix="clan_reports_main"):
    load_saved_clan_reports_from_disk()

    st.subheader(title)

    if not st.session_state.saved_clan_reports:
        st.info("No saved clan weekly reports found.")
        return

    for report in reversed(st.session_state.saved_clan_reports):
        report_id = report["id"]
        file_name = report.get("file_name", report["name"])

        col1, col2, col3 = st.columns([7, 1.2, 1.3])

        with col1:
            checked = st.checkbox(
                file_name,
                value=(st.session_state.selected_saved_clan_report_id == report_id),
                key=f"{key_prefix}_select_clan_report_{report_id}"
            )

            if checked:
                st.session_state.selected_saved_clan_report_id = report_id
            elif st.session_state.selected_saved_clan_report_id == report_id:
                st.session_state.selected_saved_clan_report_id = None

        with col2:
            if st.button("View", key=f"{key_prefix}_view_clan_report_{report_id}", use_container_width=True):
                st.session_state.pending_clan_report_update = report["content"]
                st.rerun()

        with col3:
            if st.button("Delete", key=f"{key_prefix}_delete_clan_report_{report_id}", use_container_width=True):
                st.session_state.pending_delete_clan_report_id = report_id
                st.rerun()

        if st.session_state.pending_delete_clan_report_id == report_id:
            st.warning(f"Are you sure you want to delete {file_name}?")

            confirm_col1, confirm_col2 = st.columns(2)

            with confirm_col1:
                if st.button("Yes", key=f"{key_prefix}_confirm_delete_clan_report_{report_id}", use_container_width=True):
                    file_path = report.get("file_path")

                    if file_path:
                        path_obj = Path(file_path)
                        if path_obj.exists():
                            path_obj.unlink()

                    st.session_state.saved_clan_reports = [
                        x for x in st.session_state.saved_clan_reports
                        if x["id"] != report_id
                    ]

                    if st.session_state.selected_saved_clan_report_id == report_id:
                        st.session_state.selected_saved_clan_report_id = None

                    st.session_state.pending_delete_clan_report_id = None
                    st.success(f"Deleted {file_name}")
                    st.rerun()

            with confirm_col2:
                if st.button("Cancel", key=f"{key_prefix}_cancel_delete_clan_report_{report_id}", use_container_width=True):
                    st.session_state.pending_delete_clan_report_id = None
                    st.rerun()

        with st.expander("Preview", expanded=False):
            st.text(report["content"])


def render_clan_report():
    ensure_ui_timing_state()

    st.subheader("Generate Clan Weekly Report")
    load_saved_game_reports_from_disk()
    reports = {r["id"]: r for r in st.session_state.saved_game_reports}
    if st.session_state.selected_saved_game_report_id not in reports:
        st.session_state.selected_saved_game_report_id = None
    st.selectbox(
        "Saved game report to summarize",
        options=[None, *reports],
        format_func=lambda value: "Select a report" if value is None else reports[value]["name"],
        key="selected_saved_game_report_id",
    )

    if st.button("Generate Clan Weekly Report", use_container_width=True, key="generate_clan_report_btn"):
        generate_clan_draft()

    if st.session_state.last_clan_report_generation_seconds is not None:
        st.caption(f"Last generation time: {st.session_state.last_clan_report_generation_seconds} sec")

    if st.session_state.clan_report_sources:
        st.caption(f"Source used: {', '.join(st.session_state.clan_report_sources)}")

    if st.session_state.pending_clan_report_update is not None:
        st.session_state.clan_report_draft_editor = st.session_state.pending_clan_report_update
        st.session_state.pending_clan_report_update = None

    st.text_area(
        "Draft",
        key="clan_report_draft_editor",
        height=260,
        placeholder="The generated clan weekly report will appear here..."
    )

    if st.button("Save Clan Weekly Report", use_container_width=True, key="save_clan_report_btn"):
        if not st.session_state.clan_report_draft_editor.strip():
            st.warning("No clan report to save.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        report_name = f"clan_report_{timestamp}"
        file_path = CLAN_REPORTS_DIR / f"{report_name}.md"

        file_path.write_text(
            st.session_state.clan_report_draft_editor,
            encoding="utf-8"
        )

        st.session_state.saved_clan_reports.append(
            {
                "id": str(uuid.uuid4()),
                "name": report_name,
                "content": st.session_state.clan_report_draft_editor,
                "sources": st.session_state.clan_report_sources,
                "created": timestamp,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "selected": False,
            }
        )

        st.success(f"Clan report saved as {report_name}")
        st.rerun()
