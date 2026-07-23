# AGENTS.md — working in this repository

## Purpose

This monorepo stores **portable agent skills**. Prefer editing skill packages under `skills/` rather than inventing parallel copies elsewhere.

## Rules

1. Do not commit SQLite DBs, secrets, or `__pycache__`.
2. Do not collapse two skills into one package.
3. When changing a skill schema, update examples and validators in the same change.
4. Prefer stdlib Python for validation scripts.
5. Run `python3 scripts/build_catalog.py` after adding, removing, or renaming a skill so `catalog/skills.json` stays in sync.
6. Run `./scripts/validate-all.sh` before claiming a skill is ready.

## Skill contract

Each skill directory must include:

- `SKILL.md` with YAML frontmatter (`name`, `description`)
- Optional: `README.md`, `schemas/`, `scripts/`, `references/`, `examples/`, `tests/`

## Related pipeline

- `project-task-decomposer` produces corpora under `.orchestrator/plans/`
- `software-orchestrator` consumes goal documents / corpora and executes delivery
