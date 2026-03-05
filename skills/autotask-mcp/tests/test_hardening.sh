#!/usr/bin/env bash
# Validation tests for the hardened autotask-mcp setup.
# Run: ./tests/test_hardening.sh
set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

check() {
  local desc="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    pass "$desc"
  else
    fail "$desc"
  fi
}

echo "=== Autotask MCP Hardening Tests ==="
echo ""

# --- docker-compose.yml checks ---
echo "[docker-compose.yml]"
check "read-only filesystem"        grep -q 'read_only: true' docker-compose.yml
check "no-new-privileges"           grep -q 'no-new-privileges:true' docker-compose.yml
check "cap_drop present"            grep -q 'cap_drop' docker-compose.yml
check "all capabilities dropped"    grep -q '\- ALL' docker-compose.yml
check "localhost-only port binding" grep -q '127.0.0.1:8080:8080' docker-compose.yml
check "memory limit set"            grep -q 'memory: 512m' docker-compose.yml
check "CPU limit set"               grep -q 'cpus:' docker-compose.yml
check "PID limit set"               grep -q 'pids_limit:' docker-compose.yml
check "tmpfs noexec flag"           grep -q 'noexec' docker-compose.yml
check "tmpfs nosuid flag"           grep -q 'nosuid' docker-compose.yml
check "log rotation configured"     grep -q 'max-size' docker-compose.yml

echo ""

# --- Script checks ---
echo "[Shell scripts]"
for script in scripts/mcp_*.sh scripts/cron_*.sh; do
  check "$script is executable"      test -x "$script"
  check "$script has proper shebang" head -1 "$script" | grep -q '#!/usr/bin/env bash'
  check "$script uses strict mode"   head -3 "$script" | grep -q 'set -.*uo pipefail'
done

echo ""

# --- Cron/scheduler checks ---
echo "[Scheduler]"
check "cron_install.sh uses LaunchAgent/systemd" grep -q 'LaunchAgent\|systemd' scripts/cron_install.sh
check "cron_install.sh requires user confirmation" grep -q 'read -rp' scripts/cron_install.sh
check "cron_uninstall.sh cleans up legacy crontab" grep -q 'autotask-mcp' scripts/cron_uninstall.sh

echo ""

# --- Supply chain checks ---
echo "[Supply chain]"
check "mcp_update.sh supports digest pinning"          grep -q '.pinned-digest' scripts/mcp_update.sh
check "mcp_update.sh refuses restart on mismatch"      grep -q 'Refusing to restart' scripts/mcp_update.sh
check "mcp_pin_digest.sh exists"                        test -f scripts/mcp_pin_digest.sh
check "mcp_pin_digest.sh requires user confirmation"    grep -q 'read -rp' scripts/mcp_pin_digest.sh

echo ""

# --- Gitignore checks ---
echo "[.gitignore]"
check ".env is gitignored"            grep -q '.env' .gitignore
check ".pinned-digest is gitignored"  grep -q '.pinned-digest' .gitignore
check "logs/ is gitignored"           grep -q 'logs/' .gitignore

echo ""

# --- SKILL.md security rules ---
echo "[SKILL.md agent guardrails]"
check "credential read prohibition"        grep -q 'NEVER read' SKILL.md
check "credential CLI prohibition"         grep -q 'NEVER pass credentials' SKILL.md
check "credential exfiltration prohibition" grep -q 'NEVER transmit credentials' SKILL.md
check "pin_digest in allowed commands"     grep -q 'mcp_pin_digest.sh' SKILL.md

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
