#!/usr/bin/env python3
"""Create deterministic, integrity-verifiable per-skill ZIPs for Lovable."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from skilllib import ROOT, build_documents, json_text, read_repo_file

ZIP_TIME = (1980, 1, 1, 0, 0, 0)
PROFILE_ROOT = ROOT / "catalog"
PROFILE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def profile_path(profile_name: str) -> Path:
    """Return a profile path only after validating its safe identifier."""
    if not PROFILE_NAME_RE.fullmatch(profile_name):
        raise ValueError(f"invalid profile name {profile_name!r}")
    root = PROFILE_ROOT.resolve()
    candidate = (PROFILE_ROOT / f"lovable-{profile_name}.json").resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"invalid profile name {profile_name!r}") from exc
    return candidate


def load_profile(profile_name: str) -> dict:
    """Load a checked-in export profile by its stable CLI name."""
    path = profile_path(profile_name)
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unknown or invalid Lovable profile {profile_name!r}") from exc
    if profile.get("schema_version") != 1 or profile.get("id") != profile_name:
        raise ValueError(f"invalid Lovable profile metadata for {profile_name!r}")
    skills = profile.get("skills")
    if not isinstance(skills, list) or not skills or any(not isinstance(name, str) for name in skills):
        raise ValueError(f"profile {profile_name!r} must contain a non-empty skills list")
    if len(set(skills)) != len(skills):
        raise ValueError(f"profile {profile_name!r} contains duplicate skills")
    return profile


def build_index(profile: str | None, selected: list[str], by_name: dict, hashes: dict) -> dict:
    """Return the deterministic, machine-readable export index."""
    return {
        "schema_version": 1,
        "profile": profile,
        "repository_visibility": "private",
        "import": "In Lovable, open Settings -> Skills -> Add -> Upload ZIP, then upload each individual skill ZIP; private GitHub repositories are not directly importable.",
        "skill_count": len(selected),
        "skills": [
            {
                "name": name,
                "description": by_name[name]["description"],
                "zip": f"{name}.zip",
                "manifest": f"{name}.manifest.json",
                "zip_sha256": hashes[name]["zip_sha256"],
                "tree_sha256": hashes[name]["tree_sha256"],
                "file_count": len(hashes[name]["files"]),
                "total_bytes": sum(file["bytes"] for file in hashes[name]["files"]),
            }
            for name in sorted(selected)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skills", nargs="*", help="skill names; defaults to every Lovable-compatible skill")
    parser.add_argument("--profile", help="curated export profile (currently: general-use)")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "lovable")
    parser.add_argument("--check", action="store_true", help="build and re-read each ZIP to verify integrity")
    args = parser.parse_args()
    if args.profile and args.skills:
        parser.error("--profile cannot be combined with explicit skill names")
    catalog, integrity = build_documents()
    by_name = {item["name"]: item for item in catalog["skills"]}
    hashes = {item["name"]: item for item in integrity["skills"]}
    profile = None
    if args.profile:
        try:
            profile_data = load_profile(args.profile)
        except ValueError as exc:
            parser.error(str(exc))
        profile = args.profile
        selected = profile_data["skills"]
    else:
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
        zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        # Store the digest for the index after the archive is finalized.
        hashes[name]["zip_sha256"] = zip_digest
        print(f"Exported {name} -> {zip_path}")
    index_path = output / "index.json"
    index_path.write_text(json_text(build_index(profile, selected, by_name, hashes)), encoding="utf-8", newline="\n")
    print(f"Wrote export index -> {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
