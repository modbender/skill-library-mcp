#!/usr/bin/env bash
# Pre-publish security & PII scan
# Usage: pre-publish-scan.sh <file-or-directory>
# Exit code 0 = clean, 1 = issues found

set -euo pipefail

TARGET="${1:-.}"
ISSUES=0
SCANNED=0

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

warn() { echo -e "${RED}✗ BLOCKED:${NC} $1"; ISSUES=$((ISSUES + 1)); }
note() { echo -e "${YELLOW}⚠ REVIEW:${NC} $1"; }
ok()   { echo -e "${GREEN}✓${NC} $1"; }

echo "=== Pre-Publish Security & PII Scan ==="
echo "Target: $TARGET"
echo ""

# Collect files
if [ -d "$TARGET" ]; then
  FILES=$(find "$TARGET" -type f \
    ! -path '*/.git/*' \
    ! -path '*/node_modules/*' \
    ! -name '*.png' ! -name '*.jpg' ! -name '*.gif' \
    ! -name '*.ico' ! -name '*.woff*' ! -name '*.ttf' \
    ! -name '*.zip' ! -name '*.tar*' ! -name '*.gz' \
    2>/dev/null)
else
  FILES="$TARGET"
fi

for f in $FILES; do
  SCANNED=$((SCANNED + 1))
  CONTENT=$(cat "$f" 2>/dev/null || continue)

  # --- SECRETS & KEYS ---

  # API keys / tokens (generic patterns)
  if echo "$CONTENT" | grep -qEi '(api[_-]?key|api[_-]?token|auth[_-]?token|access[_-]?token|secret[_-]?key|private[_-]?key)\s*[:=]\s*["\x27]?[A-Za-z0-9_/+=.@-]{16,}'; then
    warn "$f — Possible API key/token assignment"
  fi

  # AWS keys
  if echo "$CONTENT" | grep -qE 'AKIA[0-9A-Z]{16}'; then
    warn "$f — AWS Access Key ID detected"
  fi
  if echo "$CONTENT" | grep -qEi 'aws[_-]?secret[_-]?access[_-]?key'; then
    warn "$f — AWS Secret Access Key reference"
  fi

  # GitHub tokens
  if echo "$CONTENT" | grep -qE '(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}'; then
    warn "$f — GitHub token detected"
  fi

  # Anthropic keys
  if echo "$CONTENT" | grep -qE 'sk-ant-[A-Za-z0-9_-]{20,}'; then
    warn "$f — Anthropic API key detected"
  fi

  # OpenAI keys
  if echo "$CONTENT" | grep -qE 'sk-[A-Za-z0-9]{32,}'; then
    warn "$f — Possible OpenAI API key detected"
  fi

  # Generic private keys
  if echo "$CONTENT" | grep -q 'BEGIN.*PRIVATE KEY'; then
    warn "$f — Private key block detected"
  fi

  # Bearer tokens in code
  if echo "$CONTENT" | grep -qEi 'Bearer [A-Za-z0-9_/+=.-]{20,}'; then
    warn "$f — Bearer token detected"
  fi

  # Passwords in assignments
  if echo "$CONTENT" | grep -qEi '(password|passwd|pwd)\s*[:=]\s*["\x27][^\s"'\'']{4,}'; then
    warn "$f — Possible hardcoded password"
  fi

  # .env style secrets
  if echo "$CONTENT" | grep -qEi '^[A-Z_]*(SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL)[A-Z_]*\s*=\s*[^\s]{8,}'; then
    warn "$f — Environment variable with secret value"
  fi

  # --- PII (Personal Identifiable Information) ---

  # Email addresses
  if echo "$CONTENT" | grep -qEi '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'; then
    # Skip obvious non-PII emails
    if ! echo "$CONTENT" | grep -qEi '(example\.com|test\.com|placeholder|noreply)'; then
      note "$f — Email address(es) found — verify not personal"
    fi
  fi

  # Phone numbers (North American + international)
  if echo "$CONTENT" | grep -qE '(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'; then
    note "$f — Possible phone number(s) — verify not personal"
  fi

  # IP addresses (non-localhost, non-example)
  if echo "$CONTENT" | grep -qE '\b(?!127\.0\.0\.1|0\.0\.0\.0|192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b' 2>/dev/null; then
    note "$f — Public IP address(es) found — verify intended"
  fi

  # Physical addresses (street patterns)
  if echo "$CONTENT" | grep -qEi '\d{1,5}\s+(N|S|E|W|North|South|East|West)?\s*\w+\s+(St|Ave|Blvd|Dr|Rd|Ln|Way|Ct|Pl|Cir)\.?\b'; then
    note "$f — Possible physical address — verify not personal"
  fi

  # SSN pattern
  if echo "$CONTENT" | grep -qE '\b\d{3}-\d{2}-\d{4}\b'; then
    warn "$f — Possible SSN detected"
  fi

  # Credit card patterns
  if echo "$CONTENT" | grep -qE '\b[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b'; then
    note "$f — Possible credit card number — verify"
  fi

  # Real names near personal context
  # (This catches common PII patterns like "Name: John Smith")
  if echo "$CONTENT" | grep -qEi '(full[_\s]?name|real[_\s]?name|legal[_\s]?name)\s*[:=]'; then
    note "$f — Name field found — verify not personal"
  fi

  # --- INTERNAL PATHS ---

  # Home directory paths
  if echo "$CONTENT" | grep -qE '/Users/[a-zA-Z0-9_]+/|/home/[a-zA-Z0-9_]+/'; then
    note "$f — Home directory path found — may reveal username"
  fi

  # OpenClaw internal paths
  if echo "$CONTENT" | grep -qE '\.openclaw/(config|workspace)'; then
    note "$f — OpenClaw internal path — verify intended"
  fi

  # --- DANGEROUS CODE PATTERNS ---

  # Exfiltration endpoints
  if echo "$CONTENT" | grep -qiE '(webhook\.site|ngrok\.io|pipedream|requestbin|burpcollaborator|interact\.sh|oastify)'; then
    warn "$f — Known exfiltration endpoint detected"
  fi

  # Reverse shell patterns
  if echo "$CONTENT" | grep -qE '(mkfifo|/dev/tcp/|ncat\s.*-e|nc\s.*-e)'; then
    warn "$f — Possible reverse shell pattern"
  fi

  # Bulk env harvesting
  if echo "$CONTENT" | grep -qE '(\$\{!.*@\}|printenv\s*$|printenv\s*\|)'; then
    warn "$f — Bulk environment variable harvesting"
  fi

  # Code obfuscation
  if echo "$CONTENT" | grep -qE '(eval\s*\(.*base64|atob\s*\(|Buffer\.from\s*\(.*(base64|hex))'; then
    note "$f — Possible code obfuscation — verify intended"
  fi

  # Path traversal
  if echo "$CONTENT" | grep -qE '(\.\./\.\./|/etc/passwd|/etc/shadow|~\/\.ssh|~\/\.aws)'; then
    warn "$f — Path traversal or sensitive file access pattern"
  fi

done

echo ""
echo "--- Results ---"
echo "Files scanned: $SCANNED"

if [ $ISSUES -gt 0 ]; then
  echo -e "${RED}BLOCKED: $ISSUES issue(s) found. Fix before publishing.${NC}"
  exit 1
else
  ok "No blocking issues found."
  echo "Review any ⚠ REVIEW items above before proceeding."
  exit 0
fi
