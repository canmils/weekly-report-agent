"""Real Streamlit state/disk workflow; model responses are explicitly mocked."""
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

@contextmanager
def isolated_app():
    old = Path.cwd()
    with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        os.chdir(directory)
        try:
            yield AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        finally:
            os.chdir(old)

class WorkflowTest(unittest.TestCase):
    def click(self, app, key):
        app.button(key=key).click().run()
        self.assertEqual(len(app.exception), 0)

    def add_input(self, app):
        app.text_input(key="input_description").set_value("Fictional demo")
        app.text_area(key="input_content").set_value((ROOT / "examples/source-notes.md").read_text())
        next(b for b in app.button if b.label == "Save Input").click().run()
        self.assertEqual(len(app.exception), 0)

    def test_generate_edit_save_reload_and_explicit_clan_source(self):
        with isolated_app() as app:
            self.add_input(app)
            with patch("src.ai_writer._chat", return_value="Mock game draft") as model:
                self.click(app, "generate_game_report_btn")
                self.assertIn("Sound approval pending", model.call_args.args[1])
            app.text_area(key="game_report_draft_editor").set_value("Reviewed game report")
            self.click(app, "save_game_report_btn")
            self.click(app, "save_game_report_btn")
            files = list(Path("reports/game_reports").glob("*.md"))
            self.assertEqual(len(files), 2)
            self.assertTrue(all(p.read_text() == "Reviewed game report" for p in files))
            self.assertEqual(len(list(Path("reports/input_snapshots").glob("*/*.md"))), 2)
            self.click(app, "generate_clan_report_btn")
            self.assertTrue(any("Select a saved game report" in w.value for w in app.warning))
            report_id = app.session_state.saved_game_reports[0]["id"]
            app.selectbox(key="selected_saved_game_report_id").set_value(report_id).run()
            with patch("src.ai_writer._chat", return_value="Mock clan draft") as model:
                self.click(app, "generate_clan_report_btn")
                self.assertIn("Reviewed game report", model.call_args.args[1])
            app.text_area(key="clan_report_draft_editor").set_value("Reviewed team summary")
            self.click(app, "save_clan_report_btn")
            self.click(app, "save_clan_report_btn")
            self.assertEqual(len(list(Path("reports/clan_reports").glob("*.md"))), 2)
            reopened = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertEqual(len(reopened.exception), 0)
            self.assertEqual(len(reopened.session_state.saved_inputs), 1)
            self.assertEqual(len(reopened.session_state.saved_game_reports), 2)
            self.assertEqual(len(reopened.session_state.saved_clan_reports), 2)
            self.assertEqual(reopened.session_state.game_report_draft_editor, "")

    def test_provider_failure_preserves_draft(self):
        with isolated_app() as app:
            self.add_input(app)
            app.text_area(key="game_report_draft_editor").set_value("Keep my reviewed draft").run()
            with patch("src.ai_writer._chat", side_effect=RuntimeError("Provider unavailable")):
                self.click(app, "generate_game_report_btn")
            self.assertEqual(app.text_area(key="game_report_draft_editor").value, "Keep my reviewed draft")
            self.assertTrue(any("Provider unavailable" in e.value for e in app.error))

    def test_repeated_input_save_keeps_both_files(self):
        with isolated_app() as app:
            self.add_input(app)
            self.add_input(app)
            self.assertEqual(len(list(Path("reports/saved_inputs").glob("*.md"))), 2)

if __name__ == "__main__":
    unittest.main()
