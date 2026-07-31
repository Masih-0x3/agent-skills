#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

"$PY" "$ROOT/scripts/validate_skills.py"
"$PY" "$ROOT/scripts/build_catalog.py" --check

ORCH="$ROOT/skills/software-orchestrator"
"$PY" -m py_compile \
  "$ORCH/scripts/initialize_store.py" \
  "$ORCH/scripts/seed_model_priors.py" \
  "$ORCH/scripts/select_model.py" \
  "$ORCH/scripts/record_outcome.py"
"$PY" "$ORCH/scripts/initialize_store.py" --path "$TMP_ROOT/orchestrator.db"
"$PY" "$ORCH/scripts/seed_model_priors.py" --db "$TMP_ROOT/orchestrator.db" --force

PTD="$ROOT/skills/project-task-decomposer"
CORPUS="$PTD/examples/example-corpus"
"$PY" "$PTD/scripts/validate_task_corpus.py" "$CORPUS" --json >"$TMP_ROOT/ptd-validate.json"
"$PY" "$PTD/scripts/detect_cycles.py" "$CORPUS"
"$PY" "$PTD/scripts/check_readiness.py" "$CORPUS" >"$TMP_ROOT/ptd-ready.json"
"$PY" "$ROOT/scripts/run_decomposer_tests.py"

echo "ALL VALIDATION PASSED"
