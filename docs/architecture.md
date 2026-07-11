# Architecture of this skill library

## Monorepo model

Each skill is an **atomic package**:

```text
skills/<name>/
  SKILL.md          # operating contract + frontmatter
  README.md         # optional human install notes
  schemas/          # JSON Schema contracts
  scripts/          # deterministic validators / helpers
  references/       # long-form method docs
  examples/         # golden fixtures
  tests/            # executable checks
  templates/        # invocation / report templates
```

The monorepo root holds shared docs, catalog, and install helpers only.

## Two-skill control plane

```text
┌──────────────────────────┐
│ project-task-decomposer  │  planning plane
│  PRD → task corpus       │
└────────────┬─────────────┘
             │ JSONL corpus + manifest + waves
             ▼
┌──────────────────────────┐
│ software-orchestrator    │  execution plane
│  route / review / integrate / learn │
└────────────┬─────────────┘
             │
             ▼
      worker agents (Cline, Kilo, agy, …)
```

## Data boundaries

| Artifact | Owner skill | Consumer |
|----------|-------------|----------|
| `.orchestrator/plans/...` corpus | decomposer | orchestrator |
| Routing metadata on tasks | decomposer | orchestrator router |
| Model capability DB | orchestrator | orchestrator only |
| Implementation code | workers | orchestrator review |

## Why not one mega-skill

Separation keeps planning pure (no implementation pressure) and execution accountable (no silent re-planning of thousands of tasks mid-flight without CORPUS_UPDATE).
