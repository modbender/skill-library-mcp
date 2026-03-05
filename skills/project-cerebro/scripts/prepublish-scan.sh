#!/usr/bin/env bash
set -euo pipefail

# Prepublish secret scan for Project Cerebro.
# Fails if we detect likely secrets or personal identifiers in tracked source.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v rg >/dev/null 2>&1; then
  echo "ERROR: ripgrep (rg) is required for the prepublish scan." >&2
  exit 2
fi

# Only scan files that could ship: source + docs + config templates.
# Avoid scanning DBs, node_modules, build outputs, etc.
SCAN_PATHS=(
  "src"
  "frontend/src"
  "config"
  "README.md"
  "SETUP.md"
  "ARCHITECTURE.md"
  ".env.example"
)

# Patterns: tune conservative (better a false positive than leaking a token).
PATTERNS=(
  "AIza[0-9A-Za-z\\-_]{20,}"                     # Google API keys
  "sk-[0-9A-Za-z]{20,}"                           # OpenAI-style keys
  "xox[baprs]-[0-9A-Za-z\\-]{10,}"                # Slack tokens
  "-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"
  "Bearer[[:space:]]+[A-Za-z0-9._-]{10,}"
  "TODOIST_API_TOKEN"
  "GOCSPX-"                                        # Google OAuth client secret prefix
  # NOTE: we intentionally reference these ENV VAR NAMES in docs and code.
  # We do NOT want to fail the scan on the variable names themselves.
  # We want to fail on *actual token-like values*.
)

# Disallow referencing the user's OpenClaw state/config path (can encourage reading secrets).
# Allow mentions in docs only.
DISALLOWED_PATH_PATTERN="\\.openclaw/openclaw\\.json"


# Also catch obvious personal emails (best-effort). This will flag docs if you put a real email.
EMAIL_PATTERN='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'

fail=0

echo "== Prepublish secret scan =="

echo "Scanning paths: ${SCAN_PATHS[*]}"

for p in "${PATTERNS[@]}"; do
  if rg -n -S --hidden --no-ignore \
    -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/frontend/dist/**' -g'!**/*.db*' \
    "$p" "${SCAN_PATHS[@]}" >/dev/null 2>&1; then
    echo "\n[FAIL] Matched pattern: $p" >&2
    rg -n -S --hidden --no-ignore \
      -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/frontend/dist/**' -g'!**/*.db*' \
      "$p" "${SCAN_PATHS[@]}" | head -n 50 >&2
    fail=1
  fi
done

# Disallow local OpenClaw config path references in source code (docs are OK).
if rg -n -S --hidden --no-ignore \
  -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/frontend/dist/**' -g'!**/*.db*' \
  "$DISALLOWED_PATH_PATTERN" src frontend/src >/dev/null 2>&1; then
  echo "\n[FAIL] Source code references ~/.openclaw/openclaw.json directly (avoid reading local secret config in publishable code)." >&2
  rg -n -S "$DISALLOWED_PATH_PATTERN" src frontend/src | head -n 50 >&2
  fail=1
fi

# Email scan: allow obvious placeholders only.
# If we find emails, fail unless they are clearly placeholders.
if rg -n -S --hidden --no-ignore -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/frontend/dist/**' -g'!**/*.db*' "$EMAIL_PATTERN" "${SCAN_PATHS[@]}" >/dev/null 2>&1; then
  # If any email that is NOT a placeholder exists, fail.
  matches=$(rg -n -S --hidden --no-ignore -g'!**/node_modules/**' -g'!**/dist/**' -g'!**/frontend/dist/**' -g'!**/*.db*' "$EMAIL_PATTERN" "${SCAN_PATHS[@]}" | head -n 200)
  if echo "$matches" | rg -v "(you@example.com|YOUR_|example\\.com|example\\.org)" >/dev/null 2>&1; then
    echo "\n[FAIL] Found email-like strings (non-placeholder)." >&2
    echo "$matches" | head -n 50 >&2
    fail=1
  fi
fi

if [[ "$fail" -eq 1 ]]; then
  echo "\nPrepublish scan FAILED. Remove secrets/PII before publishing." >&2
  exit 1
fi

echo "Prepublish scan OK."
