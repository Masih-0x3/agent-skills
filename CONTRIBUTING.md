# Contributing

## Adding or updating a skill

1. Create or update `skills/<skill-name>/` with a valid `SKILL.md` frontmatter containing only `name` and `description`.
2. Keep packages self-contained: schemas, scripts, references, examples, assets, and tests as needed.
3. Record immutable source provenance and compatibility in `catalog/sources.lock.json`.
4. Store host-specific metadata in `catalog/frontmatter-extensions.json`, not `SKILL.md`.
5. Run `python3 scripts/build_catalog.py` to update both generated catalogs.
6. Run `./scripts/validate-all.sh` or `scripts/validate-all.ps1`.
7. Run `python3 scripts/assert_repository_target.py` before publishing.

## Quality bar

- Descriptions are trigger-oriented and explain when the skill should load.
- Scripts are dependency-light; repository tooling uses the Python standard library.
- Examples validate against schemas when schemas exist.
- No secrets, private keys, databases, caches, or generated runtime state are committed.
- Folder names exactly match declared skill names.
- Blocked packages are neither installed nor exported by default.
- Large outputs are written to files, not chat.

Update a package `CHANGELOG.md` when one exists. Version, author, license, host tags, and invocation hints belong in the extension catalog or source lock.
