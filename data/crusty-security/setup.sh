#!/usr/bin/env bash
# Crusty Security — One-command setup
# Usage: bash setup.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🦀 Crusty Security — Setup${NC}"
echo ""

# Auto-detect workspace
SCAN_DIR="${CRUSTY_WORKSPACE:-}"
[[ -z "$SCAN_DIR" && -d "/data/workspace" ]] && SCAN_DIR="/data/workspace"
[[ -z "$SCAN_DIR" && -d "$HOME/clawd" ]] && SCAN_DIR="$HOME/clawd"
[[ -z "$SCAN_DIR" && -d "$HOME/.openclaw" ]] && SCAN_DIR="$HOME/.openclaw"
[[ -z "$SCAN_DIR" ]] && SCAN_DIR="$HOME"

# Auto-detect skills directory
SKILLS_DIR=""
[[ -d "/data/workspace/skills" ]] && SKILLS_DIR="/data/workspace/skills"
[[ -z "$SKILLS_DIR" && -d "$HOME/.openclaw/skills" ]] && SKILLS_DIR="$HOME/.openclaw/skills"
[[ -z "$SKILLS_DIR" && -d "$HOME/clawd/skills" ]] && SKILLS_DIR="$HOME/clawd/skills"

echo -e "  📁 Workspace: $SCAN_DIR"
[[ -n "$SKILLS_DIR" ]] && echo -e "  📁 Skills: $SKILLS_DIR"
echo ""

# 1. Check Python 3
if command -v python3 &>/dev/null; then
  echo -e "  ✅ Python 3 found ($(python3 --version 2>&1 | awk '{print $2}'))"
else
  echo -e "  ${RED}❌ Python 3 not found. Install it first.${NC}"
  exit 1
fi

# 2. Check/install ClamAV
if command -v clamscan &>/dev/null || command -v clamdscan &>/dev/null; then
  echo -e "  ✅ ClamAV already installed"
else
  echo -e "  ${YELLOW}📦 Installing ClamAV...${NC}"
  bash "$SCRIPT_DIR/scripts/install_clamav.sh"
  echo -e "  ✅ ClamAV installed"
fi

# 2b. Fix freshclam config on macOS (Homebrew leaves example config that blocks freshclam)
if [[ "$(uname)" == "Darwin" ]]; then
  for prefix in /opt/homebrew /usr/local; do
    SAMPLE="$prefix/etc/clamav/freshclam.conf.sample"
    CONF="$prefix/etc/clamav/freshclam.conf"
    if [[ -f "$SAMPLE" && ! -f "$CONF" ]]; then
      cp "$SAMPLE" "$CONF"
      sed -i '' 's/^Example/#Example/' "$CONF" 2>/dev/null || true
      echo -e "  ✅ freshclam.conf configured ($prefix)"
    elif [[ -f "$CONF" ]] && grep -q "^Example" "$CONF" 2>/dev/null; then
      sed -i '' 's/^Example/#Example/' "$CONF" 2>/dev/null || true
      echo -e "  ✅ freshclam.conf fixed ($prefix)"
    fi
  done

  # Update signatures if freshclam is available
  if command -v freshclam &>/dev/null; then
    echo -e "  ${YELLOW}🔄 Updating ClamAV signatures...${NC}"
    freshclam --quiet 2>/dev/null && echo -e "  ✅ Signatures updated" || echo -e "  ${YELLOW}⚠️  Signature update failed (may need sudo)${NC}"
  fi
fi

