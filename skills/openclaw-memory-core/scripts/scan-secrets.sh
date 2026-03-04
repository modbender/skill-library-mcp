#!/usr/bin/env bash
# Scan the repository for secrets using gitleaks or a built-in fallback.
# Usage: bash scripts/scan-secrets.sh
# Exit codes: 0 = clean, 1 = secrets found or error

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# --- High-entropy / known-pattern checks (built-in fallback) ---
# These patterns catch the most common secret types without external tools.

PATTERNS=(
  # AWS
  'AKIA[0-9A-Z]{16}'
  # Generic secret assignments
  '(?i)(secret|password|token|api_key|apikey|private_key)\s*[:=]\s*["\x27][^\s"'\'']{8,}'
  # Private keys
  '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'
  # GitHub tokens
  'gh[pousr]_[A-Za-z0-9_]{36,}'
  # npm tokens
  'npm_[A-Za-z0-9]{36,}'
  # Generic long hex secrets (64+ chars, e.g. signing keys)
  '(?i)(secret|key|token|sign)\s*[:=]\s*["\x27][0-9a-f]{64,}'
)

echo "Scanning for secrets in: $REPO_ROOT"

# Try gitleaks first (preferred)
if command -v gitleaks &>/dev/null; then
  echo "Using gitleaks..."
  gitleaks detect --source="$REPO_ROOT" --config="$REPO_ROOT/.gitleaks.toml" --verbose
  exit $?
fi

echo "gitleaks not found - using built-in pattern scanner..."

FOUND=0
for pattern in "${PATTERNS[@]}"; do
  # grep -rPn: recursive, Perl regex, line numbers
  # Exclude common non-source directories and files
  if grep -rPn "$pattern" "$REPO_ROOT" \
    --include='*.ts' --include='*.js' --include='*.json' --include='*.yml' \
    --include='*.yaml' --include='*.toml' --include='*.env' --include='*.md' \
    --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.git \
    --exclude-dir=.ai --exclude-dir=tests --exclude='package-lock.json' \
    --exclude='scan-secrets.sh' 2>/dev/null; then
    FOUND=1
  fi
done

if [ "$FOUND" -eq 1 ]; then
  echo ""
  echo "WARNING: Potential secrets detected! Review the matches above."
  echo "If they are false positives, add them to .gitleaks.toml allowlist."
  exit 1
else
  echo "No secrets found."
  exit 0
fi
