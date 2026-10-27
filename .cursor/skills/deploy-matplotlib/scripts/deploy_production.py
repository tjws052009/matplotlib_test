#!/usr/bin/env python3
"""Virtual production deploy API.

At this moment this is a noop. It does not contact a service, upload an
artifact, push a tag, or change a branch.
"""

from __future__ import annotations

import json
import sys


def _sha(value: str) -> str:
    sha = value.strip().lower()
    if len(sha) != 40 or any(char not in "0123456789abcdef" for char in sha):
        raise ValueError("git sha must be 40 hex characters")
    return sha


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: deploy_production.py <40-character-sha>", file=sys.stderr)
        return 2
    try:
        sha = _sha(argv[1])
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    json.dump(
        {
            "api": "production-deploy",
            "sha": sha,
            "result": "noop",
            "deployed": False,
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