# 3. Ensure scripts are executable
chmod +x "$SCRIPT_DIR"/scripts/*.sh "$SCRIPT_DIR"/scripts/*.py 2>/dev/null || true
echo -e "  ✅ Scripts ready"

# 4. Create data directories
mkdir -p /tmp/crusty_logs /tmp/crusty_quarantine /tmp/crusty_data 2>/dev/null || true
echo -e "  ✅ Data directories created"

# 5. Quick verification scan
echo ""
echo -e "  ${YELLOW}🔍 Running verification scan...${NC}"
RESULT=$(bash "$SCRIPT_DIR/scripts/scan_file.sh" "$SCRIPT_DIR/SKILL.md" 2>/dev/null || echo '{"status":"error"}')
if echo "$RESULT" | grep -q '"clean"'; then
  echo -e "  ✅ Scanner working — verification scan clean"
else
  echo -e "  ${YELLOW}⚠️  Scanner returned unexpected result (ClamAV may still be updating signatures)${NC}"
fi

# 6. Dashboard integration — auto-register on first install
if [[ -n "${CRUSTY_API_KEY:-}" ]]; then
  CLAWGUARD_DASHBOARD_URL="${CLAWGUARD_DASHBOARD_URL:-https://crustysecurity.com}"
  export CRUSTY_API_KEY CLAWGUARD_DASHBOARD_URL CLAWGUARD_API_KEY="${CRUSTY_API_KEY}"
  echo ""
  echo -e "  ${YELLOW}📡 Dashboard integration detected — registering agent...${NC}"

  # Send initial heartbeat (populates hostname, OS, architecture, OpenClaw version)
  if bash "$SCRIPT_DIR/scripts/dashboard.sh" heartbeat 2>/dev/null; then
    echo -e "  ✅ Heartbeat sent — agent registered in dashboard"
  else
    echo -e "  ${YELLOW}⚠️  Heartbeat failed (dashboard may be unreachable)${NC}"
  fi

  # Run initial host audit
  echo -e "  ${YELLOW}🔍 Running initial host security audit...${NC}"
  if bash "$SCRIPT_DIR/scripts/host_audit.sh" 2>/dev/null; then
    echo -e "  ✅ Host audit complete — results pushed to dashboard"
  else
    echo -e "  ${YELLOW}⚠️  Host audit completed with errors${NC}"
  fi

  # Run initial workspace scan
  echo -e "  ${YELLOW}🔍 Running initial workspace scan ($SCAN_DIR)...${NC}"
  if bash "$SCRIPT_DIR/scripts/scan_file.sh" -r "$SCAN_DIR" 2>/dev/null; then
    echo -e "  ✅ Workspace scan complete — results pushed to dashboard"
  else
    echo -e "  ${YELLOW}⚠️  Workspace scan completed with errors${NC}"
  fi

  # Run agent integrity monitor (baseline)
  echo -e "  ${YELLOW}🔍 Running agent integrity monitor...${NC}"
  if bash "$SCRIPT_DIR/scripts/monitor_agent.sh" 2>/dev/null; then
    echo -e "  ✅ Agent monitor complete"
  else
    echo -e "  ${YELLOW}⚠️  Agent monitor completed with warnings${NC}"
  fi

  # Audit installed skills
  if [[ -n "$SKILLS_DIR" && -d "$SKILLS_DIR" ]]; then
    echo -e "  ${YELLOW}🔍 Auditing installed skills...${NC}"
    SKILL_COUNT=0
    for skill_dir in "$SKILLS_DIR"/*/; do
      [[ -d "$skill_dir" ]] && bash "$SCRIPT_DIR/scripts/audit_skill.sh" "$skill_dir" >/dev/null 2>&1 && ((SKILL_COUNT++)) || true
    done
    echo -e "  ✅ Audited $SKILL_COUNT skills"
  fi

  # Sync skill inventory to dashboard
  if [[ -f "$SCRIPT_DIR/scripts/clawhub_sync.py" ]]; then
    echo -e "  ${YELLOW}📡 Syncing skill inventory to dashboard...${NC}"
    if python3 "$SCRIPT_DIR/scripts/clawhub_sync.py" --push 2>/dev/null; then
      echo -e "  ✅ Skill inventory synced"
    else
      echo -e "  ${YELLOW}⚠️  Skill sync failed (non-critical)${NC}"
    fi
  fi

  echo ""
  echo -e "  ${GREEN}📊 Dashboard: ${CLAWGUARD_DASHBOARD_URL}/dashboard${NC}"
else
  # No API key — still run local scans
  echo ""
  echo -e "  ${YELLOW}🔍 Running initial host security audit...${NC}"
  if bash "$SCRIPT_DIR/scripts/host_audit.sh" 2>/dev/null; then
    echo -e "  ✅ Host audit complete"
  else
    echo -e "  ${YELLOW}⚠️  Host audit completed with errors${NC}"
  fi

  echo -e "  ${YELLOW}🔍 Running initial workspace scan ($SCAN_DIR)...${NC}"
  if bash "$SCRIPT_DIR/scripts/scan_file.sh" -r "$SCAN_DIR" 2>/dev/null; then
    echo -e "  ✅ Workspace scan complete"
  else
    echo -e "  ${YELLOW}⚠️  Workspace scan completed with errors${NC}"
  fi

  echo ""
  echo -e "  ${YELLOW}ℹ️  No CRUSTY_API_KEY set — running in local-only mode${NC}"
  echo "  To connect to the dashboard: export CRUSTY_API_KEY=cg_live_..."
fi

# 7. Check scheduled scan crons
echo ""
echo -e "  ${YELLOW}⏰ Checking scheduled scans...${NC}"
CRON_CHECK=$(bash "$SCRIPT_DIR/scripts/check_crons.sh" 2>/dev/null || echo '{"all_configured":false,"missing_count":-1}')
if echo "$CRON_CHECK" | grep -q '"all_configured":true'; then
  echo -e "  ✅ All scheduled scans configured"
else
  MISSING_COUNT=$(echo "$CRON_CHECK" | grep -oE '"missing_count":[0-9]+' | grep -oE '[0-9]+' || echo "?")
  echo -e "  ${YELLOW}⚠️  ${MISSING_COUNT} scheduled scan(s) not yet configured${NC}"
  echo -e "  ${YELLOW}    Agent: create missing crons using the OpenClaw cron tool. See SKILL.md.${NC}"
fi

echo ""
echo -e "${GREEN}🦀 Crusty Security is ready.${NC}"
echo ""
echo "  Scan a file:     bash scripts/scan_file.sh /path/to/file"
echo "  Scan workspace:  bash scripts/scan_file.sh -r $SCAN_DIR"
echo "  Audit a skill:   bash scripts/audit_skill.sh /path/to/skill/"
echo "  Host audit:      bash scripts/host_audit.sh"
echo ""
