#!/usr/bin/env python3
"""Fail closed unless the current origin is the canonical skills repository."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

EXPECTED = "Masih-0x3/agent-skills"
ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    remote = result.stdout.strip().removesuffix(".git")
    match = re.search(r"github\.com[/:]([^/]+/[^/]+)$", remote)
    actual = match.group(1) if match else ""
    if actual.casefold() != EXPECTED.casefold():
        print(f"REFUSED: origin resolves to {actual or remote!r}; expected {EXPECTED!r}")
        return 1
    print(f"Repository target verified: {EXPECTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
