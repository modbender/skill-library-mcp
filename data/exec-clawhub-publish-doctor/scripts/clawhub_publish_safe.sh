#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  clawhub_publish_safe.sh <skill_path> <slug> <name> <version> [changelog]

Example:
  clawhub_publish_safe.sh ./skills/my-skill my-skill "My Skill" 1.0.0 "Initial release"
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 4 ]]; then
  usage
  exit 2
fi

SKILL_PATH="$1"
SLUG="$2"
NAME="$3"
VERSION="$4"
CHANGELOG="${5:-Auto publish via exec-clawhub-publish-doctor}"
MAX_RETRIES="${MAX_RETRIES:-12}"
SLEEP_SECONDS="${SLEEP_SECONDS:-10}"

if ! command -v clawhub >/dev/null 2>&1; then
  echo "ERROR: clawhub not found. Install: npm i -g clawhub" >&2
  exit 3
fi

if ! clawhub whoami >/tmp/clawhub_publish_whoami.out 2>/tmp/clawhub_publish_whoami.err; then
  echo "ERROR: Not logged in. Run: clawhub login --token <clh_token>" >&2
  exit 4
fi

echo "Publishing ${SLUG}@${VERSION}..."
clawhub publish "$SKILL_PATH" \
  --slug "$SLUG" \
  --name "$NAME" \
  --version "$VERSION" \
  --changelog "$CHANGELOG" \
  --tags latest

echo "Verifying with retry (inspect may be temporarily hidden during security scan)..."
for ((i=1; i<=MAX_RETRIES; i++)); do
  if OUT=$(clawhub inspect "$SLUG" --json 2>&1); then
    echo "$OUT"
    echo "OK: ${SLUG} is inspectable."
    exit 0
  fi

  if echo "$OUT" | grep -qiE 'hidden while security scan is pending|Skill not found'; then
    echo "Attempt ${i}/${MAX_RETRIES}: still pending visibility. Waiting ${SLEEP_SECONDS}s..."
    sleep "$SLEEP_SECONDS"
    continue
  fi

  echo "ERROR: Non-transient inspect failure:" >&2
  echo "$OUT" >&2
  exit 5
done

echo "WARN: Published, but inspect is still pending after retries." >&2
echo "Check: https://clawhub.ai/skills/${SLUG}" >&2
exit 0
