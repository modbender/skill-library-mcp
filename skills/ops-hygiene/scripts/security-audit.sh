#!/bin/bash
# Security Audit — comprehensive monthly check
# Usage: bash security-audit.sh
# Combines secret scan, dependency audit, permission check, and config review

set -euo pipefail

WORKSPACE="${HOME}/.openclaw/workspace"
REPORT=""
ISSUES=0

log() { REPORT+="$1\n"; echo "$1"; }

log "🔒 Security Audit — $(date '+%Y-%m-%d %H:%M')"
log "════════════════════════════════════════════════"
log ""

# 1. Secret scan
log "▸ 1. SECRET SCAN"
if bash "$(dirname "$0")/secret-scan.sh" "$WORKSPACE" 2>&1 | grep -q "🔴"; then
    log "  ⚠️  SECRETS FOUND — see secret-scan output"
    ISSUES=$((ISSUES + 1))
else
    log "  ✅ No secrets in workspace"
fi
log ""

# 2. File permissions
log "▸ 2. FILE PERMISSIONS"
WORLD_READABLE=$(find "$WORKSPACE" -maxdepth 3 -name ".secrets" -o -name ".env" -o -name "*.key" 2>/dev/null | while read -r f; do
    if [ -f "$f" ]; then
        perms=$(stat -f "%Lp" "$f" 2>/dev/null || stat -c "%a" "$f" 2>/dev/null)
        if [ "${perms: -1}" != "0" ]; then
            echo "$f ($perms)"
        fi
    fi
done)

if [ -n "$WORLD_READABLE" ]; then
    log "  ⚠️  World-readable sensitive files:"
    echo "$WORLD_READABLE" | while read -r f; do log "     $f"; done
    ISSUES=$((ISSUES + 1))
else
    log "  ✅ Sensitive file permissions OK"
fi
log ""

# 3. Dependency audit
log "▸ 3. DEPENDENCY AUDIT"
for project_dir in "$HOME/projects/bot-network" "$WORKSPACE"; do
    if [ -f "$project_dir/package.json" ]; then
        log "  Node.js: $project_dir"
        VULN_COUNT=$(cd "$project_dir" && npm audit --json 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    v=d.get('metadata',{}).get('vulnerabilities',{})
    total=sum(v.values()) if isinstance(v,dict) else 0
    print(total)
except: print(0)
" 2>/dev/null || echo "0")
        if [ "$VULN_COUNT" -gt 0 ]; then
            log "  ⚠️  $VULN_COUNT vulnerabilities found"
            ISSUES=$((ISSUES + 1))
        else
            log "  ✅ No known vulnerabilities"
        fi
    fi
done
log ""

# 4. OpenClaw config review
log "▸ 4. OPENCLAW CONFIG"
CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$CONFIG" ]; then
    # Check if elevated commands are restricted
    ELEVATED=$(python3 -c "
import json
with open('$CONFIG') as f:
    c = json.load(f)
sec = c.get('security', {})
elevated = sec.get('elevated', 'unknown')
print(f'elevated={elevated}')
" 2>/dev/null || echo "error reading config")
    log "  Config: $ELEVATED"
else
    log "  ⚠️  No config found at $CONFIG"
fi
log ""

# 5. Open ports
log "▸ 5. NETWORK EXPOSURE"
LISTENING=$(lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep -v "^COMMAND" | awk '{print $1, $9}' | sort -u || echo "none")
if [ "$LISTENING" != "none" ] && [ -n "$LISTENING" ]; then
    log "  Listening services:"
    echo "$LISTENING" | while read -r line; do log "     $line"; done
    # Check for services on 0.0.0.0 (exposed to network)
    EXPOSED=$(echo "$LISTENING" | grep "0.0.0.0\|\*:" || true)
    if [ -n "$EXPOSED" ]; then
        log "  ⚠️  Services exposed to network (0.0.0.0):"
        echo "$EXPOSED" | while read -r line; do log "     $line"; done
        ISSUES=$((ISSUES + 1))
    fi
else
    log "  ✅ No unexpected listening services"
fi
log ""

# 6. Git status
log "▸ 6. GIT STATUS"
cd "$WORKSPACE" 2>/dev/null
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
MODIFIED=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
if [ "$UNTRACKED" -gt 0 ] || [ "$MODIFIED" -gt 0 ]; then
    log "  📝 $MODIFIED modified, $UNTRACKED untracked files"
else
    log "  ✅ Workspace clean"
fi
log ""

# 7. Stale sessions
log "▸ 7. STALE PROCESSES"
STALE=$(ps aux | grep -E "[n]ode server|[p]ython.*serve" | grep -v grep || true)
if [ -n "$STALE" ]; then
    STALE_COUNT=$(echo "$STALE" | wc -l | tr -d ' ')
    log "  📋 $STALE_COUNT background server processes running"
else
    log "  ✅ No stale server processes"
fi
log ""

# Summary
log "════════════════════════════════════════════════"
if [ "$ISSUES" -gt 0 ]; then
    log "🔴 AUDIT COMPLETE — $ISSUES issue(s) found"
else
    log "✅ AUDIT COMPLETE — all clear"
fi

exit $ISSUES
