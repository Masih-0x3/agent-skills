#!/usr/bin/env python3
"""Fail closed unless the current origin is the canonical skills repository."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED = "Masih-0x3/agent-skills"
ROOT = Path(__file__).resolve().parent.parent


def repository_from_remote(remote: str) -> str:
    """Return owner/repository only for an exact github.com remote."""
    value = remote.strip()

    # Git's SCP-style SSH syntax: git@github.com:owner/repository.git
    if "://" not in value:
        host_and_path = value.split(":", 1)
        if len(host_and_path) != 2:
            return ""
        host = host_and_path[0].rsplit("@", 1)[-1]
        path = host_and_path[1]
    else:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        path = parsed.path

    if host.casefold() != "github.com":
        return ""

    parts = path.strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        return ""
    parts[1] = parts[1].removesuffix(".git")
    return "/".join(parts) if parts[1] else ""


def main() -> int:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    remote = result.stdout.strip()
    actual = repository_from_remote(remote)
    if actual.casefold() != EXPECTED.casefold():
        print(f"REFUSED: origin resolves to {actual or remote!r}; expected {EXPECTED!r}")
        return 1
    print(f"Repository target verified: {EXPECTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
