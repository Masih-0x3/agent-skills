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

Compatibility policy is stored in `catalog/sources.lock.json`. `pentest-tools` is non-installable because Windows Defender blocks one reference file. The installer has no runtime bypass for blocked packages; an isolated security review and an explicit source-lock status change are required first.

## Lovable

Direct GitHub URL import is unavailable while this repository is private. Export the curated general-use profile:

```bash
python3 scripts/export_lovable.py --profile general-use --output dist/lovable --check
```

The exporter writes one `<skill>.zip` and `<skill>.manifest.json` per selected skill, plus `dist/lovable/index.json`. The index is the machine-readable import list with descriptions, ZIP names, file counts, and SHA-256 tree hashes.

In Lovable, open the target project and go to `Settings -> Skills -> Add -> Upload ZIP`. Upload each individual skill ZIP. Keep the ZIP's wrapping `<skill>/` directory. Do not upload `index.json` or sidecar manifests as skills. Verify the skill appears in the project's enabled skills after each upload.

For GitHub Actions, open the successful `validate-skills` workflow run, download the `lovable-general-use` artifact, unzip the bundle locally, then upload each individual skill ZIP through `Settings -> Skills -> Add -> Upload ZIP`.

The profile excludes desktop/browser operators, Orca/Paseo/provider routing, MCP or named CLI dependencies, cloud administration, remote sandboxes, security offense/reverse engineering, private project workflows, publishing, and required live research. It never includes `computer-use` or `pentest-tools`. See [`catalog/lovable-general-use.json`](../catalog/lovable-general-use.json) for the stable allowlist and exclusion reasons.

For one compatible package outside the profile, explicit export remains supported:

```bash
python3 scripts/export_lovable.py playwright --output dist/lovable --check
```

## Verification after installation

Check representative entrypoints and restart the coding tool or open a new session:

```powershell
Test-Path "$env:USERPROFILE\.agents\skills\playwright\SKILL.md"
Test-Path "$env:USERPROFILE\.codex\skills\supabase\SKILL.md"
```

Run `scripts/build_catalog.py --check` in the repository to verify all committed hashes and generated catalogs.
