import os
from pathlib import Path
from typing import List, Dict

from docx import Document
from openai import OpenAI



MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = 0.1
MAX_TOKENS = 1800

GUIDELINE_PATH = Path("prompts/Guideline for Writing Effective Weekly Status Updates.docx")


# ---------- LOAD GUIDELINES ----------
def read_docx_text(path: Path) -> str:
    doc = Document(path)
    parts = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            parts.append(text)

    for table in doc.tables:
        for row in table.rows:
            row_cells = []
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    row_cells.append(text)
            if row_cells:
                parts.append(" | ".join(row_cells))

    return "\n".join(parts)


def load_guidelines() -> str:
    if GUIDELINE_PATH.exists():
        return read_docx_text(GUIDELINE_PATH)
    return ""


# ---------- FORMAT INPUT ----------
def build_input_text(selected_inputs: List[Dict]) -> str:
    return "\n\n".join(
        item.get("content", "").strip()
        for item in selected_inputs
    )


# ---------- CORE CALL ----------
def _chat(system_prompt: str, user_prompt: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Set OPENAI_API_KEY in the terminal before generating a report.")
    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


# ---------- GAME REPORT (NO TOCAR) ----------
def generate_weekly_report_by_game(selected_inputs: List[Dict]) -> str:
    if not selected_inputs:
        return "No selected inputs."

    input_text = build_input_text(selected_inputs)

    system_prompt = """
You are a senior game producer writing weekly reports.

Write naturally, clearly and concisely.
Do not sound like an AI.
""".strip()

    user_prompt = f"""
Write the weekly report by game using the inputs below.

Be accurate.
Cross-check inputs.
Use weekly update as main source.

{input_text}
""".strip()

    return _chat(system_prompt, user_prompt)


# ---------- CLAN REPORT (CLAU!) ----------
def generate_clan_report(selected_inputs: List[Dict]) -> str:
    if not selected_inputs:
        return "No selected inputs."

    input_text = build_input_text(selected_inputs)
    guidelines = load_guidelines()

    system_prompt = f"""
You are a senior game producer.

You will receive a weekly report by game.

Your job is simple:
Rewrite it as a weekly report by clan.

Write like a HUMAN:
- natural
- clear
- concise
- not like AI

IMPORTANT:
- Do NOT list game by game
- GROUP information naturally
- Keep important issues and risks
- Keep full game names
- Do NOT invent anything

Use the guidelines to structure the sections correctly.

GUIDELINES:
{guidelines}
""".strip()

    user_prompt = f"""
Rewrite this weekly report by game into a weekly report by clan.

Do it like I would do manually in ChatGPT.

{input_text}
""".strip()

    return _chat(system_prompt, user_prompt)
