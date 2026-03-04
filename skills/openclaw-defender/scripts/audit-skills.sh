#!/bin/bash
# Skill Security Audit Script
# Part of openclaw-defender
# Note: Auditing openclaw-defender itself may report violations from its documentation of threat patterns; that is expected.

SKILL_PATH="$1"
DEFENDER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLOCKLIST_FILE="$DEFENDER_ROOT/references/blocklist.conf"

# Load blocklist from file or fallback to built-in
# Strips inline # comments and trims whitespace so entries match correctly
get_blocklist_section() {
  local section="$1"
  if [ -f "$BLOCKLIST_FILE" ]; then
    sed -n "/^\[$section\]/,/^\[/p" "$BLOCKLIST_FILE" | grep -v '^\[' | grep -v '^$' | sed 's/#.*$//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | tr '\n' '|' | sed 's/|$//'
  fi
}
BLOCKLIST_SKILLS_RAW="$(get_blocklist_section skills)"
BLOCKLIST_AUTHORS_RAW="$(get_blocklist_section authors)"
BLOCKLIST_SKILLS="${BLOCKLIST_SKILLS_RAW:-clawhub|clawhub1|clawdhub1|clawhud|polymarket-traiding-bot|base-agent|bybit-agent|moltbook-lm8|moltbookagent|publish-dist}"
BLOCKLIST_AUTHORS="${BLOCKLIST_AUTHORS_RAW:-zaycv|Aslaep123|moonshine-100rze|pepe276|aztr0nutzs|Ddoy233}"

if [ -z "$SKILL_PATH" ]; then
  echo "Usage: $0 <path-to-skill-directory>"
  exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
  echo "Error: $SKILL_PATH is not a directory"
  exit 1
fi

SKILL_NAME=$(basename "$SKILL_PATH")
SKILL_MD="$SKILL_PATH/SKILL.md"

echo "=== OpenClaw Defender: Skill Security Audit ==="
echo "Skill: $SKILL_NAME"
echo "Path: $SKILL_PATH"
echo ""

if [ ! -f "$SKILL_MD" ]; then
  echo "❌ FAIL: No SKILL.md found"
  exit 1
fi

VIOLATIONS=0

# Check 1: Base64 encoding
echo "--- Checking for base64 encoding ---"
if grep -qi "base64" "$SKILL_MD"; then
  echo "⚠️  WARNING: Base64 pattern detected"
  grep -n "base64" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ PASS"
fi

# Check 2: Suspicious downloads
echo ""
echo "--- Checking for suspicious downloads ---"
if grep -iE "(curl|wget).*\|.*bash" "$SKILL_MD"; then
  echo "🚨 CRITICAL: curl|bash pattern detected"
  grep -n -iE "(curl|wget).*\|.*bash" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 5))
elif grep -iE "\.(zip|exe|dmg|pkg)" "$SKILL_MD" | grep -qi "password"; then
  echo "🚨 CRITICAL: Password-protected archive detected"
  VIOLATIONS=$((VIOLATIONS + 5))
elif grep -iE "(curl|wget|download)" "$SKILL_MD"; then
  echo "⚠️  WARNING: Download detected (review manually)"
  grep -n -iE "(curl|wget|download)" "$SKILL_MD" | head -5
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "✓ PASS"
fi

# Check 3: Credential requests
echo ""
echo "--- Checking for credential requests ---"
if grep -iE "(echo|print|log).*\$.*(_KEY|_TOKEN|_PASSWORD|_SECRET)" "$SKILL_MD"; then
  echo "🚨 CRITICAL: Credential echo/print detected"
  grep -n -iE "(echo|print|log).*\$.*(_KEY|_TOKEN|_PASSWORD|_SECRET)" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 5))
else
  echo "✓ PASS"
fi

# Check 4: Jailbreak patterns
echo ""
echo "--- Checking for jailbreak patterns ---"
if grep -iE "(ignore.*(previous|above|prior).*(instruction|command|prompt))" "$SKILL_MD"; then
  echo "🚨 CRITICAL: Prompt injection detected"
  grep -n -iE "(ignore.*(previous|above|prior).*(instruction|command|prompt))" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 5))
elif grep -iE "(you are now|system.?prompt|DAN mode)" "$SKILL_MD"; then
  echo "🚨 CRITICAL: Jailbreak attempt detected"
  grep -n -iE "(you are now|system.?prompt|DAN mode)" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 5))
else
  echo "✓ PASS"
fi

# Check 5: Unicode tricks (portable: perl works on macOS and Linux)
echo ""
echo "--- Checking for unicode steganography ---"
if perl -ne 'exit 1 if /[\x{200B}-\x{200D}\x{FEFF}\x{2060}]/' "$SKILL_MD" 2>/dev/null; then
  echo "✓ PASS"
else
  echo "🚨 CRITICAL: Invisible Unicode characters detected"
  VIOLATIONS=$((VIOLATIONS + 5))
fi

# Check 6: Memory poisoning
echo ""
echo "--- Checking for memory poisoning attempts ---"
if grep -iE "(SOUL|MEMORY|IDENTITY)\.md" "$SKILL_MD" | grep -iE "(modify|change|update|edit|write)"; then
  echo "🚨 CRITICAL: Memory modification detected"
  grep -n -iE "(SOUL|MEMORY|IDENTITY)\.md" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 5))
