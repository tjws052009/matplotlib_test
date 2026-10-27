#!/usr/bin/env python3
"""Spin up a Cursor cloud agent that runs the Matplotlib test application.

The agent starts on the given main SHA. It runs pytest and does not edit the
repository. CURSOR_API_KEY is read from the environment.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request

REPO_URL = "https://github.com/tjws052009/matplotlib_test"
API_URL = "https://api.cursor.com/v1/agents"
PROMPT = """Run the Matplotlib test application on this checkout. Do not edit files, commit, push, or open a pull request.

Follow .cursor/skills/run-matplotlib-regression/SKILL.md. Do not set MPLBACKEND.

From the repository root, with the editable install on PATH, run:

xvfb-run -a pytest -n 2 --tb=line --timeout=180

Reply with passed, failed, skipped, and xfailed, and list every failed node id with the first error line.

These six node ids are known when the first error line is subprocess.TimeoutExpired. Report them, and do not treat them as blocking failures:

- lib/matplotlib/tests/test_backends_interactive.py::test_interactive_thread_safety[MPLBACKEND=tkagg-BACKEND_DEPS=tkinter]
- lib/matplotlib/tests/test_backends_interactive.py::test_lazy_auto_backend_selection
- lib/matplotlib/tests/test_backends_interactive.py::test_qt_missing
- lib/matplotlib/tests/test_backends_interactive.py::test_blitting_events[MPLBACKEND=tkagg-BACKEND_DEPS=tkinter]
- lib/matplotlib/tests/test_backends_interactive.py::test_fallback_to_different_backend
- lib/matplotlib/tests/test_backends_interactive.py::test_interactive_timers[MPLBACKEND=tkagg-BACKEND_DEPS=tkinter]

Any other failure is blocking, including subprocess.TimeoutExpired on a different test.
"""


def _sha(value: str) -> str:
    sha = value.strip().lower()
    if len(sha) != 40 or any(char not in "0123456789abcdef" for char in sha):
        raise ValueError("git sha must be 40 hex characters")
    return sha


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "usage: start_test_application.py <40-character-sha>",
            file=sys.stderr,
        )
        return 2
    try:
        sha = _sha(argv[1])
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    key = os.environ.get("CURSOR_API_KEY", "")
    if not key:
        print("CURSOR_API_KEY is not set", file=sys.stderr)
        return 2

    body = {
        "name": "Matplotlib test application",
        "prompt": {"text": PROMPT},
        "repos": [{"url": REPO_URL, "startingRef": sha}],
        "autoCreatePR": False,
        "workOnCurrentBranch": False,
    }
    token = base64.b64encode(f"{key}:".encode()).decode("ascii")
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        print(f"cloud agent API returned {error.code}: {detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"cloud agent API request failed: {error.reason}", file=sys.stderr)
        return 1

    agent = payload.get("agent") or {}
    run = payload.get("run") or {}
    url = agent.get("url")
    if not url:
        print("cloud agent API response did not include an agent url", file=sys.stderr)
        return 1

    json.dump(
        {
            "agentId": agent.get("id"),
            "runId": run.get("id"),
            "url": url,
            "startingRef": sha,
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
