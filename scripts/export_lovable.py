#!/usr/bin/env python3
"""Create deterministic, integrity-verifiable per-skill ZIPs for Lovable."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from skilllib import ROOT, build_documents, json_text, read_repo_file

ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skills", nargs="*", help="skill names; defaults to every Lovable-compatible skill")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "lovable")
    parser.add_argument("--check", action="store_true", help="build and re-read each ZIP to verify integrity")
    args = parser.parse_args()
    catalog, integrity = build_documents()
    by_name = {item["name"]: item for item in catalog["skills"]}
    hashes = {item["name"]: item for item in integrity["skills"]}
    selected = args.skills or [name for name, item in by_name.items() if item["compatibility"]["lovable"]]
    unknown = sorted(set(selected) - set(by_name))
    if unknown:
        parser.error(f"unknown skill(s): {', '.join(unknown)}")
    incompatible = [name for name in selected if not by_name[name]["compatibility"]["lovable"]]
    if incompatible:
        parser.error(f"not Lovable-compatible: {', '.join(incompatible)}")
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    for name in selected:
        zip_path = output / f"{name}.zip"
        manifest = hashes[name]
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for file in manifest["files"]:
                data = read_repo_file(f"skills/{name}/{file['path']}")
                info = zipfile.ZipInfo(f"{name}/{file['path']}", ZIP_TIME)
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data, compresslevel=9)
        sidecar = zip_path.with_suffix(".manifest.json")
        sidecar.write_text(json_text(manifest), encoding="utf-8", newline="\n")
        if args.check:
            with zipfile.ZipFile(zip_path) as archive:
                for file in manifest["files"]:
                    data = archive.read(f"{name}/{file['path']}")
                    if hashlib.sha256(data).hexdigest() != file["sha256"]:
                        raise RuntimeError(f"integrity mismatch in {zip_path}: {file['path']}")
        print(f"Exported {name} -> {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
