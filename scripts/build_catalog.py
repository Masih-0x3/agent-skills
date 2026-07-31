#!/usr/bin/env python3
"""Generate a lightweight inventory of the portable skill packages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CATALOG = ROOT / "catalog" / "skills.json"


def value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?(.+?)[\"']?\s*$", frontmatter, re.M)
    return match.group(1).strip() if match else None


def main() -> None:
    entries = []
    for skill_file in sorted(SKILLS.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match:
            raise SystemExit(f"Missing YAML frontmatter: {skill_file}")
        skill_dir = skill_file.parent
        frontmatter = match.group(1)
        entries.append({
            "id": skill_dir.name,
            "name": value(frontmatter, "name") or skill_dir.name,
            "description": value(frontmatter, "description") or "",
            "path": skill_dir.relative_to(ROOT).as_posix(),
            "file_count": sum(1 for path in skill_dir.rglob("*") if path.is_file()),
        })
    CATALOG.parent.mkdir(exist_ok=True)
    CATALOG.write_text(json.dumps({
        "schema_version": 2,
        "description": "Portable snapshot of the owner's personal and approved third-party skills.",
        "skill_count": len(entries),
        "skills": entries,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {CATALOG.relative_to(ROOT)} with {len(entries)} skills")


if __name__ == "__main__":
    main()
