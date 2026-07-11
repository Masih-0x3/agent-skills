#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
fail=0

echo "== frontmatter =="
for skill in "$ROOT"/skills/*/SKILL.md; do
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  $PY - <<PY || fail=1
import re, pathlib
p = pathlib.Path("$skill")
t = p.read_text()
assert t.startswith("---"), p
m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
assert m, p
body = m.group(1)
assert "name:" in body and "description:" in body, p
print("OK", "$name", "chars", len(t))
PY
done

echo "== software-orchestrator scripts =="
ORCH="$ROOT/skills/software-orchestrator"
$PY -m py_compile \
  "$ORCH/scripts/initialize_store.py" \
  "$ORCH/scripts/seed_model_priors.py" \
  "$ORCH/scripts/select_model.py" \
  "$ORCH/scripts/record_outcome.py"
rm -f /tmp/agent-skills-orch.db
$PY "$ORCH/scripts/initialize_store.py" --path /tmp/agent-skills-orch.db
$PY "$ORCH/scripts/seed_model_priors.py" --db /tmp/agent-skills-orch.db --force
$PY -c "import json; json.load(open('$ORCH/references/model-registry.seed.json'))"
echo "OK software-orchestrator"

echo "== project-task-decomposer =="
PTD="$ROOT/skills/project-task-decomposer"
CORPUS="$PTD/examples/example-corpus"
$PY "$PTD/scripts/validate_task_corpus.py" "$CORPUS" --json >/tmp/ptd-validate.json
$PY -c "import json; d=json.load(open('/tmp/ptd-validate.json')); assert d['status']=='PASS', d"
$PY "$PTD/scripts/detect_cycles.py" "$CORPUS"
$PY "$PTD/scripts/check_readiness.py" "$CORPUS" --write >/tmp/ptd-ready.out

$PY - <<PY
import importlib.util, sys, traceback
from pathlib import Path
root = Path(r"$PTD")
failed = 0
count = 0
for t in sorted((root / "tests").glob("test_*.py")):
    count += 1
    spec = importlib.util.spec_from_file_location(t.stem, t)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        for name in dir(mod):
            if name.startswith("test_"):
                getattr(mod, name)()
        print("OK", t.name)
    except Exception:
        failed += 1
        traceback.print_exc()
if count == 0:
    raise SystemExit("no tests found")
sys.exit(1 if failed else 0)
PY
echo "OK project-task-decomposer"

echo "== catalog =="
$PY -c "import json; d=json.load(open('$ROOT/catalog/skills.json')); assert len(d['skills'])>=2; print('skills', [s['id'] for s in d['skills']])"

if [[ $fail -ne 0 ]]; then
  echo "FAILED"
  exit 1
fi
echo "ALL VALIDATION PASSED"