else
  echo "✓ PASS"
fi

# Check 7: Known malicious infrastructure
echo ""
echo "--- Checking for known malicious infrastructure ---"
if grep -E "91\.92\.242\.30" "$SKILL_MD"; then
  echo "🚨 CRITICAL: Known C2 server detected (91.92.242.30)"
  VIOLATIONS=$((VIOLATIONS + 10))
else
  echo "✓ PASS"
fi

# Check 8: Known malicious skill names and authors (blocklist from references/blocklist.conf)
echo ""
echo "--- Checking blocklist (skill names / authors) ---"
BLOCKLIST_HIT=""
if echo "$SKILL_NAME" | grep -qiE "$BLOCKLIST_SKILLS"; then
  BLOCKLIST_HIT="skill name ($SKILL_NAME)"
fi
# Only check author in frontmatter (so documenting blocklist in body doesn't trigger)
FRONTMATTER="$(sed -n '/^---$/,/^---$/p' "$SKILL_MD" | head -n -1 | tail -n +2)"
if echo "$FRONTMATTER" | grep -qiE "$BLOCKLIST_AUTHORS"; then
  [ -n "$BLOCKLIST_HIT" ] && BLOCKLIST_HIT="$BLOCKLIST_HIT and "
  BLOCKLIST_HIT="${BLOCKLIST_HIT}blocklisted author in SKILL.md frontmatter"
fi
# Also check extracted author from frontmatter (homepage / metadata)
GITHUB_URL="$(head -80 "$SKILL_MD" | grep -oE 'https?://github\.com/[^/[:space:]")]+' | head -1)"
if [ -n "$GITHUB_URL" ]; then
  GITHUB_USER="$(echo "$GITHUB_URL" | sed -E 's|.*github\.com/||' | cut -d/ -f1)"
  for a in $(echo "$BLOCKLIST_AUTHORS" | tr '|' '\n'); do
    [ -z "$a" ] && continue
    if [ "$(echo "$GITHUB_USER" | tr '[:upper:]' '[:lower:]')" = "$(echo "$a" | tr '[:upper:]' '[:lower:]')" ]; then
      [ -n "$BLOCKLIST_HIT" ] && BLOCKLIST_HIT="$BLOCKLIST_HIT and "
      BLOCKLIST_HIT="${BLOCKLIST_HIT}blocklisted GitHub user ($GITHUB_USER)"
      break
    fi
  done
fi
if [ -n "$BLOCKLIST_HIT" ]; then
  echo "🚨 CRITICAL: Blocklist match: $BLOCKLIST_HIT"
  VIOLATIONS=$((VIOLATIONS + 10))
else
  echo "✓ PASS"
fi

# Check 9: glot.io (common in ClawHavoc macOS vector)
echo ""
echo "--- Checking for glot.io paste / obfuscated install ---"
if grep -qi "glot\.io" "$SKILL_MD"; then
  echo "🚨 CRITICAL: glot.io snippet detected (known malware vector)"
  grep -n "glot\.io" "$SKILL_MD"
  VIOLATIONS=$((VIOLATIONS + 5))
else
  echo "✓ PASS"
fi

# Check 10: GitHub account age (optional; requires curl + jq)
echo ""
echo "--- Checking GitHub author age (if homepage present) ---"
if [ -n "$GITHUB_USER" ] && command -v curl >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  CREATED="$(curl -sS "https://api.github.com/users/$GITHUB_USER" 2>/dev/null | jq -r '.created_at // empty')"
  if [ -n "$CREATED" ]; then
    CREATED_EPOCH=$(date -d "$CREATED" +%s 2>/dev/null)
    [ -z "$CREATED_EPOCH" ] && CREATED_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$CREATED" +%s 2>/dev/null)
    NOW_EPOCH=$(date +%s)
    DAYS_OLD=$(( (NOW_EPOCH - CREATED_EPOCH) / 86400 ))
    if [ -n "$CREATED_EPOCH" ] && [ "$DAYS_OLD" -lt 90 ] 2>/dev/null; then
      echo "⚠️  WARNING: GitHub account $GITHUB_USER is $DAYS_OLD days old (< 90 day minimum)"
      VIOLATIONS=$((VIOLATIONS + 2))
    else
      echo "✓ PASS (account $DAYS_OLD days old)"
    fi
  else
    echo "  (could not fetch or invalid response)"
  fi
else
  echo "  (skip: no GitHub URL, or curl/jq not available)"
fi

# Summary
echo ""
echo "=== Audit Summary ==="
echo "Total violations: $VIOLATIONS"

if [ $VIOLATIONS -eq 0 ]; then
  echo "✅ PASS: No security issues detected"
  exit 0
elif [ $VIOLATIONS -lt 5 ]; then
  echo "⚠️  WARN: Minor issues found (review manually)"
  exit 1
else
  echo "🚨 FAIL: CRITICAL security issues detected"
  echo "Recommendation: DO NOT INSTALL"
  exit 2
fi
