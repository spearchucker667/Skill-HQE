#!/usr/bin/env bash
# Skill-HQE invariant verification script.
#
# Purpose:
#   Run the canonical repository integrity checks in a single command so that
#   local development and optional CI stages can verify the skill quickly.
#
# Checks performed:
#   - scripts/check_skill.py        structure, links, schema, and syntax
#   - scripts/validate_protocol_bundle.py  protocol/schema consistency
#   - scripts/scan_secrets.py       high-confidence secret scan
#
# Usage:
#   scripts/verify_invariants.sh [REPO_ROOT]
#
# Exit codes:
#   0  all checks passed
#   1  one or more checks failed

set -euo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
cd "$ROOT"

fail=0

run_check() {
  local name="$1"
  shift
  echo
  echo "[verify_invariants] Running: $name"
  if "$@"; then
    echo "[verify_invariants] $name: OK"
  else
    echo "[verify_invariants] $name: FAILED" >&2
    fail=1
  fi
}

run_check "Skill structure & link check" \
  python3 scripts/check_skill.py .

run_check "Protocol bundle validation" \
  python3 scripts/validate_protocol_bundle.py --strict-schema-metadata

run_check "Secret scan" \
  python3 scripts/scan_secrets.py . --allowlist .secretscanignore

echo
if [[ "$fail" -ne 0 ]]; then
  echo "[verify_invariants] FAILED" >&2
  exit 1
fi

echo "[verify_invariants] OK"
