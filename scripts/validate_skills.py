#!/usr/bin/env python3
"""Validate portable skill contracts, integrity, and repository safety."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from skilllib import (
    CATALOG,
    EXTENSIONS,
    INTEGRITY,
    NAME_RE,
    ROOT,
    SECRET_PATTERNS,
    SOURCE_LOCK,
    build_documents,
    json_text,
    parse_skill,
    read_repo_file,
    skill_file_paths,
    skill_names,
)


def main() -> int:
    errors: list[str] = []
    names = skill_names()
    declared: set[str] = set()
    for name in names:
        try:
            blocks, declared_name, description = parse_skill(name)
        except (UnicodeDecodeError, ValueError, FileNotFoundError) as exc:
            errors.append(f"{name}: {exc}")
            continue
        if not NAME_RE.fullmatch(name) or len(name) > 64:
            errors.append(f"{name}: invalid directory name")
        if declared_name != name:
            errors.append(f"{name}: declares name {declared_name!r}")
        if declared_name in declared:
            errors.append(f"{name}: duplicate declared name")
        declared.add(declared_name)
        if not description.strip():
            errors.append(f"{name}: empty description")
        extra = sorted(set(blocks) - {"name", "description"})
        if extra:
            errors.append(f"{name}: non-portable frontmatter fields: {', '.join(extra)}")
        for relative in skill_file_paths(name):
            path = Path(relative)
            if (ROOT / path).is_symlink():
                errors.append(f"{relative}: symbolic links are not portable")
            lower = path.name.lower()
            if lower.endswith((".pem", ".p12", ".pfx", ".jks", ".keystore", ".key")) or lower in {"id_rsa", "id_ed25519"}:
                errors.append(f"{relative}: private-key-like file is forbidden")
            data = read_repo_file(relative)
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(data):
                    errors.append(f"{relative}: secret-like content ({label})")
    for required in (SOURCE_LOCK, EXTENSIONS):
        try:
            json.loads(required.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{required.relative_to(ROOT)}: {exc}")
    try:
        catalog, integrity = build_documents()
        for path, expected in ((CATALOG, json_text(catalog)), (INTEGRITY, json_text(integrity))):
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                errors.append(f"{path.relative_to(ROOT)}: generated file is stale")
    except Exception as exc:  # validation must aggregate generation failures
        errors.append(f"catalog generation failed: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"FAILED with {len(errors)} error(s)")
        return 1
    print(f"Validated {len(names)} portable skills; catalogs and safety checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
