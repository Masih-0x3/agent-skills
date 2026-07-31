#!/usr/bin/env python3
"""Shared, dependency-free helpers for the portable skill repository."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CATALOG = ROOT / "catalog" / "skills.json"
INTEGRITY = ROOT / "catalog" / "integrity.json"
SOURCE_LOCK = ROOT / "catalog" / "sources.lock.json"
EXTENSIONS = ROOT / "catalog" / "frontmatter-extensions.json"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOP_LEVEL_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$")
IGNORED_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".db", ".db-journal", ".db-wal", ".db-shm"}
EXECUTABLE_SUFFIXES = {".bat", ".cmd", ".exe", ".js", ".mjs", ".ps1", ".py", ".sh", ".ts"}
SECRET_PATTERNS = {
    "aws_access_key": re.compile(rb"(?:AKIA|ASIA)[0-9A-Z]{16}"),
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    "openai_key": re.compile(rb"sk-[A-Za-z0-9]{20,}"),
    "private_key": re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
}
LOVABLE_LIMITS = {
    "max_files": 200,
    "max_total_bytes": 10 * 1024 * 1024,
    "max_file_bytes": 1024 * 1024,
    "max_skill_characters": 100_000,
}


def _git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=not binary,
    )
    return result.stdout


def normalized_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts) or any(
        path.name.endswith(suffix) for suffix in IGNORED_SUFFIXES
    )


def skill_names() -> list[str]:
    names = {
        path.parent.name
        for path in SKILLS.glob("*/SKILL.md")
        if path.is_file()
    }
    try:
        tracked = str(_git("ls-files", "skills/*/SKILL.md"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        tracked = ""
    for value in tracked.splitlines():
        parts = Path(value).parts
        if len(parts) == 3:
            names.add(parts[1])
    return sorted(names)


def skill_file_paths(name: str) -> list[str]:
    prefix = f"skills/{name}/"
    paths: set[str] = set()
    try:
        raw = _git("ls-files", "-z", "--", f"skills/{name}", binary=True)
        assert isinstance(raw, bytes)
        paths.update(item.decode("utf-8") for item in raw.split(b"\0") if item)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    directory = SKILLS / name
    if directory.exists():
        paths.update(normalized_relative(path) for path in directory.rglob("*") if path.is_file())
    return sorted(path for path in paths if path.startswith(prefix) and not ignored(Path(path)))


def read_repo_file(relative_path: str) -> bytes:
    path = ROOT / Path(relative_path)
    if path.is_file() and not path.is_symlink():
        value = path.read_bytes()
    else:
        try:
            value = _git("show", f":{relative_path}", binary=True)
        except subprocess.CalledProcessError as exc:
            raise FileNotFoundError(relative_path) from exc
        assert isinstance(value, bytes)
    if b"\0" not in value:
        try:
            value.decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            value = value.replace(b"\r\n", b"\n")
    return value


def frontmatter_blocks(text: str) -> tuple[dict[str, list[str]], str]:
    if text.startswith("\ufeff"):
        text = text[1:]
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        raise ValueError("missing YAML frontmatter")
    lines = match.group(1).replace("\r\n", "\n").split("\n")
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        top = TOP_LEVEL_RE.match(line) if line and not line[0].isspace() else None
        if top:
            current = top.group(1)
            if current in blocks:
                raise ValueError(f"duplicate frontmatter field: {current}")
            blocks[current] = [line]
        elif current is not None:
            blocks[current].append(line)
        elif line.strip():
            raise ValueError(f"invalid frontmatter line: {line}")
    return blocks, text[match.end():]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return str(json.loads(value))
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def block_value(lines: list[str]) -> str:
    _, raw = lines[0].split(":", 1)
    raw = raw.strip()
    if not raw.startswith(("|", ">")):
        return _unquote(raw)
    continuation = lines[1:]
    nonblank = [len(line) - len(line.lstrip()) for line in continuation if line.strip()]
    indent = min(nonblank) if nonblank else 0
    content = [line[indent:] if line.strip() else "" for line in continuation]
    if raw.startswith("|"):
        return "\n".join(content).strip()
    paragraphs: list[str] = []
    paragraph: list[str] = []
    for line in content:
        if line:
            paragraph.append(line.strip())
        elif paragraph:
            paragraphs.append(" ".join(paragraph))
            paragraph = []
    if paragraph:
        paragraphs.append(" ".join(paragraph))
    return "\n\n".join(paragraphs).strip()


def parse_skill(name: str) -> tuple[dict[str, list[str]], str, str]:
    text = read_repo_file(f"skills/{name}/SKILL.md").decode("utf-8")
    blocks, _ = frontmatter_blocks(text)
    if "name" not in blocks or "description" not in blocks:
        raise ValueError("frontmatter requires name and description")
    return blocks, block_value(blocks["name"]), block_value(blocks["description"])


def load_source_lock() -> dict[str, Any]:
    return json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def commit_paths(commit: str) -> frozenset[str]:
    return frozenset(str(_git("ls-tree", "-r", "--name-only", commit)).splitlines())


def source_for(name: str, lock: dict[str, Any]) -> dict[str, str]:
    for source in lock["sources"]:
        explicit = source.get("skills", {})
        if name in explicit:
            return {
                "id": source["id"],
                "repository": source["repository"],
                "commit": source["commit"],
                "path": explicit[name],
                "license": source["license"],
            }
    baseline = next(source for source in lock["sources"] if source["id"] == "agent-skills-baseline")
    source_path = baseline.get("path_overrides", {}).get(name, baseline["path_template"].format(name=name))
    if f"{source_path}/SKILL.md" not in commit_paths(baseline["commit"]):
        raise ValueError(
            f"skill {name!r} is absent from the baseline commit; add an explicit immutable source mapping"
        )
    return {
        "id": baseline["id"],
        "repository": baseline["repository"],
        "commit": baseline["commit"],
        "path": source_path,
        "license": baseline["license"],
    }


def integrity_for(name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    files: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for repo_path in skill_file_paths(name):
        data = read_repo_file(repo_path)
        relative = repo_path.removeprefix(f"skills/{name}/")
        sha256 = hashlib.sha256(data).hexdigest()
        files.append({"path": relative, "sha256": sha256, "bytes": len(data)})
        digest.update(relative.encode("utf-8") + b"\0" + sha256.encode("ascii") + b"\0")
    summary = {
        "algorithm": "sha256",
        "tree_sha256": digest.hexdigest(),
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "largest_file_bytes": max((item["bytes"] for item in files), default=0),
    }
    return summary, files


def build_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    lock = load_source_lock()
    extension_data = json.loads(EXTENSIONS.read_text(encoding="utf-8")) if EXTENSIONS.is_file() else {"skills": {}}
    entries: list[dict[str, Any]] = []
    integrity_entries: list[dict[str, Any]] = []
    for name in skill_names():
        blocks, declared_name, description = parse_skill(name)
        summary, files = integrity_for(name)
        policy = lock.get("compatibility", {}).get(name, {})
        lovable = (
            summary["file_count"] <= LOVABLE_LIMITS["max_files"]
            and summary["total_bytes"] <= LOVABLE_LIMITS["max_total_bytes"]
            and summary["largest_file_bytes"] <= LOVABLE_LIMITS["max_file_bytes"]
            and len(read_repo_file(f"skills/{name}/SKILL.md").decode("utf-8"))
            <= LOVABLE_LIMITS["max_skill_characters"]
        )
        if policy.get("lovable_compatible") is False:
            lovable = False
        normalizations = list(lock.get("normalizations", {}).get(name, []))
        if name in extension_data.get("skills", {}):
            note = "Moved non-portable top-level frontmatter fields into catalog/frontmatter-extensions.json."
            if note not in normalizations:
                normalizations.append(note)
        entries.append({
            "id": name,
            "name": declared_name,
            "description": description,
            "path": f"skills/{name}",
            "entrypoint": f"skills/{name}/SKILL.md",
            "source": source_for(name, lock),
            "normalizations": normalizations,
            "review": {
                "status": policy.get("review_status", "reviewed" if name in lock.get("normalizations", {}) else "unreviewed"),
                "has_executable_content": any(Path(item["path"]).suffix.lower() in EXECUTABLE_SUFFIXES for item in files),
            },
            "integrity": summary,
            "compatibility": {
                "agent_skills": set(blocks) == {"name", "description"},
                "installable": policy.get("installable", True),
                "lovable": lovable,
                "reason": policy.get("reason", ""),
            },
        })
        integrity_entries.append({"name": name, "tree_sha256": summary["tree_sha256"], "files": files})
    catalog = {
        "schema_version": 3,
        "repository": "https://github.com/Masih-0x3/agent-skills",
        "repository_visibility": "private",
        "description": "Canonical portable snapshot of personal and approved third-party skills.",
        "lovable_import": "Use deterministic ZIP upload while the repository remains private.",
        "limits": {"lovable": LOVABLE_LIMITS},
        "skill_count": len(entries),
        "skills": entries,
    }
    integrity = {"schema_version": 1, "algorithm": "sha256", "skill_count": len(entries), "skills": integrity_entries}
    return catalog, integrity


def json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"
