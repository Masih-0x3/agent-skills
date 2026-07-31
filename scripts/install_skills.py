#!/usr/bin/env python3
"""Install one or more skills with staging, validation, and rollback safety."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Callable, TypeVar

from skilllib import ROOT, SKILLS, SOURCE_LOCK, parse_skill, skill_names

TARGETS = {
    "agents": lambda: Path.home() / ".agents" / "skills",
    "codex": lambda: Path.home() / ".codex" / "skills",
    "claude": lambda: Path.home() / ".claude" / "skills",
    "grok": lambda: Path.home() / ".grok" / "skills",
    "hermes": lambda: Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / "skills" / "software-development",
    "cursor": lambda: Path.cwd() / ".cursor" / "skills",
    "copilot": lambda: Path.cwd() / ".github" / "skills",
}

T = TypeVar("T")


def retry_transient_lock(operation: Callable[[], T], attempts: int = 8) -> T:
    """Retry filesystem operations briefly when a Windows scanner holds a handle."""
    delay = 0.05
    for attempt in range(attempts):
        try:
            return operation()
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 0.5)
    raise AssertionError("unreachable")


def copy_skill(source: Path, destination_root: Path, name: str, dry_run: bool) -> None:
    destination_root = destination_root.expanduser().resolve()
    destination = destination_root / name
    print(f"{'Would install' if dry_run else 'Installing'} {name} -> {destination}")
    if dry_run:
        return
    destination_root.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    staging = destination_root / f".{name}.staging-{token}"
    backup = destination_root / f".{name}.backup-{token}"

    def ignore(_: str, entries: list[str]) -> set[str]:
        return {
            entry for entry in entries
            if entry == "__pycache__" or entry.endswith((".pyc", ".pyo", ".db", ".db-journal", ".db-wal", ".db-shm"))
        }

    swapped = False
    try:
        shutil.copytree(source, staging, ignore=ignore)
        if not (staging / "SKILL.md").is_file():
            raise RuntimeError(f"staged package lacks SKILL.md: {name}")
        if destination.exists():
            retry_transient_lock(lambda: destination.rename(backup))
        retry_transient_lock(lambda: staging.rename(destination))
        swapped = True
        if backup.exists():
            retry_transient_lock(lambda: shutil.rmtree(backup))
    except Exception:
        if not swapped:
            if destination.exists() and backup.exists():
                retry_transient_lock(lambda: shutil.rmtree(destination))
                retry_transient_lock(lambda: backup.rename(destination))
            elif backup.exists() and not destination.exists():
                retry_transient_lock(lambda: backup.rename(destination))
        if staging.exists():
            retry_transient_lock(lambda: shutil.rmtree(staging))
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skills", nargs="*", help="skill names; defaults to the full library")
    parser.add_argument("--target", choices=[*TARGETS, "both", "all", "custom"], default="both")
    parser.add_argument("--destination", type=Path, help="required for --target custom")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    available = skill_names()
    selected = args.skills or available
    unknown = sorted(set(selected) - set(available))
    if unknown:
        parser.error(f"unknown skill(s): {', '.join(unknown)}")
    lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    blocked = {name for name, policy in lock.get("compatibility", {}).items() if policy.get("installable") is False}
    selected = [name for name in selected if name not in blocked]
    skipped = sorted(set(args.skills or available) - set(selected))
    for name in selected:
        parse_skill(name)
    if args.target == "custom":
        if args.destination is None:
            parser.error("--destination is required with --target custom")
        destinations = [args.destination]
    elif args.target == "both":
        destinations = [TARGETS["agents"](), TARGETS["codex"]()]
    elif args.target == "all":
        destinations = [TARGETS[name]() for name in ("agents", "codex", "claude", "grok", "hermes")]
    else:
        destinations = [TARGETS[args.target]()]
    for destination in destinations:
        for name in selected:
            copy_skill(SKILLS / name, destination, name, args.dry_run)
    print(f"Processed {len(selected)} skill(s) for {len(destinations)} destination(s)")
    if skipped:
        print(f"Skipped blocked skill(s): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
