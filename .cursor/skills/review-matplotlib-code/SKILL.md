---
name: review-matplotlib-code
description: Review Matplotlib changes for rules, coding conventions, bugs, and human-readable comments. Use when reviewing a pull request, a diff, or when the user asks for a code review or an approval. Approve only after the regression run has passed.
---

# Review Matplotlib code

Make sure all the rules and coding conventions are being followed. Look for any bug and make sure code is commented so it is human readable. Only approve after you have run a regression test on it and checked everything has passed.

## Read first

Read the diff, then the rules and guides that apply. If a skill and its source file disagree, follow the source file.

- `.cursor/rules/new-dependencies.mdc`
- `.cursor/rules/no-deprecated-apis.mdc`
- `.cursor/rules/tests-required.mdc`
- `follow-matplotlib-coding-guide` (`doc/devel/coding_guide.rst`)
- `write-matplotlib-tests` (`doc/devel/testing.rst`)
- `write-matplotlib-docs` (`doc/devel/document.rst`)
- `change-matplotlib-api` when the diff changes public API or appearance
- `open-matplotlib-pr` and `disclose-matplotlib-ai` when the review is a pull request

## Check the change

1. **Rules and conventions.** Every always-applied rule above holds. A behavior change has a test that asserts the outcome. A new library is named in the PR summary and listed in every place `new-dependencies.mdc` names. New code does not call a deprecated Matplotlib API. Style matches `doc/devel/coding_guide.rst`: ruff, 88-character lines, `fig` / `ax` names, type stubs, and logging.
2. **Bugs.** Walk the changed paths for wrong results, unhandled edges (empty input, a sequence where a scalar was assumed, the failure path), races, and leaks. A test that only calls a function does not lock the behavior.
3. **Comments.** A reader can follow the change without guessing. Non-obvious logic has a comment that says what it is doing. Place that comment before the code or on the same line, as `doc/devel/style_guide.rst` requires. Do not leave a comment on the following line.

## Regression

Follow `run-matplotlib-regression`. Do not set `MPLBACKEND`.

1. Run the new or affected test.
2. If it passes, run that test module.
3. Run the full suite: `xvfb-run -a pytest -n 2 --tb=line --timeout=180`.
4. If the diff has tests outside `lib/matplotlib/tests/`, run those as well. They are not in the suite above.

Report passed, failed, skipped, and xfailed. List every failed node id with the first error line. Skips and expected failures that match the known optional-dependency results in `run-matplotlib-regression` do not block approval. A new failure does.

## Approve

Approve only when the checks above are clean and the regression run has no failures.

On a pull request:

```bash
gh pr review <number> --approve --body "<regression command and pass counts>"
```

The body names the command and the pass, fail, skip, and xfail counts.

If a rule, a bug, a missing comment, or a test failure remains, request changes and do not approve.

## Review

```markdown
## Verdict
Approve or request changes.

## Rules and conventions
- file:line — which rule or guide, and what to change

## Bugs
- file:line — what breaks, and the edge that shows it

## Comments
- file:line — what a reader cannot follow

## Regression
Command, passed / failed / skipped / xfailed, and every failed node id.
```
