# Contributing

## Adding a skill

1. Create `skills/<skill-name>/` with a valid `SKILL.md` frontmatter (`name`, `description`).
2. Keep packages self-contained: schemas, scripts, references, examples, tests as needed.
3. Update `catalog/skills.json` (or re-run catalog generation).
4. Add a row to the README skills table.
5. Ensure `./scripts/validate-all.sh` passes.

## Skill quality bar

- Description is trigger-oriented (when to load), not marketing.
- Non-goals are explicit.
- Scripts are dependency-light when possible (stdlib preferred).
- Examples validate against schemas.
- No secrets in the repo.
- Large outputs write to files, not chat.

## Versioning

Bump the skill’s own `version` in `SKILL.md` and note changes in that skill’s `CHANGELOG.md` when present.
