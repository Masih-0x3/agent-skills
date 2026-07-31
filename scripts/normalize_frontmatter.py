#!/usr/bin/env python3
"""Move non-portable top-level frontmatter blocks into a sidecar catalog."""

from __future__ import annotations

import argparse
import json

from skilllib import EXTENSIONS, SKILLS, frontmatter_blocks, json_text

PORTABLE = {"name", "description"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    existing = {"schema_version": 1, "description": "Host-specific fields removed from portable SKILL.md frontmatter.", "skills": {}}
    if EXTENSIONS.is_file():
        existing = json.loads(EXTENSIONS.read_text(encoding="utf-8"))
    changed: list[str] = []
    for skill_file in sorted(SKILLS.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        blocks, body = frontmatter_blocks(text)
        extras = {key: "\n".join(value) for key, value in blocks.items() if key not in PORTABLE}
        if extras:
            existing["skills"].setdefault(skill_file.parent.name, {}).update(extras)
            changed.append(skill_file.parent.name)
            if not args.check:
                frontmatter = ["---", *blocks["name"], *blocks["description"], "---"]
                skill_file.write_text("\n".join(frontmatter) + "\n" + body, encoding="utf-8", newline="\n")
    if args.check:
        if changed:
            print("Non-portable frontmatter remains: " + ", ".join(changed))
            return 1
        print("All SKILL.md frontmatter is portable")
        return 0
    EXTENSIONS.write_text(json_text(existing), encoding="utf-8", newline="\n")
    print(f"Normalized {len(changed)} skill(s); wrote {EXTENSIONS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
