# Install and import guide

## Full-library sync

Preview before writing:

```powershell
.\scripts\sync-skills.ps1 -Target Both -DryRun
```

```bash
./scripts/sync-skills.sh --target both --dry-run
```

Apply after reviewing the destination list:

```powershell
.\scripts\sync-skills.ps1 -Target Both
```

```bash
./scripts/sync-skills.sh --target both
```

`both` targets the per-user Agents and Codex roots. `all` targets the global Agents, Codex, Claude, Grok, and Hermes roots; it deliberately does not write into the current project's Cursor or Copilot folders.

## One skill or a custom destination

```bash
./scripts/install-skill.sh software-orchestrator --target codex --dry-run
./scripts/install-skill.sh software-orchestrator --target codex
python3 scripts/install_skills.py playwright --target custom --destination /path/to/tool/skills
```

For project-local Cursor or Copilot discovery, run from the intended project:

```bash
python3 /path/to/agent-skills/scripts/install_skills.py playwright --target cursor
python3 /path/to/agent-skills/scripts/install_skills.py playwright --target copilot
```

The installer never removes unrelated skills. A same-named package is copied to a staging directory, validated, moved into place, and rolled back if replacement fails.

## Blocked packages

Compatibility policy is stored in `catalog/sources.lock.json`. `pentest-tools` is skipped by default because Windows Defender blocks one reference file. Do not bypass endpoint protection. Review the package in an isolated environment before using `--include-blocked`.

## Lovable

Direct GitHub URL import is unavailable while this repository is private. Export and upload one deterministic ZIP:

```bash
python3 scripts/export_lovable.py playwright --output dist/lovable --check
```

The exporter writes `playwright.zip` and `playwright.manifest.json`. It rejects blocked or over-limit packages before writing.

## Verification after installation

Check representative entrypoints and restart the coding tool or open a new session:

```powershell
Test-Path "$env:USERPROFILE\.agents\skills\playwright\SKILL.md"
Test-Path "$env:USERPROFILE\.codex\skills\supabase\SKILL.md"
```

Run `scripts/build_catalog.py --check` in the repository to verify all committed hashes and generated catalogs.
