# Agent Skills

Private, canonical source of truth for 155 portable agent skills used across Codex, Agents-compatible tools, and other coding assistants.

Each package lives at `skills/<name>/` and has a `SKILL.md` whose only frontmatter fields are `name` and `description`. Source provenance, host-specific extensions, compatibility, and integrity hashes live in `catalog/`.

This repository is **not** mirrored into SkillMap. Publication must target `Masih-0x3/agent-skills` and is guarded by `scripts/assert_repository_target.py`.

## Validate

Windows:

```powershell
py -3 .\scripts\build_catalog.py --check
.\scripts\validate-all.ps1
```

macOS, Linux, Git Bash, or WSL:

```bash
python3 scripts/build_catalog.py --check
./scripts/validate-all.sh
```

The generated catalogs include immutable source commits, package digests, per-file SHA-256 hashes, file sizes, executable-content flags, and import compatibility.

## Install

Preview the default Codex and Agents sync, then apply it:

```powershell
.\scripts\sync-skills.ps1 -Target Both -DryRun
.\scripts\sync-skills.ps1 -Target Both
```

```bash
./scripts/sync-skills.sh --target both --dry-run
./scripts/sync-skills.sh --target both
```

The installer stages and validates each package, atomically replaces only the same-named destination, and preserves unrelated local skills. Packages marked non-installable are always skipped until their review status is resolved in the source lock.

Supported targets:

| Target | Destination |
|---|---|
| `agents` | `~/.agents/skills` |
| `codex` | `~/.codex/skills` |
| `claude` | `~/.claude/skills` |
| `grok` | `~/.grok/skills` |
| `hermes` | `~/.hermes/skills/software-development` |
| `cursor` | `./.cursor/skills` |
| `copilot` | `./.github/skills` |
| `custom` | Explicit `--destination` / `-Destination` |

Install one skill:

```bash
./scripts/install-skill.sh playwright --target agents
python3 scripts/install_skills.py supabase --target custom --destination /path/to/project/.agents/skills
```

See [`docs/install.md`](docs/install.md) for platform-specific examples.

## Lovable ZIP import

The repository remains private, so use deterministic per-skill ZIP upload rather than a public GitHub URL:

```powershell
py -3 .\scripts\export_lovable.py playwright --output .\dist\lovable --check
```

Each ZIP contains one wrapping skill directory. A sidecar manifest records every file hash and the package tree digest. Export fails closed when a package is blocked or exceeds Lovable's documented file-count, file-size, total-size, or `SKILL.md` size limits.

`cloudflare` remains in the canonical library but exceeds Lovable's 200-file limit. `pentest-tools` remains tracked but is blocked from default installation and export pending review of a Windows Defender-triggered reference.

## Repository layout

```text
agent-skills/
  catalog/
    skills.json                 # searchable package catalog
    integrity.json              # per-file SHA-256 manifest
    sources.lock.json           # immutable sources and compatibility policy
    frontmatter-extensions.json # preserved host-specific metadata
  scripts/
    build_catalog.py
    validate_skills.py
    install_skills.py
    export_lovable.py
    assert_repository_target.py
  skills/<name>/SKILL.md
```

## Publishing guard

Run before every push or PR:

```bash
python3 scripts/assert_repository_target.py
git remote get-url origin
```

The guard accepts GitHub HTTPS or SSH forms only when they resolve to `Masih-0x3/agent-skills`.

## License

Repository tooling is MIT. Vendored skills retain their per-package license and source attribution recorded in the source lock and package files.
