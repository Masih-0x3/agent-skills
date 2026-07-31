#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"
if [[ -z "$NAME" || "$NAME" == "-h" || "$NAME" == "--help" ]]; then
  echo "Usage: $0 <skill-name> [--target agents|codex|claude|grok|hermes|cursor|copilot|custom] [--destination PATH] [--dry-run]"
  exit 0
fi
shift
exec "${PYTHON:-python3}" "$ROOT/scripts/install_skills.py" "$NAME" "$@"
