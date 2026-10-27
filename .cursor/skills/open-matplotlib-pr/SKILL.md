---
name: open-matplotlib-pr
description: Open a Matplotlib pull request using doc/devel/pr_guide.rst and the branch rules in doc/devel/development_workflow.rst. Covers the author checklist, draft PRs, milestones, tests, docs, and API notes. Use when preparing, opening, or updating a pull request.
---

# Open a Matplotlib pull request

The sources are `doc/devel/pr_guide.rst` and `doc/devel/development_workflow.rst`. If this skill and those files disagree, follow the files. Fill `.github/PULL_REQUEST_TEMPLATE.md`.

## Before opening

Work on a feature branch whose name says what the change is. Target `main`. Do not merge `main` into the feature branch. Rebase onto `upstream/main` when the branch must pick up new commits, then push with `--force-with-lease`.

Check the items that apply:

- Tests cover the behavior change. Follow `write-matplotlib-tests`.
- Public methods have numpydoc docstrings. A high-level plotting function has a short example, in the docstring or in `galleries/examples`.
- An API or appearance change has a note under `doc/api/next_api_changes/` or `doc/release/next_whats_new/`. Follow `change-matplotlib-api`.
- New or changed public signatures have type hints. Follow `follow-matplotlib-coding-guide`.
- `ruff check` is clean. Pre-commit spelling and formatting pass when the hooks are installed.

The title describes the change, for example `Add ability to plot timedeltas`. If a GitHub issue exists, the body contains `Closes #8869` or `Fixes #8869`.

A PR that is not ready for a full review is a draft. Say why, and ask for the specific feedback you want. Reviewers do not read draft code unless asked.

## What the body must show

Use the repository template: PR summary, AI disclosure, and the quality checklist. Mark a box `x` or `N/A`. State AI use in the disclosure. See `disclose-matplotlib-ai`.

## Milestone, when you can set one

Pick the first rule that matches:

| Change | Milestone |
|---|---|
| New feature or API change | next meso release `v3.N.0` |
| Bugfix, test of released code, or docstring | next micro release `v3.N.M` |
| Only `.rst` files and examples | `v3.N-doc` |

Code under `src/` or `lib/` needs two maintainer approvals. Documentation and example PRs of small or medium size can merge on one. Do not self-merge unless a reviewer says so.

Pure formatting that is not part of a behavior change stays out of the PR. It hides the history of the real change.
