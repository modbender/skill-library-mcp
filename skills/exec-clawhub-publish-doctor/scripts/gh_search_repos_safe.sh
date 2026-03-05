#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  gh_search_repos_safe.sh <query> [limit]

Env overrides:
  GH_FIELDS   comma-separated JSON fields for gh search repos

Examples:
  gh_search_repos_safe.sh "safe-exec skill" 15
  GH_FIELDS="nameWithOwner,url,description" gh_search_repos_safe.sh "clawhub doctor" 10
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

QUERY="$1"
LIMIT="${2:-15}"
FIELDS="${GH_FIELDS:-fullName,url,description,stargazersCount,updatedAt}"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found. Install GitHub CLI first." >&2
  exit 3
fi

# common alias fix for older snippets
FIELDS="${FIELDS//nameWithOwner/fullName}"

run_search() {
  local fields="$1"
  gh search repos "$QUERY" --limit "$LIMIT" --json "$fields"
}

set +e
OUT=$(run_search "$FIELDS" 2>&1)
EC=$?
set -e

if [[ $EC -eq 0 ]]; then
  echo "$OUT"
  exit 0
fi

if ! grep -qi "Unknown JSON field" <<<"$OUT"; then
  echo "$OUT" >&2
  exit $EC
fi

echo "WARN: JSON field mismatch detected. Attempting fallback field set..." >&2

AVAILABLE=$(awk '
  /Available fields:/ {capture=1; next}
  capture && NF==0 {capture=0}
  capture {gsub(/^ +/, "", $0); if ($1 ~ /^[a-zA-Z]/) print $1}
' <<<"$OUT" | tr '\n' ',' | sed 's/,$//')

if [[ -z "$AVAILABLE" ]]; then
  FALLBACK="fullName,url,description,stargazersCount,updatedAt"
else
  declare -a WANT=(fullName url description stargazersCount updatedAt)
  FALLBACK=""
  for f in "${WANT[@]}"; do
    if grep -qE "(^|,)$f(,|$)" <<<"$AVAILABLE"; then
      FALLBACK+="$f,"
    fi
  done
  FALLBACK="${FALLBACK%,}"
  if [[ -z "$FALLBACK" ]]; then
    FALLBACK="$(cut -d',' -f1-5 <<<"$AVAILABLE")"
  fi
fi

set +e
OUT2=$(run_search "$FALLBACK" 2>&1)
EC2=$?
set -e

if [[ $EC2 -eq 0 ]]; then
  echo "INFO: Fallback fields used: $FALLBACK" >&2
  echo "$OUT2"
  exit 0
fi

echo "$OUT2" >&2
exit $EC2
