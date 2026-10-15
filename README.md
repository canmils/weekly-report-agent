# Weekly Report Agent

A local Streamlit draft assistant for game producers: paste production notes, draft a weekly report by game, review it, then summarize one saved report for your team (called a **clan** in the UI).

**Status: local single-user prototype.** It does not fetch Jira, contact colleagues, send email or verify project facts. It is useful for organizing notes and reviewing drafts; time savings and commercial value have not been measured.

| Input | Action | Result |
| --- | --- | --- |
| Pasted weekly status/call notes | Save Input | Local Markdown source |
| Selected saved inputs | Generate Weekly Report | Editable OpenAI draft |
| Reviewed draft | Save Weekly Report | New Markdown file and input snapshots |
| One explicitly selected saved game report | Generate Clan Weekly Report | Editable team summary |

## Install and launch

Requires Git, Python **3.11 or 3.12**, and internet for dependency installation. Run from the repository root. No API key is needed to save inputs, manually edit/save reports, or run offline tests.

Windows PowerShell (activation is unnecessary):

```powershell
git clone https://github.com/canmils/weekly-report-agent.git
cd weekly-report-agent
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

macOS/Linux:

```sh
git clone https://github.com/canmils/weekly-report-agent.git
cd weekly-report-agent
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://localhost:8501. Keep the terminal running; Ctrl+C stops the server.

## First use: free local walkthrough

The [worked example](examples/README.md) provides fictional source notes and **human-written reference reports**. They demonstrate an acceptable result, not measured model quality.

1. Open **Inputs**. Choose **Weekly Status**, enter description `Orchard Workshop demo`, and paste [source-notes.md](examples/source-notes.md). Click **Save Input**.
2. Open **Game Report**. Verify the source checkbox under **Inputs to Use** is selected. Without a key, **Generate Weekly Report** shows an explicit configuration error.
3. For a free manual walkthrough, paste [game-report.md](examples/game-report.md) into **Draft**. Review and click **Save Weekly Report**. A new entry appears under **Saved Game Reports**.
4. Open **Clan Report**. Choose that report in **Saved game report to summarize**. AI generation requires a key; for the free walkthrough paste [clan-report.md](examples/clan-report.md) into **Draft**, then click **Save Clan Weekly Report**.
5. Stop and restart the server. Saved inputs/reports reappear. Unsaved editor text does not survive a fresh session.

Each save creates a new timestamped file, including repeated saves. **View** loads a report into the editor; saving creates a new copy rather than updating the original. Delete requires confirmation and removes that report/input file. Deleting a game report does not delete its separate input snapshot folder.

## Enable paid generation

`OPENAI_API_KEY` is **required for either Generate button**. A ChatGPT subscription does not supply API credits. Set the key in the terminal that launches the server, then restart it. The app does **not** load `.env` files automatically.

PowerShell 5.1/7:

```powershell
$secret = Read-Host "OpenAI API key" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
Remove-Variable secret
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Bash on macOS/Linux:

```bash
read -s -p "OpenAI API key: " OPENAI_API_KEY; echo
export OPENAI_API_KEY
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

Optional `OPENAI_MODEL` defaults to `gpt-4o-mini`. Other models must support the existing Chat Completions parameters; arbitrary model compatibility is not established. Each generation invokes one application-level model request; SDK retries can make additional requests. There is no application spending cap.

After adding a key, repeat the walkthrough using the Generate buttons instead of pasting reference reports. Check every date, owner, dependency and approval against the source before saving or sharing. Clan generation summarizes **one selected saved game-report file**, which can itself contain multiple games. It does not combine all saved reports, and never silently chooses the latest one.

## Data, backup and recovery

| Path | Contains |
| --- | --- |
| `reports/saved_inputs/` | Original notes with type/description metadata |
| `reports/game_reports/` | Saved game reports |
| `reports/clan_reports/` | Saved team summaries |
| `reports/input_snapshots/<report-name>/` | Source copies for a newly generated game draft, or currently selected inputs for a new manual draft |

Changing selected inputs after generation does not change the generated draft's captured source copies. Loading an existing report with **View** clears source attribution for the new editor copy; the original snapshot remains on disk. Clan source labels are session state, not a durable audit trail.

Stop the server and back up the **entire `reports/` directory** before updating or deleting work. To restore, stop the app and restore that folder to the same repository root, then restart. Test restores using a separate copy. Markdown files can also be opened directly in a text editor. Malformed input files may be skipped during loading; retain their original format.

Inputs/reports are local plain text, without application encryption or accounts. `reports/` is gitignored. Selected source text is sent to OpenAI for game generation; clan generation sends the selected saved report and any local optional guideline text. Use only permitted data. Do not expose this development server publicly or commit credentials/company reports.

## Limits and supported code

- AI can omit or invent details despite prompts. It cannot approve releases, resolve conflicting evidence or certify facts.
- Draft editors are temporary until saved. Source snapshots help review but are not a compliance-grade audit log.
- Clan means team; no shared workspace or multi-user permissions are implemented.
- Optional `prompts/Guideline for Writing Effective Weekly Status Updates.docx` adds clan writing guidance. It is not bundled or required. The built-in prompt works without it.
- Supported UI: `app.py`, `src/state.py`, `src/ui_inputs.py`, `src/ui_reports.py`, `src/ai_writer.py`. Other parser/batch scripts and prompt text files are legacy utilities and are not the documented UI pipeline.

## Update and troubleshoot

Stop the app, back up `reports/`, and inspect `git status`. Preserve tracked changes on your own branch before pulling. Then run:

```sh
git pull --ff-only
```

Reinstall with the **same virtual-environment pip command used above**, then relaunch. Resolve divergent Git history rather than discarding local work.

| Problem | Check |
| --- | --- |
| Python/Git not found | Install prerequisite, reopen terminal, check its version |
| Missing module | Use the same `.venv` interpreter for install and launch |
| Missing key | Set the environment in the launch terminal and restart; `.env` alone is insufficient |
| Provider rejects generation | Check account billing/model access/connectivity; previous draft is retained on failure |
| Port 8501 occupied | Stop the other app or append `--server.port 8502` and open that port |
| Saved work appears missing | Check working directory; inspect `reports/` and restore backup if necessary |
| Unsaved draft disappeared | Only saved files are durable; no automatic draft recovery is implemented |

## Verify and contribute

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS/Linux:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Tests use real Streamlit state and temporary files with mocked model output; they do not call OpenAI. [Verification record](ONBOARDING_CHECKS.md) distinguishes actual checks from unverified behavior. [GitHub Actions](https://github.com/canmils/weekly-report-agent/actions/workflows/onboarding.yml) runs tests on Ubuntu and Windows.

Report [bugs or suggestions](https://github.com/canmils/weekly-report-agent/issues) with OS/Python version, commit (`git rev-parse HEAD`), exact steps, fictional input, sanitized error and expected/actual behavior. Useful feedback: corrections required, lost context, missing workflow steps and whether it improves on your current process. Never attach keys or private reports. See [CONTRIBUTING.md](CONTRIBUTING.md) for fork, branch and pull-request instructions.

## License

[MIT](LICENSE) for repository code/authored documentation. Third-party content and your inputs retain their own rights.
