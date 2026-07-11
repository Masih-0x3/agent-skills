# Install guide

## Targets

| Target | Path |
|--------|------|
| Grok Build (user) | `~/.grok/skills/<name>/` |
| Hermes (user) | `~/.hermes/skills/software-development/<name>/` |
| Agents / Codex global | `~/.agents/skills/<name>/` |
| Project Grok | `./.grok/skills/<name>/` |
| Project Agents | `./.agents/skills/<name>/` |

## Install helper

```bash
./scripts/install-skill.sh software-orchestrator --target all
./scripts/install-skill.sh project-task-decomposer --target all
```

Targets: `grok` | `hermes` | `agents` | `all`

## Post-install: software-orchestrator store

```bash
cd ~/.grok/skills/software-orchestrator   # or chosen install path
python scripts/initialize_store.py --path store/orchestrator.db
python scripts/seed_model_priors.py --db store/orchestrator.db --force
```

## Verify

```bash
# Grok
# grok inspect   # if available

# Hermes
hermes skills list | grep -E 'software-orchestrator|project-task-decomposer'

# Files
ls ~/.agents/skills/software-orchestrator/SKILL.md
ls ~/.agents/skills/project-task-decomposer/SKILL.md
```

## npx skills add

If using the Skills CLI against this monorepo:

```bash
# Example patterns (CLI versions differ):
# npx skills add Masih-0x3/agent-skills --skill software-orchestrator
# or clone and copy as above
```

Prefer explicit copy/`install-skill.sh` when the CLI multi-skill layout differs.
