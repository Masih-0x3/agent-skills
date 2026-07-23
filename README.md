# Agent Skills

Personal, production-oriented **agent skills** for Grok Build, Hermes, Codex/Agents, and compatible CLIs.

This repository is a **skill monorepo**: each skill is a self-contained package under `skills/` with its own `SKILL.md`, schemas, scripts, references, examples, and tests.

## Skills

This private repository is the portable source of truth for 152 skills: the owner's personal skills, approved third-party snapshots, and the two original orchestration packages. The complete machine-readable inventory is [`catalog/skills.json`](catalog/skills.json).

It deliberately excludes Codex's bundled `.system` skills and plugin-cache skills. Install or update those through Codex on each machine; copying them here would make the repository stale and platform-dependent.

## Recommended pipeline

```text
PRD / handoff / plan
        │
        ▼
 project-task-decomposer
        │  .orchestrator/plans/<slug>/<version>/
        ▼
 software-orchestrator   (/goal style, run to completion)
        │
        ▼
 integrated software + outcome learning
```

## Install

### Sync the full library (recommended)

Clone this private repository on a machine, then run the native sync command. It copies every package to both global discovery roots and does not remove unrelated local skills.

```powershell
git clone https://github.com/Masih-0x3/agent-skills.git $HOME\agent-skills
cd $HOME\agent-skills
.\scripts\sync-skills.ps1
```

On macOS or Linux:

```bash
git clone https://github.com/Masih-0x3/agent-skills.git ~/agent-skills
cd ~/agent-skills
./scripts/sync-skills.sh
```

Use `--target agents` / `--target codex` in Bash or `-Target Agents` / `-Target Codex` in PowerShell to install to only one location. Restart Codex or open a new session afterwards.

### One skill (legacy helper)

```bash
# Grok Build
mkdir -p ~/.grok/skills
cp -R skills/software-orchestrator ~/.grok/skills/
cp -R skills/project-task-decomposer ~/.grok/skills/

# Hermes
mkdir -p ~/.hermes/skills/software-development
cp -R skills/software-orchestrator ~/.hermes/skills/software-development/
cp -R skills/project-task-decomposer ~/.hermes/skills/software-development/

# Codex / Agents global
mkdir -p ~/.agents/skills
cp -R skills/software-orchestrator ~/.agents/skills/
cp -R skills/project-task-decomposer ~/.agents/skills/
```

### Helper script

```bash
./scripts/install-skill.sh software-orchestrator --target all
./scripts/install-skill.sh project-task-decomposer --target all
```

### Project-local

```bash
mkdir -p .grok/skills .agents/skills
cp -R skills/software-orchestrator .grok/skills/
cp -R skills/project-task-decomposer .grok/skills/
```

See [docs/install.md](docs/install.md).

## Invoke

```text
/project-task-decomposer
Analyze @docs/product-handoff.md in PRD_PLUS_REPO mode.
Plan version: 1.0.0

/software-orchestrator
Invoke Software Orchestrator on .orchestrator/plans/<slug>/1.0.0/
# or attach a plan document and run goal-mode to completion
```

## Repository layout

```text
agent-skills/
  README.md
  AGENTS.md
  LICENSE
  CONTRIBUTING.md
  catalog/skills.json
  docs/
    install.md
    architecture.md
  scripts/
    install-skill.sh
    validate-all.sh
  skills/
    software-orchestrator/     # full package (schemas, scripts, priors, …)
    project-task-decomposer/   # full package (schemas, scripts, example corpus, tests, …)
```

## Validate

```bash
./scripts/validate-all.sh
```

When adding, removing, or renaming a skill, regenerate the inventory:

```bash
python3 scripts/build_catalog.py
```

## Design principles

1. **Operational over aspirational** — schemas, scripts, and examples that actually run  
2. **Orchestration boundary** — decomposer plans; orchestrator executes; workers implement  
3. **No permanent model hardcoding** — capability tags + learning store  
4. **Large corpora stay on disk** — JSONL shards, never one giant chat dump  
5. **Goal-mode** — attached documents run to completion unless hard-blocked  
6. **Portable skills** — SKILL.md + assets, no proprietary runtime required  

## License

MIT — see [LICENSE](LICENSE).

## Authorship notes

- **project-task-decomposer** original design: repository owner; revised/audited for production packaging.  
- **software-orchestrator**: design + implementation package for multi-model software delivery orchestration.
