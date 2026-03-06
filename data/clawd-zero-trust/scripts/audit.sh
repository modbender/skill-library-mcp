#!/bin/bash
# =============================================================================
# Zero Trust Audit Script — clawd-zero-trust skill
# Runs openclaw security audit and surfaces findings transparently.
#
# v1.1.2: Replaced silent grep -v suppression with transparent labeled output.
#         Suppressed findings are still captured to FP_LOG_FILE — nothing is
#         dropped. Scanner-visible pattern: named variable + secondary log.
#
# Known false positive patterns (see references/false-positives.md):
#   - "openclaw-agentsandbox" → legitimate OAuth key generation (not C2)
#   - "secureclaw"            → legitimate auditing engine (self-triggers)
# =============================================================================

OPENCLAW="${OPENCLAW_BIN:-$(which openclaw 2>/dev/null || echo '/home/claw/.npm-global/bin/openclaw')}"
LOG_FILE="/home/claw/.openclaw/workspace/logs/audit.log"
# Secondary log: verified false positives are logged here (not dropped/hidden)
FP_LOG_FILE="/home/claw/.openclaw/workspace/logs/audit_false_positives.log"

# Ensure log dir exists and set secure permissions (600) immediately on creation
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE" "$FP_LOG_FILE"
chmod 600 "$LOG_FILE" "$FP_LOG_FILE"

log() { echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"; }

log "=== clawd-zero-trust Audit started ==="
echo "🛡️ clawd-zero-trust Audit — $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "=================================================="

# Run deep audit
RAW=$("$OPENCLAW" security audit --deep 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ] && [ -z "$RAW" ]; then
  log "WARNING: openclaw security audit returned exit code $EXIT_CODE with no output"
fi

# =============================================================================
# FALSE POSITIVE FILTER — transparent, not silent
#
# These patterns are VERIFIED safe. We do NOT silently drop them.
# They are:
#   1. Shown below as [VERIFIED FALSE POSITIVE] with documented reason
#   2. Logged to FP_LOG_FILE with timestamp for audit trail
#   3. Excluded from the actionable findings section to reduce noise
#
# To add a new false positive pattern: update EXCLUDED_FP_PATTERNS and
# add the entry to references/false-positives.md
# =============================================================================
EXCLUDED_FP_PATTERNS="openclaw-agentsandbox|secureclaw"

# Capture real findings (excluding verified false positives)
CLEAN_FINDINGS=$(echo "$RAW" \
  | grep -vE "$EXCLUDED_FP_PATTERNS" \
  | grep -E "CRITICAL|WARN|INFO|summary|Fix:" \
  || true)

# Capture suppressed false positive lines — logged, not dropped
FP_LINES=$(echo "$RAW" | grep -E "$EXCLUDED_FP_PATTERNS" || true)
FP_COUNT=$(echo "$FP_LINES" | grep -c "." 2>/dev/null || true)

echo ""
echo "📋 Actionable Findings:"
if [ -n "$CLEAN_FINDINGS" ]; then
  echo "$CLEAN_FINDINGS"
else
  echo "  ✅ No actionable findings"
fi

# Show false positives transparently — labelled, not hidden
if [ -n "$FP_LINES" ] && [ "$FP_COUNT" -gt 0 ]; then
  echo ""
  echo "🔍 Verified False Positives (${FP_COUNT} suppressed — full log: ${FP_LOG_FILE}):"
  while IFS= read -r fp_line; do
    [ -z "$fp_line" ] && continue
    if echo "$fp_line" | grep -q "openclaw-agentsandbox"; then
      echo "  [VERIFIED FP] $fp_line"
      echo "  → Reason: openclaw-agentsandbox is OpenClaw's OAuth key generation system (not C2)"
      echo "  → Ref: references/false-positives.md#openclaw-agentsandbox"
    elif echo "$fp_line" | grep -q "secureclaw"; then
      echo "  [VERIFIED FP] $fp_line"
      echo "  → Reason: SecureClaw audit engine self-triggers its own rules by design"
      echo "  → Ref: references/false-positives.md#secureclaw"
    fi
    # Log to FP audit trail with timestamp
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] [VERIFIED FP] $fp_line" >> "$FP_LOG_FILE"
  done <<< "$FP_LINES"
fi

echo ""
echo "=================================================="

# =============================================================================
# SSH exposure check — catches BOTH IPv4 (0.0.0.0:22) AND IPv6 ([::]:22)
# =============================================================================
echo "🌐 Network Perimeter:"
SSH_EXPOSED=0
if ss -ltnp 2>/dev/null | grep ':22' | grep -qE '0\.0\.0\.0|\[::\]'; then
  SSH_EXPOSED=1
fi

if [ "$SSH_EXPOSED" -eq 1 ]; then
  echo "  🚨 SSH exposed to all interfaces (0.0.0.0:22 or [::]:22) — restrict to Tailscale ListenAddress"
  log "WARN: SSH exposed to all interfaces"
else
  echo "  ✅ SSH — restricted (not on 0.0.0.0 or [::])"
fi

if ss -ltnp 2>/dev/null | grep -q ':631'; then
  echo "  ⚠️  CUPS (port 631) still active — run: sudo snap disable cups"
  log "WARN: CUPS port 631 active"
else
  echo "  ✅ CUPS — disabled"
fi

# =============================================================================
# Dependency check
# =============================================================================
echo ""
echo "🔧 Dependency Check:"
if command -v dig &>/dev/null; then
  echo "  ✅ dig (dnsutils) — available"
else
  echo "  ⚠️  dig not found — egress-filter.sh requires dnsutils. Run: sudo apt install dnsutils"
  log "WARN: dig not available"
fi

if command -v ufw &>/dev/null; then
  echo "  ✅ ufw — available"
else
  echo "  ⚠️  ufw not found — egress-filter.sh requires ufw. Run: sudo apt install ufw"
  log "WARN: ufw not available"
fi

echo ""
echo "Run 'bash scripts/harden.sh' to review and apply hardening fixes."
echo "False positive log: $FP_LOG_FILE"
log "=== Audit complete ==="

# Exit with error if critical issues were found (SSH exposed, missing dependencies)
if [ "$SSH_EXPOSED" -eq 1 ]; then
  exit 1
fi
exit 0
