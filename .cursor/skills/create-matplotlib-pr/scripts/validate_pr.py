#!/usr/bin/env python3
"""Check a pull request body before `gh pr create`.

Usage:
    python3 .cursor/skills/create-matplotlib-pr/scripts/validate_pr.py path/to/pr.md

Prints "OK", or lists problems on stderr and exits 1.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    "PR name",
    "Description",
    "Impact",
    "Decisions",
    "AI disclosure",
]

CHECKLIST = "PR quality check"

HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})")
ISSUE_LINK = re.compile(r"\b(Closes|Fixes|Resolves)\s+#\d+\b", re.IGNORECASE)
NO_ISSUE = re.compile(r"^No issue:\s*\S", re.IGNORECASE | re.MULTILINE)
BOX = re.compile(r"^- \[([ xX]|N/A)\] .+", re.MULTILINE)


def sections(text: str) -> tuple[list[str], dict[str, str]]:
    current: str | None = None
    body: dict[str, str] = {}
    order: list[str] = []
    fence: str | None = None

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if fence is not None:
            if current is not None:
                body[current] += line
            if stripped.startswith(fence):
                fence = None
            continue

        opener = FENCE_OPEN.match(stripped)
        if opener:
            fence = opener.group(1)[0] * 3
            if current is not None:
                body[current] += line
            continue

        match = HEADING.match(line.rstrip("\r\n"))
        if match:
            current = match.group(1).strip()
            if current not in body:
                order.append(current)
                body[current] = ""
            continue

        if current is not None:
            body[current] += line

    return order, body


def meaningful(text: str | None) -> str:
    return COMMENT.sub("", text or "").strip()


def validate(text: str) -> list[str]:
    order, body = sections(text)
    errors: list[str] = []

    if order[: len(REQUIRED)] != REQUIRED:
        missing = [heading for heading in REQUIRED if heading not in order]
        if missing:
            errors.append("missing required titles: " + ", ".join(missing))
        else:
            errors.append(
                "the first five titles must be, in order: " + ", ".join(REQUIRED)
            )

    if CHECKLIST not in order:
        errors.append("missing PR quality check")

    for heading in REQUIRED:
        if heading not in order:
            continue
        content = meaningful(body[heading])
        if not content:
            errors.append(f"{heading} is empty")

    name = meaningful(body.get("PR name", ""))
    if name and len([line for line in name.splitlines() if line.strip()]) > 1:
        errors.append("PR name must be a single line")

    description = meaningful(body.get("Description", ""))
    if description and not ISSUE_LINK.search(description) and not NO_ISSUE.search(description):
        errors.append(
            "Description must contain Closes #N, Fixes #N, or Resolves #N, "
            "or a line `No issue: <reason>`"
        )

    checklist = body.get(CHECKLIST, "")
    boxes = BOX.findall(checklist)
    if CHECKLIST in order and len(boxes) != 5:
        errors.append("PR quality check must contain the five template boxes")
    if any(mark == " " for mark in boxes):
        errors.append("PR quality check has an unmarked box; use x or N/A")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_pr.py PR.md", file=sys.stderr)
        return 1
    path = Path(argv[1])
    if not path.is_file():
        print("usage: validate_pr.py PR.md", file=sys.stderr)
        return 1
    errors = validate(path.read_text(encoding="utf-8"))
    if not errors:
        print("OK")
        return 0
    print("pull request body is incomplete:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
