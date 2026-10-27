#!/usr/bin/env python3
"""Check an issue body before `gh issue create`.

Usage:
    python3 .cursor/skills/create-matplotlib-issue/scripts/validate_issue.py path/to/issue.md

Prints "OK", or lists problems on stderr and exits 1.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED = [
    "Issue name",
    "Issue type",
    "Impact",
    "Description",
]

EXTRA = {
    "bug": [
        "Code for reproduction",
        "Actual outcome",
        "Expected outcome",
        "Environment",
        "Affected component",
    ],
    "regression": [
        "Code for reproduction",
        "Actual outcome",
        "Expected outcome",
        "Last known good version",
        "Environment",
        "Affected component",
    ],
    "feature": [
        "Problem",
        "Proposed solution",
        "Affected component",
    ],
    "documentation": [
        "Documentation link",
        "Problem",
        "Suggested improvement",
    ],
    "maintenance": [
        "Summary",
        "Proposed fix",
        "Affected component",
    ],
    "tag": [
        "Need",
        "Proposed tag",
    ],
}

COMPONENTS = {
    "pyplot",
    "axes",
    "figure",
    "artist",
    "image",
    "colors",
    "colorbar",
    "cm",
    "animation",
    "widgets",
    "axis",
    "ticker",
    "dates",
    "units",
    "text",
    "legend",
    "contour",
    "collections",
    "patches",
    "transforms",
    "lines",
    "markers",
    "spines",
    "scale",
    "style",
    "font_manager",
    "mathtext",
    "texmanager",
    "path",
    "quiver",
    "streamplot",
    "tri",
    "table",
    "inset",
    "offsetbox",
    "projections",
    "rcsetup",
    "backend",
    "cbook",
    "category",
    "patheffects",
    "hatch",
    "testing",
    "documentation",
    "gallery",
    "general",
    "mpl_toolkits.mplot3d",
    "mpl_toolkits.axes_grid1",
    "mpl_toolkits.axisartist",
}

INSTALLATIONS = {
    "pip",
    "conda",
    "pixi",
    "uv",
    "linux package manager",
    "from source (.tar.gz)",
    "git checkout",
    "unknown",
    "n/a",
}

HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})")
TAG_LINE = re.compile(r"^(?!\s*https?:)([^:\n]{2,40}):\s*(\S.*?)\s*$", re.IGNORECASE)


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


def first_line(text: str) -> str:
    lines = [line.strip() for line in meaningful(text).splitlines() if line.strip()]
    return lines[0] if lines else ""


def labeled_value(section: str, label: str) -> str | None:
    pattern = re.compile(
        rf"^\s*(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:\s*(.*?)\s*$",
        re.IGNORECASE,
    )
    for line in COMMENT.sub("", section).splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


def has_executable_python(section: str) -> bool:
    blocks = re.findall(r"```[^\n]*\n(.*?)```", section, flags=re.DOTALL)
    for block in blocks:
        for line in block.splitlines():
            code = line.strip()
            if code and not code.startswith("#"):
                return True
    return False


def validate(text: str) -> list[str]:
    order, body = sections(text)
    errors: list[str] = []

    if order[: len(REQUIRED)] != REQUIRED:
        missing = [heading for heading in REQUIRED if heading not in order]
        if missing:
            errors.append("missing required headings: " + ", ".join(missing))
        else:
            errors.append(
                "the first four headings must be, in order: " + ", ".join(REQUIRED)
            )

    issue_type = first_line(body.get("Issue type", "")).lower()
    if not issue_type:
        errors.append("Issue type is empty")
    elif re.search(r"\s", issue_type):
        errors.append("Issue type must be a single word")

    known_extra = EXTRA.get(issue_type)
    if known_extra:
        extra_missing = [heading for heading in known_extra if heading not in order]
        if extra_missing:
            errors.append(
                f"missing {issue_type} headings: " + ", ".join(extra_missing)
            )
    elif issue_type and "Affected component" not in order:
        errors.append(f"missing Affected component for issue type {issue_type}")

    check_headings = REQUIRED + (known_extra or ["Affected component"])
    for heading in check_headings:
        if heading not in order:
            continue
        content = meaningful(body[heading])
        if not content:
            errors.append(f"{heading} is empty")
        if "[REPLACE ME]" in content:
            errors.append(f"{heading} still contains [REPLACE ME]")

    name = meaningful(body.get("Issue name", ""))
    if name:
        if len([line for line in name.splitlines() if line.strip()]) > 1:
            errors.append("Issue name must be a single line")
        if name.lstrip().startswith("["):
            errors.append(
                "Issue name must not include the title prefix; add [Bug]:, [ENH]:, [Doc]:, [MNT]:, or [Tag]: only in the GitHub title"
            )

    if issue_type in {"bug", "regression"} and "Code for reproduction" in order:
        if not has_executable_python(body["Code for reproduction"]):
            errors.append(
                "Code for reproduction must include a fenced Python snippet with executable lines"
            )

    if issue_type in {"bug", "regression"} and "Environment" in order:
        version = labeled_value(body["Environment"], "Matplotlib version")
        if version is None:
            errors.append("Environment is missing Matplotlib version")
        elif not version:
            errors.append("Matplotlib version is empty")
        install = labeled_value(body["Environment"], "Installation")
        if install and install.lower() not in INSTALLATIONS:
            allowed = ", ".join(sorted(INSTALLATIONS))
            errors.append(f"Installation must be one of: {allowed}")

    if "Affected component" in order:
        component = first_line(body["Affected component"]).lower()
        if component and component not in COMPONENTS:
            errors.append(
                "Affected component must be one of: " + ", ".join(sorted(COMPONENTS))
            )

    if issue_type == "tag" and "Proposed tag" in order:
        tag_body = meaningful(body["Proposed tag"])
        if tag_body and not any(TAG_LINE.match(line) for line in tag_body.splitlines()):
            errors.append(
                "Proposed tag must contain a line in the form `subcategory: tag`"
            )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_issue.py ISSUE.md", file=sys.stderr)
        return 1
    path = Path(argv[1])
    if not path.is_file():
        print("usage: validate_issue.py ISSUE.md", file=sys.stderr)
        return 1
    errors = validate(path.read_text(encoding="utf-8"))
    if not errors:
        print("OK")
        return 0
    print("issue body is incomplete:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
