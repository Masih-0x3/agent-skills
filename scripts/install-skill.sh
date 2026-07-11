#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"
TARGET="all"

if [[ -z "$NAME" || "$NAME" == "-h" || "$NAME" == "--help" ]]; then
  echo "Usage: $0 <skill-name> [--target grok|hermes|agents|all]"
  echo "Available:"
  ls -1 "$ROOT/skills"
  exit 0
fi

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

SRC="$ROOT/skills/$NAME"
if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "ERROR: skill not found: $SRC"
  exit 1
fi

install_one() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  rsync -a --delete \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '*.db' \
    --exclude '*.db-*' \
    "$SRC/" "$dest/"
  echo "Installed $NAME → $dest"
}

case "$TARGET" in
  grok)
    install_one "${HOME}/.grok/skills/${NAME}"
    ;;
  hermes)
    install_one "${HOME}/.hermes/skills/software-development/${NAME}"
    if [[ -n "${HERMES_HOME:-}" ]]; then
      install_one "${HERMES_HOME}/skills/software-development/${NAME}"
    fi
    ;;
  agents)
    install_one "${HOME}/.agents/skills/${NAME}"
    ;;
  all)
    install_one "${HOME}/.grok/skills/${NAME}"
    install_one "${HOME}/.hermes/skills/software-development/${NAME}"
    install_one "${HOME}/.agents/skills/${NAME}"
    if [[ -n "${HERMES_HOME:-}" && "${HERMES_HOME}" != "${HOME}/.hermes" ]]; then
      install_one "${HERMES_HOME}/skills/software-development/${NAME}"
    fi
    ;;
  *)
    echo "Unknown target: $TARGET"
    exit 1
    ;;
esac
