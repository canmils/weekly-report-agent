import os, tempfile, unittest, sys
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
class OnboardingTest(unittest.TestCase):
    def test_no_key_launch_and_save_input(self):
        old=Path.cwd();sys.path.insert(0,str(ROOT))
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ,{"OPENAI_API_KEY": ""}):
            os.chdir(temp)
            try:
                at=AppTest.from_file(str(ROOT/"app.py"), default_timeout=30).run()
                self.assertEqual(len(at.exception),0)
                at.text_input(key="input_description").set_value("Fictional demo")
                at.text_area(key="input_content").set_value("Orchard Workshop: art ready; QA Monday.")
                next(b for b in at.button if b.label=="Save Input").click().run()
                self.assertEqual(len(at.exception),0)
                self.assertEqual(len(list(Path("reports/saved_inputs").glob("*.md"))),1)
                next(b for b in at.button if b.label=="Generate Weekly Report").click().run()
                self.assertEqual(len(at.exception),0)
                self.assertTrue(any("OPENAI_API_KEY" in e.value for e in at.error))
            finally:os.chdir(old)
if __name__ == "__main__": unittest.main()
