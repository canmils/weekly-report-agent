# Weekly Report Agent

A local Streamlit tool for turning pasted production notes into editable weekly reports, first by game and then by team (called a clan in the UI). It helps producers organize source notes and save reviewed drafts; it does not retrieve Jira or send reports.

## Install

Requirements: Git, Python 3.11 or 3.12, and an internet connection to install dependencies. Run all commands from the repository root. Use a virtual environment to keep dependencies separate.

Windows PowerShell:

```powershell
git clone https://github.com/canmils/weekly-report-agent.git
cd weekly-report-agent
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS/Linux:

```sh
git clone https://github.com/canmils/weekly-report-agent.git
cd weekly-report-agent
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Below, `python` means the virtual-environment interpreter: `.\.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux. You can instead activate the environment with `.\.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`. If PowerShell blocks activation, use the direct interpreter path above; activation is optional.

## Optional / paid AI configuration

A ChatGPT subscription does not include OpenAI API credits. Model calls may incur charges. Use only data you are allowed to send to the provider, review generated output, and never include credentials in issues or commits.

Set the key in the terminal that starts the application:

PowerShell:

```powershell
$secret = Read-Host "OpenAI API key" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
Remove-Variable secret
```

This works in Windows PowerShell 5.1 and PowerShell 7. The key remains in this process environment until you close the terminal; do not print it or include it in logs.

macOS/Linux (Bash):

```bash
read -s -p "OpenAI API key: " OPENAI_API_KEY; echo
export OPENAI_API_KEY
```

Restart the app after changing configuration. Never use a `NEXT_PUBLIC_` prefix for a secret.

## First use

```sh
python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://localhost:8501. You can save notes and edit drafts without a key; generation requires `OPENAI_API_KEY`.

1. In **Inputs**, choose Weekly Status, enter description `Fictional demo`, and paste: `Orchard Workshop: art complete; QA starts Monday; sound approval pending with Alex. Next milestone: internal review.`
2. Click **Save Input**, then select it in **Game Report**.
3. With a key configured, click **Generate Weekly Report**. Check names, dates and owners against the source; edit the draft and click **Save Weekly Report**.
4. In **Clan Report**, choose a saved game report and generate/edit/save the team summary. If no report is selected, the latest saved game report is used.

Expected output: Markdown under `reports/saved_inputs/`, `reports/game_reports/`, `reports/clan_reports/`, and source snapshots under `reports/input_snapshots/`. The app does not email anything.

## Scope, data and limitations

Notes and reports are saved locally in plain-text Markdown. Selected text is sent to OpenAI when you generate. Optional `OPENAI_MODEL` defaults to `gpt-4o-mini`. The optional DOCX guideline file is not required. AI output needs human review. This is a single-user local prototype.

## Update your copy

Stop the application with Ctrl+C. Back up the entire `reports/` folder; it contains your saved work. Check `git status` first; commit your edits on a branch before pulling if you have changed tracked files.

```sh
git pull --ff-only
python -m pip install -r requirements.txt
```

Use the same virtual-environment interpreter for Python commands. Restart with the run command above. If pulling reports divergent history, resolve your branch changes rather than forcing or discarding work.

## Troubleshooting

- Command not found: install the prerequisite and reopen the terminal.
- Missing module: install dependencies using the same interpreter or package manager that starts the app.
- Missing file: make sure you are in this repository's root directory and have followed the example setup.
- Port already used: stop the earlier server or select another port where supported.
- Provider error: check key, account credit, model access and internet connectivity. Repeating a model request can incur another charge.

## Verify, report bugs and contribute

Compile/import check: `python -m compileall -q app.py src`. Launch the app and follow the fictional example. A live generation check requires your key and is not part of installation verification.

Report bugs at https://github.com/canmils/weekly-report-agent/issues with your OS, runtime version, commit (`git rev-parse HEAD`), exact command, sanitized error, and expected versus actual result. Feature requests should describe the user problem and a small example. Do not attach credentials or private company data.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the fork → branch → test → pull-request workflow. Installation checks do not establish commercial value, factual accuracy, or AI output quality.

## License

MIT; see [LICENSE](LICENSE). This covers repository code and authored documentation, not third-party data, trademarks, captured content or your private inputs. Retain dependency and upstream notices.

## Offline onboarding tests

`python -m unittest discover -s tests -v` exercises the first-use path with fictional/mocked input. CI runs this on Ubuntu and Windows; a configured workflow is not proof its remote run has passed. Desktop rendering and external-provider availability require separate checks.

## Verification record

See [ONBOARDING_CHECKS.md](ONBOARDING_CHECKS.md) for checks actually run and limits.
