# Agent Skills

Personal, production-oriented **agent skills** for Grok Build, Hermes, Codex/Agents, and compatible CLIs.

This repository is a **skill monorepo**: each skill is a self-contained package under `skills/` with its own `SKILL.md`, schemas, scripts, references, examples, and tests.

## Skills

| Skill | Version | Purpose |
|-------|---------|---------|
| [`software-orchestrator`](skills/software-orchestrator/) | 0.3.0 | Goal-mode multi-agent software orchestration: plan → route → dispatch → validate → review → integrate → learn. Model-agnostic routing with host capability priors. |
| [`project-task-decomposer`](skills/project-task-decomposer/) | 1.1.0 | Turn a PRD / handoff / plan into a versioned, sharded, dependency-aware **task corpus** for the Software Orchestrator. Does not implement code or assign models. |

Machine-readable catalog: [`catalog/skills.json`](catalog/skills.json)

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

### One skill (global)

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
