---
name: deploy-matplotlib
description: Deploy the Matplotlib fork from main. Assumes main is deployable anytime. Runs a final regression test, spins up a Cursor cloud agent with the test application running on that commit, waits for final approval from the user, then kicks a virtual production API that is a noop. Use when the user asks to deploy Matplotlib, ship main, or release tjws052009/matplotlib_test to production.
---

# Deploy Matplotlib

The main branch is deployable anytime. Deploy the current `main` commit of `https://github.com/tjws052009/matplotlib_test`. Do not wait for a release branch, a tag, CircleCI, or an upstream GitHub Actions result.

Do these steps in order. Stop at the first one that does not pass.

1. Run a final regression test.
2. Spin up a cloud agent with the test application running on top of it.
3. Wait for the final approval from the user.
4. Deploy to production by kicking a virtual API. At this moment, do not do anything else. The virtual API is a noop.

Pytest follows `run-matplotlib-regression`. If this skill and that skill disagree about the test command, follow that skill.

## Record main

```bash
git fetch origin main
git rev-parse origin/main
```

Keep the 40-character SHA. Every later command uses that SHA.

## Final regression test

From the root of that checkout, with the editable install on `PATH`. Do not set `MPLBACKEND`.

```bash
xvfb-run -a pytest -n 2 --tb=line --timeout=180
```

Report passed, failed, skipped, and xfailed. List every failed node id with the first error line.

Six interactive-backend failures are known and do not stop the deploy. Ignore a failure only when its node id is in this list and its first error line is `subprocess.TimeoutExpired`:

- `lib/matplotlib/tests/test_backends_interactive.py::test_interactive_thread_safety[MPLBACKEND=tkagg-BACKEND_DEPS=tkinter]`
- `lib/matplotlib/tests/test_backends_interactive.py::test_lazy_auto_backend_selection`
- `lib/matplotlib/tests/test_backends_interactive.py::test_qt_missing`
- `lib/matplotlib/tests/test_backends_interactive.py::test_blitting_events[MPLBACKEND=tkagg-BACKEND_DEPS=tkinter]`
- `lib/matplotlib/tests/test_backends_interactive.py::test_fallback_to_different_backend`
- `lib/matplotlib/tests/test_backends_interactive.py::test_interactive_timers[MPLBACKEND=tkagg-BACKEND_DEPS=tkinter]`

Any other failure stops the deploy, including a `subprocess.TimeoutExpired` on a different test and a different error on one of these six. Do not start the cloud agent while a blocking failure remains. The suite must finish. An interrupted run does not pass.

If `import matplotlib` fails, follow the build steps in `run-matplotlib-regression`, then run the same command again.

## Cloud agent

Run this only after the final regression test has finished with no blocking failures:

```bash
python3 scripts/start_test_application.py <sha>
```

Run that from this skill's `scripts/` directory. In a Matplotlib checkout where the skill is installed, the directory is `.cursor/skills/deploy-matplotlib/scripts/`.

The script spins up a cloud agent on that SHA with the test application running on top of it. The test application is the same pytest command. The agent does not edit files, commit, or open a pull request.

`CURSOR_API_KEY` must already be in the environment. Do not print the key, and do not pass it as an argument. If it is missing, stop and tell the user. Do not kick the virtual API.

Send the user the `url` from the script's JSON.

## Final approval

Stop this turn after you send the SHA, the regression counts, and the cloud agent URL.

Final approval is a later message in which the user approves that SHA. The earlier request to deploy is not final approval. Silence is not approval. Do not approve it yourself.

If the user names a different SHA, start over from the final regression test.

## Virtual production API

After final approval, and only then:

```bash
python3 scripts/deploy_production.py <sha>
```

Run that from this skill's `scripts/` directory.

At this moment, we will not do anything, just a noop. The script is the virtual API. It does not contact a service, upload an artifact, push a tag, or run `.circleci/deploy-docs.sh`. Do not add a real deploy beside it.

Reply with the SHA, the regression counts, the cloud agent URL, the approval, and the JSON the script prints.
