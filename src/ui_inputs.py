import uuid
from datetime import datetime
from pathlib import Path
import streamlit as st


DOC_TYPES = [
    "Weekly Status",
    "Call Notes",
    "Other",
]

SAVED_INPUTS_DIR = Path("reports") / "saved_inputs"
SAVED_INPUTS_DIR.mkdir(parents=True, exist_ok=True)


def make_safe_description(text: str, max_words: int = 5) -> str:
    words = text.lower().split()
    short = "_".join(words[:max_words])
    safe = "".join(c for c in short if c.isalnum() or c == "_")
    return safe or "input"

def parse_saved_input_file(file_path: Path) -> dict:
    raw = file_path.read_text(encoding="utf-8")

    metadata_part, content_part = raw.split("\n---\n\n", 1)

    doc_type = "Other"
    description = file_path.stem

    for line in metadata_part.splitlines():
        if line.startswith("Type: "):
            doc_type = line.replace("Type: ", "", 1).strip()
        elif line.startswith("Description: "):
            description = line.replace("Description: ", "", 1).strip()

    return {
        "id": str(uuid.uuid4()),
        "type": doc_type,
        "description": description,
        "content": content_part.strip(),
        "selected": False,
        "file_path": str(file_path),
        "file_name": file_path.name,
        "created": file_path.stem.split("_")[-5:] if "_" in file_path.stem else "",
    }


def load_saved_inputs_from_disk():
    if st.session_state.saved_inputs_loaded_from_disk:
        return

    existing_file_names = {
        item.get("file_name")
        for item in st.session_state.saved_inputs
        if item.get("file_name")
    }

    for file_path in sorted(SAVED_INPUTS_DIR.glob("*.md")):
        if file_path.name in existing_file_names:
            continue

        try:
            parsed = parse_saved_input_file(file_path)
            st.session_state.saved_inputs.append(parsed)
        except Exception:
            continue

    st.session_state.saved_inputs_loaded_from_disk = True

def render_inputs():

    load_saved_inputs_from_disk()

    if st.session_state.pending_input_form_reset:
        st.session_state.input_doc_type = DOC_TYPES[0]
        st.session_state.input_description = ""
        st.session_state.input_content = ""
        st.session_state.pending_input_form_reset = False

    st.subheader("1. Add Input")

    st.selectbox(
        "Document Type",
        DOC_TYPES,
        key="input_doc_type",
    )

    st.text_input("Description", key="input_description")
    st.text_area("Content", height=220, key="input_content")

    if st.button("Save Input", use_container_width=True):

        if not st.session_state.input_description.strip():
            st.warning("Please add a description before saving.")
            return

        if not st.session_state.input_content.strip():
            st.warning("Please add some content before saving.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        safe_type = st.session_state.input_doc_type.strip().lower().replace(" ", "_")
        safe_desc = make_safe_description(
            st.session_state.input_description.strip()
        )

        file_name = f"{safe_type}_{safe_desc}_{timestamp}.md"
        file_path = SAVED_INPUTS_DIR / file_name

        file_content = f"""# Input Source

Type: {st.session_state.input_doc_type.strip()}
Description: {st.session_state.input_description.strip()}
Created: {timestamp}
Source file: {file_name}

---

{st.session_state.input_content.strip()}
"""

        file_path.write_text(file_content, encoding="utf-8")

        st.session_state.saved_inputs.append(
            {
                "id": str(uuid.uuid4()),
                "type": st.session_state.input_doc_type.strip(),
                "description": st.session_state.input_description.strip(),
                "content": st.session_state.input_content.strip(),
                "selected": True,
                "file_path": str(file_path),
                "file_name": file_name,
                "created": timestamp,
            }
        )

        st.session_state.pending_input_form_reset = True

        st.success(f"Input saved as {file_name}")
        st.rerun()
