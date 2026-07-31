# AGENTS.md — working in this repository

## Purpose

This monorepo stores **portable agent skills**. Prefer editing skill packages under `skills/` rather than inventing parallel copies elsewhere.

Canonical GitHub repository: `Masih-0x3/agent-skills`. SkillMap is a separate product repository and must never receive this library. Run `python3 scripts/assert_repository_target.py` before every push.

## Rules

1. Do not commit SQLite DBs, secrets, or `__pycache__`.
2. Do not collapse two skills into one package.
3. When changing a skill schema, update examples and validators in the same change.
4. Prefer stdlib Python for validation scripts.
5. Run `python3 scripts/build_catalog.py` after adding, removing, or renaming a skill so `catalog/skills.json` stays in sync.
6. Run `./scripts/validate-all.sh` before claiming a skill is ready.
7. Keep `SKILL.md` frontmatter limited to `name` and `description`; preserve host-specific fields in `catalog/frontmatter-extensions.json`.
8. Do not restore, install, export, or execute a package marked blocked in `catalog/sources.lock.json` unless its review status is explicitly resolved.
9. Preserve unrelated installed skills. Installers may replace only the same-named destination after staging and validation.

## Skill contract

Each skill directory must include:

- `SKILL.md` with YAML frontmatter (`name`, `description`)
- Optional: `README.md`, `schemas/`, `scripts/`, `references/`, `examples/`, `tests/`

Generated catalogs bind packages to immutable source commits and SHA-256 integrity data. Regenerate them; never hand-edit generated hashes.

## Related pipeline

- `project-task-decomposer` produces corpora under `.orchestrator/plans/`
- `software-orchestrator` consumes goal documents / corpora and executes delivery
