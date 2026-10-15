# Verification record

## 15 October 2026: supported local onboarding

- Fresh Python 3.12 virtual environment installed from `requirements.txt` on Linux.
- Four automated tests pass with Streamlit AppTest and temporary local files.
- No-key launch/input save and explicit generation error checked.
- Mocked game generation receives fictional source notes; edited report saves.
- Repeated input, game-report and clan-report saves retain separate files.
- Generated game drafts retain source snapshots.
- Clan generation requires an explicit saved report; mocked request receives its text.
- A new app session reloads saved inputs and both report types; unsaved draft is empty.
- Simulated provider failure preserves the previous draft and reports an error.

Run: `.venv/bin/python -m unittest discover -s tests -v` on Linux/macOS;
use `.\.venv\Scripts\python.exe` instead on Windows.

[CI history](https://github.com/canmils/weekly-report-agent/actions/workflows/onboarding.yml)
runs the same suite on Ubuntu and Windows. Inspect the run for your commit;
a configured workflow alone is not a pass. Earlier implementation checks belong
to their historical commits, not a claim that all workflows have been evaluated.

## Not established

- Live paid OpenAI generation, factual accuracy, latency or cost.
- Visual browser testing, native macOS execution or multi-user hosting.
- Exhaustive deletion/backup recovery behavior or a durable compliance audit trail.
- Measured time savings, buyer demand or commercial readiness.

The examples are explicitly human-written references. Automated model mocks verify
application wiring, not model quality. Dependency ranges remain flexible; there is
no fully pinned Python dependency lock. Save only permitted data and review drafts.
