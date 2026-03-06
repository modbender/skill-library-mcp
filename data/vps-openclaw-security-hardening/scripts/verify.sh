#!/bin/bash
# Verify VPS Security Hardening Installation
# Usage: ./verify.sh

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local command="$2"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} $name"
        ((FAIL++))
        return 1
    fi
}

warn() {
    local name="$1"
    echo -e "${YELLOW}⚠${NC} $name"
    ((WARN++))
}

echo "╔════════════════════════════════════════════════╗"
echo "║   VPS SECURITY HARDENING VERIFICATION          ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

echo "=== SSH CONFIGURATION ==="
SSH_PORT=${SSH_PORT:-$(grep "^Port " /etc/ssh/sshd_config | tail -1 | awk '{print $2}')}
SSH_PORT=${SSH_PORT:-22}
check "SSH running on port $SSH_PORT" "ss -tulnp | grep -q ':$SSH_PORT.*sshd'"
check "Password authentication disabled" "grep -q 'PasswordAuthentication no' /etc/ssh/sshd_config"
check "Root login disabled" "grep -q 'PermitRootLogin no' /etc/ssh/sshd_config"
check "Max auth tries configured" "grep -q 'MaxAuthTries' /etc/ssh/sshd_config"

echo ""
echo "=== FIREWALL (UFW) ==="
check "UFW installed" "which ufw"
check "UFW active" "ufw status | grep -q 'Status: active'"
check "UFW allows SSH port" "ufw status | grep -q 'SSH hardened'"
check "UFW denies incoming by default" "ufw status verbose | grep -q 'Default: deny (incoming)'"

echo ""
echo "=== AUDIT LOGGING ==="
check "Auditd installed" "which auditd"
check "Auditd running" "systemctl is-active --quiet auditd"
check "Audit rules loaded" "auditctl -l | grep -q agent_home"
check "Custom rules file exists" "test -f /etc/audit/rules.d/agent-security.rules"

echo ""
echo "=== AUTO-UPDATES ==="
check "Unattended-upgrades installed" "which unattended-upgrade"
check "Unattended-upgrades running" "systemctl is-active --quiet unattended-upgrades"

echo ""
echo "=== FAIL2BAN ==="
check "Fail2ban installed" "which fail2ban-server"
check "Fail2ban running" "systemctl is-active --quiet fail2ban"

echo ""
echo "=== CREDENTIAL SECURITY ==="
# Check credential file permissions (customize paths as needed)
CRED_PATHS=(
    "/root/.openclaw/.env"
    "/root/.env"
)
CRED_SECURE=0
for path in "${CRED_PATHS[@]}"; do
    if [[ -f "$path" ]]; then
        perms=$(stat -c "%a" "$path" 2>/dev/null || echo "000")
        if [[ "$perms" == "600" ]]; then
            ((CRED_SECURE++))
        fi
    fi
done

if [[ $CRED_SECURE -gt 0 ]]; then
    check "Credential file permissions (600)" "true"
else
    warn "No credential files found with secure permissions (600)"
fi

echo ""
echo "=== CRON JOBS ==="
check "Security cron installed" "test -f /etc/cron.d/agent-security"

echo ""
echo "=== RESOURCE USAGE ==="
AUDIT_SIZE=$(du -sm /var/log/audit/ 2>/dev/null | cut -f1)
if [[ $AUDIT_SIZE -lt 100 ]]; then
    check "Audit log size (${AUDIT_SIZE}MB)" "true"
else
    warn "Audit log size large (${AUDIT_SIZE}MB)"
fi

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   VERIFICATION COMPLETE                        ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARN warnings${NC}"
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Review output above.${NC}"
    exit 1
fi
