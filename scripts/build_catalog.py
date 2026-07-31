#!/usr/bin/env python3
"""Generate deterministic catalogs for the portable skill packages."""

from __future__ import annotations

import argparse

from skilllib import CATALOG, INTEGRITY, build_documents, json_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated catalogs are stale")
    args = parser.parse_args()
    catalog, integrity = build_documents()
    expected = {CATALOG: json_text(catalog), INTEGRITY: json_text(integrity)}
    if args.check:
        stale = [path for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"STALE {path}")
            return 1
        print(f"Catalogs are current for {catalog['skill_count']} skills")
        return 0
    for path, content in expected.items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {path} with {catalog['skill_count']} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
