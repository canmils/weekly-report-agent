# Contributing

Read README.md first: scope, first-use workflow, limitations and verification commands describe the supported project. Documentation, reproducible bug reports, accessibility fixes, fictional examples and small scoped changes are welcome.

## Report or suggest

Use https://github.com/canmils/weekly-report-agent/issues. Include the user problem, expected and actual result, OS/runtime versions, exact command and commit (`git rev-parse HEAD`). Include the smallest reproducible fictional/public input. Remove keys, personal data, private company material and generated commercial data. A feature request should explain who benefits and how you would verify the result.

## Change and submit

1. Fork the repository using GitHub's Fork button (private repository contributors need granted access; forks can be restricted).
2. Clone your fork; add this repository as upstream: `git remote add upstream https://github.com/canmils/weekly-report-agent.git`.
3. Create a branch: `git switch -c improve-onboarding`.
4. Install according to README.md, make one focused change and update relevant examples/docs.
5. Run the README verification commands. Record unavailable checks and why; do not describe mocked AI tests as live provider validation.
6. Check `git diff` and `git status` for unintended files/secrets. Commit only intended files, push the branch and open a pull request to this repository's default branch.
7. Explain the problem, resulting behavior, verification and any remaining limitations. Maintainers review before merging.

To update a fork, fetch upstream and merge its default branch into your own branch; do not force-push shared history. Preserve local inputs and outputs before changing versions.

## Data and ownership

Use fictional, public-permitted or explicitly licensed fixtures. Keep real company data outside version control. Preserve existing attribution and license notices. A repository without a license does not grant a general reuse license; consult its README/license status before redistributing. Never upload confidential reports, API keys or personal details in logs/screenshots.
