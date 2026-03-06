#!/bin/bash
# =============================================================================
# verify.sh — Post-deployment verification suite
# =============================================================================
# Usage: bash verify.sh
# Returns exit code 0 if all critical checks pass
# =============================================================================

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $name"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name"
        FAIL=$((FAIL + 1))
    fi
}

warn_check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $name"
        PASS=$((PASS + 1))
    else
        echo "  ⚠️  $name (non-critical)"
        WARN=$((WARN + 1))
    fi
}

echo "=== OpenClaw Verification Suite ==="
echo

echo "🔧 CORE SERVICES:"
check "Node.js installed" "node --version"
check "OpenClaw installed" "openclaw --version"
check "Gateway running" "systemctl is-active openclaw-gateway"
check "Gateway port responsive" "nc -z 127.0.0.1 18789"

echo
echo "📁 WORKSPACE FILES:"
check "SOUL.md exists" "test -f ~/.openclaw/workspace/SOUL.md"
check "AGENTS.md exists" "test -f ~/.openclaw/workspace/AGENTS.md"
check "MEMORY.md exists" "test -f ~/.openclaw/workspace/MEMORY.md"
check "USER.md exists" "test -f ~/.openclaw/workspace/USER.md"
warn_check "memory/ has files" "test $(ls ~/.openclaw/workspace/memory/*.md 2>/dev/null | wc -l) -gt 0"

echo
echo "🔐 SECURITY:"
check "SSH key-only auth" "! grep -q '^PasswordAuthentication yes' /etc/ssh/sshd_config"
warn_check "UFW firewall active" "sudo ufw status | grep -q 'Status: active'"
warn_check "Fail2Ban running" "sudo fail2ban-client status sshd"
warn_check "GPG key exists" "gpg --list-keys 2>/dev/null | grep -q 'pub'"
warn_check "Pass store initialized" "pass ls >/dev/null 2>&1"

echo
echo "🌐 CONNECTIVITY:"
warn_check "Chrome installed" "google-chrome --version"
warn_check "Internet access" "curl -s --max-time 5 https://api.telegram.org >/dev/null"

echo
echo "💾 BACKUP:"
warn_check "Backup script exists" "test -x ~/.openclaw/workspace/scripts/backup-memory.sh"

echo
echo "============================================"
echo "  Results: ✅ $PASS passed | ❌ $FAIL failed | ⚠️  $WARN warnings"
echo "============================================"

if [ $FAIL -gt 0 ]; then
    echo "  ⚠️  Some critical checks failed. Review above."
    exit 1
else
    echo "  🎉 All critical checks passed!"
    exit 0
fi
