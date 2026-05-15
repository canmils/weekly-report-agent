from pathlib import Path
from openai import OpenAI
from .config import OPENAI_MODEL

PROMPT_PATH = Path("prompts/game_report_prompt.txt")


def load_game_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_game_report(client: OpenAI, game_name: str, source_notes: str) -> str:
    """
    Generate a weekly report for one game using ChatGPT.
    """

    system_prompt = load_game_prompt()

    user_prompt = f"""
Game:
{game_name}

Source notes:
{source_notes}

Write the weekly report using the required structure.
Rewrite the notes into a concise professional report.
Do NOT copy the wording of the source notes.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text.strip()
