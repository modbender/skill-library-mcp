#!/usr/bin/env bash
set -uo pipefail
# Note: -e disabled because grep returns non-zero when no match found

# security-scan.sh - Security audit a skill before publishing
# Usage: security-scan.sh <skill-folder>

usage() {
  echo "Usage: $0 <skill-folder>"
  echo ""
  echo "Scans skill for security red flags."
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
fi

SKILL_DIR="$1"
RED_FLAGS=()
WARNINGS=()

if [[ ! -d "$SKILL_DIR" ]]; then
  echo "❌ Error: Directory not found: $SKILL_DIR"
  exit 1
fi

SKILL_NAME=$(basename "$SKILL_DIR")

echo "🔒 Security scanning: $SKILL_NAME"
echo ""

# Find all files
ALL_FILES=$(find "$SKILL_DIR" -type f 2>/dev/null)

# Patterns to check
echo "Checking for dangerous patterns..."

# 1. Remote code execution / eval
# Skip checking our own scripts (they contain detection patterns / legitimate eval)
for file in $ALL_FILES; do
  [[ "$(basename "$file")" =~ ^(security-scan|publish|validate|scaffold)\.sh$ ]] && continue
  if grep -l -E "(eval\s*\(|exec\s*\(|subprocess\.call.*shell=True|os\.system\()" "$file" 2>/dev/null; then
    WARNINGS+=("Potential code execution in: $(basename "$file") - review eval/exec usage")
  fi
done

# 2. Curl/wget to unknown hosts (excluding common safe hosts)
SAFE_HOSTS="github.com|githubusercontent.com|clawhub.com|here.now|api.openai.com|api.anthropic.com"
for file in $ALL_FILES; do
  SUSPICIOUS_URLS=$(grep -oE "(curl|wget)[^|&;]*https?://[^\s\"')\`]+" "$file" 2>/dev/null | grep -vE "$SAFE_HOSTS" || true)
  if [[ -n "$SUSPICIOUS_URLS" ]]; then
    RED_FLAGS+=("External network call in $(basename "$file"): $SUSPICIOUS_URLS")
  fi
done

# 3. Remote prompt injection vector (fetching instructions from URLs)
# Skip this check on security-scan.sh itself (it contains detection patterns)
for file in $ALL_FILES; do
  [[ "$(basename "$file")" == "security-scan.sh" ]] && continue
  if grep -l -E "curl.*skill\.md|fetch.*instructions|download.*prompt" "$file" 2>/dev/null; then
    RED_FLAGS+=("CRITICAL: Remote instruction fetch in $(basename "$file") - potential prompt injection vector")
  fi
done

# 4. Environment variable harvesting (beyond reasonable scope)
for file in $ALL_FILES; do
  [[ "$(basename "$file")" =~ ^(security-scan|publish|validate|scaffold)\.sh$ ]] && continue
  ENV_HARVEST=$(grep -oE '\$\{?[A-Z_]+\}?' "$file" 2>/dev/null | sort -u | wc -l)
  if [[ $ENV_HARVEST -gt 10 ]]; then
    WARNINGS+=("Many env vars accessed in $(basename "$file") ($ENV_HARVEST) - verify necessity")
  fi
  
  # Specific dangerous env vars
  if grep -l -E "(AWS_SECRET|PRIVATE_KEY|PASSWORD|TOKEN.*=)" "$file" 2>/dev/null; then
    WARNINGS+=("Sensitive env var pattern in $(basename "$file") - review carefully")
  fi
done

# 5. Base64 encoded payloads
for file in $ALL_FILES; do
  [[ "$(basename "$file")" =~ ^(security-scan|publish|validate|scaffold)\.sh$ ]] && continue
  if grep -l -E "base64.*-d|atob\(|decode\('base64'\)" "$file" 2>/dev/null; then
    WARNINGS+=("Base64 decoding in $(basename "$file") - check for hidden payloads")
  fi
done

# 6. File permissions - check for setuid/setgid (4xxx, 2xxx) which are dangerous
while IFS= read -r file; do
  PERMS=$(stat -c %a "$file" 2>/dev/null || stat -f %OLp "$file" 2>/dev/null || echo "")
  # Only flag setuid (4xxx), setgid (2xxx), or world-writable (xx7)
  if [[ "$PERMS" =~ ^[42] ]] || [[ "$PERMS" =~ [0-7][0-7]7$ ]]; then
    WARNINGS+=("Dangerous permissions on $(basename "$file"): $PERMS")
  fi
done <<< "$ALL_FILES"

# 7. Hidden files (other than .gitkeep)
HIDDEN=$(find "$SKILL_DIR" -name ".*" -type f ! -name ".gitkeep" ! -name ".clawhub" 2>/dev/null)
if [[ -n "$HIDDEN" ]]; then
  WARNINGS+=("Hidden files found: $HIDDEN")
fi

# 8. Check SKILL.md for auto-update patterns (like here-now had)
if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
  if grep -qE "curl.*version|fetch.*latest|check.*update.*curl" "$SKILL_DIR/SKILL.md"; then
    RED_FLAGS+=("CRITICAL: SKILL.md contains auto-update pattern - remote instruction injection risk")
  fi
fi

# Print results
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ ${#RED_FLAGS[@]} -gt 0 ]]; then
  echo "🔴 RED FLAGS (do not publish until resolved):"
  for flag in "${RED_FLAGS[@]}"; do
    echo "   • $flag"
  done
  echo ""
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo "🟡 WARNINGS (review before publishing):"
  for warn in "${WARNINGS[@]}"; do
    echo "   • $warn"
  done
  echo ""
fi

if [[ ${#RED_FLAGS[@]} -eq 0 && ${#WARNINGS[@]} -eq 0 ]]; then
  echo "✅ No security issues detected!"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Summary
echo ""
echo "Files scanned: $(echo "$ALL_FILES" | wc -l)"
echo "Red flags: ${#RED_FLAGS[@]}"
echo "Warnings: ${#WARNINGS[@]}"

# Exit with error if there are red flags
if [[ ${#RED_FLAGS[@]} -gt 0 ]]; then
  echo ""
  echo "⛔ Publish blocked due to red flags. Fix issues and re-scan."
  exit 1
fi

exit 0
