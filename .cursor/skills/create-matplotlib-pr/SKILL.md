---
name: create-matplotlib-pr
description: Open a Matplotlib pull request whose body matches .github/PULL_REQUEST_TEMPLATE.md, links a GitHub issue, and includes PR name, Description, Impact, Decisions, and AI disclosure. Use when the user asks to create, open, or draft a pull request.
---

# Create a Matplotlib pull request

The PR should be connected to an issue as much as possible. Titles should atleast include: PR name, Description, Impact, Decisions, AI disclosure.

Follow existing PR conventions. Branch, tests, docs, draft status, and milestone come from `open-matplotlib-pr`, `doc/devel/pr_guide.rst`, and `doc/devel/development_workflow.rst`. If this skill and those files disagree, follow the files. AI wording comes from `disclose-matplotlib-ai`.

The GitHub template is `.github/PULL_REQUEST_TEMPLATE.md`. The body to fill is [templates.md](templates.md). Both use the same headings, in the same order.

## Required titles

The body starts with these titles, in this order, spelled exactly this way. Do not rename, drop, or reorder them.

1. PR name
2. Description
3. Impact
4. Decisions
5. AI disclosure

Then keep `PR quality check` from the GitHub template. Mark each box `x` or `N/A`.

`PR name` is one line. It is the GitHub title. Do not put the other titles into the GitHub title.

## Connect an issue

Search this repository before opening the pull request:

```bash
gh issue list --state open --limit 20 --search "keywords from the PR name"
gh issue list --state closed --limit 10 --search "keywords from the PR name"
```

Use the issue that matches. In `Description`, write `Closes #8869` for a change that finishes the issue, or `Fixes #8869` for a bugfix. GitHub closes the issue only when that keyword is in the body.

If no issue matches, file one with `create-matplotlib-issue`, then link it. Skip creating an issue only when the user explicitly said not to. Say that in `Decisions`, and in `Description` write `No issue: <reason>`.

## Workflow

1. Finish the checks in `open-matplotlib-pr`. Do not open a pull request for a change that is not on a feature branch targeting `main`.
2. Copy [templates.md](templates.md). Fill every title. Strip the HTML comments before filing.
3. Write the body to a temp file and validate it. Fix every reported line and run it again. File only after it prints `OK`.

```bash
python3 .cursor/skills/create-matplotlib-pr/scripts/validate_pr.py /tmp/mpl-pr.md
```

4. Create the pull request only when the user asked to open it. A draft request stops after the validated body, unless they asked for a draft pull request.

```bash
gh pr create --title "<PR name line>" --body-file /tmp/mpl-pr.md
```

Add `--draft` when the change is not ready for a full review. The body says why.

5. Reply with the pull request URL and the issue it closes.

## Section rules

- **PR name.** The change, in the form `Add ability to plot timedeltas`.
- **Description.** What changed and why this solution. Include the issue keyword here.
- **Impact.** Who is affected, and what behavior or docs change. Do not repeat Description verbatim.
- **Decisions.** What was chosen and what was rejected. Write `None.` when there are none.
- **AI disclosure.** How AI was used, or `No AI was used.` Follow `disclose-matplotlib-ai`.
