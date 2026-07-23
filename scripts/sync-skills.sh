#!/usr/bin/env bash
set -euo pipefail

# Copies the versioned skill snapshot into local discovery folders.
# It deliberately does not delete unrelated local skills or touch bundled/plugin skills.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="both"

usage() {
  cat <<'EOF'
Usage: ./scripts/sync-skills.sh [--target agents|codex|both]
Copies every package under skills/ to the selected user-level skill folders.
Existing packages with the same name are updated; unrelated packages are retained.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:?missing target}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 1 ;;
  esac
done

sync_to() {
  local destination="$1"
  mkdir -p "$destination"
  for source in "$ROOT"/skills/*; do
    [[ -d "$source" ]] || continue
    rsync -a --delete \
      --exclude '__pycache__' --exclude '*.pyc' --exclude '*.db' --exclude '*.db-*' \
      "$source/" "$destination/$(basename "$source")/"
  done
  echo "Synced $(find "$ROOT"/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ') skills -> $destination"
}

case "$TARGET" in
  agents) sync_to "$HOME/.agents/skills" ;;
  codex) sync_to "$HOME/.codex/skills" ;;
  both) sync_to "$HOME/.agents/skills"; sync_to "$HOME/.codex/skills" ;;
  *) echo "Unknown target: $TARGET" >&2; exit 1 ;;
esac
