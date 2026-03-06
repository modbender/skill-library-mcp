#!/usr/bin/env bash
set -euo pipefail

# pre-install hook: scan a local skill folder and return decision.
# exit codes: 0 allow, 10 warn, 20 reject, 30 scanner/parse error

SCANNER_ROOT="${SCANNER_ROOT:-/home/guofeng/clawd/skill-trust-scanner}"
SCANNER_CLI="${SCANNER_CLI:-$SCANNER_ROOT/src/cli.ts}"

usage() {
  cat <<'EOF'
Usage: pre-install.sh [--json] <skill-path>

Runs skill-trust-scanner and evaluates policy:
  score < 50   => reject (exit 20)
  50-74        => warn   (exit 10)
  >= 75        => allow  (exit 0)

Output (stdout):
  SCORE=<n>
  SUMMARY=<risk-level-or-summary>
  DECISION=<allow|warn|reject>

With --json, prints scanner JSON after key-value lines.
EOF
}

PRINT_JSON=0
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi
if [[ "${1:-}" == "--json" ]]; then
  PRINT_JSON=1
  shift
fi

SKILL_PATH="${1:-}"
if [[ -z "$SKILL_PATH" ]]; then
  echo "missing-skill-path" >&2
  usage >&2
  exit 30
fi
if [[ ! -d "$SKILL_PATH" ]]; then
  echo "invalid-skill-path: $SKILL_PATH" >&2
  exit 30
fi
if [[ ! -f "$SCANNER_CLI" ]]; then
  echo "scanner-cli-not-found: $SCANNER_CLI" >&2
  exit 30
fi

RAW=$(cd "$SCANNER_ROOT" && npx tsx "$SCANNER_CLI" "$SKILL_PATH" --json 2>/dev/null || true)
if [[ -z "$RAW" ]]; then
  echo "scanner-empty-output" >&2
  exit 30
fi

PARSED=$(RAW="$RAW" node - <<'NODE'
const raw = process.env.RAW || '';
try {
  const start = raw.indexOf('{');
  const jsonText = start >= 0 ? raw.slice(start) : raw;
  const data = JSON.parse(jsonText);
  const score =
    typeof data.score === 'number' ? data.score :
    typeof data.score?.total === 'number' ? data.score.total :
    typeof data.result?.score === 'number' ? data.result.score :
    typeof data.result?.score?.total === 'number' ? data.result.score.total :
    typeof data.overallScore === 'number' ? data.overallScore :
    null;
  const summary = data.summary || data.score?.riskLevel || data.result?.summary || '';
  if (score === null) {
    console.log('PARSE_ERROR=1');
  } else {
    let decision = 'allow';
    if (score < 50) decision = 'reject';
    else if (score < 75) decision = 'warn';
    console.log(`SCORE=${Math.round(score)}`);
    console.log(`SUMMARY=${String(summary).replace(/\n/g,' ')}`);
    console.log(`DECISION=${decision}`);
  }
} catch {
  console.log('PARSE_ERROR=1');
}
NODE
)

if grep -q '^PARSE_ERROR=1$' <<<"$PARSED"; then
  echo "parse-error" >&2
  exit 30
fi

echo "$PARSED"
if [[ $PRINT_JSON -eq 1 ]]; then
  echo "$RAW"
fi

DECISION=$(awk -F= '/^DECISION=/{print $2}' <<<"$PARSED")
case "$DECISION" in
  allow) exit 0 ;;
  warn) exit 10 ;;
  reject) exit 20 ;;
  *) exit 30 ;;
esac
