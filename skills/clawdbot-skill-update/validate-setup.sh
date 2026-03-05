#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Clawdbot Setup Validation${NC}"
echo -e "${BLUE}============================${NC}"
echo ""

# Check if config exists
echo -e "${YELLOW}📋 Configuration Check${NC}"
if [ -f ~/.clawdbot/clawdbot.json ]; then
  echo -e "${GREEN}✅${NC} Config file exists"
  CONFIG_SIZE=$(du -h ~/.clawdbot/clawdbot.json | cut -f1)
  echo "   Size: $CONFIG_SIZE"
else
  echo -e "${RED}❌${NC} Config file missing!"
  exit 1
fi

# Check critical config values
echo ""
echo -e "${YELLOW}🔧 Critical Config Values${NC}"

TELEGRAM_DM=$(jq -r '.telegram.dmPolicy // "not set"' ~/.clawdbot/clawdbot.json)
WHATSAPP_DM=$(jq -r '.whatsapp.dmPolicy // "not set"' ~/.clawdbot/clawdbot.json)
SANDBOX_SCOPE=$(jq -r '.agent.sandbox.scope // "not set"' ~/.clawdbot/clawdbot.json)

echo "Telegram dmPolicy:  $TELEGRAM_DM"
[ "$TELEGRAM_DM" = "pairing" ] && echo -e "${GREEN}   ✅ Secure (pairing)${NC}" || echo -e "${YELLOW}   ⚠️  Not pairing${NC}"

echo "WhatsApp dmPolicy:  $WHATSAPP_DM"
[ "$WHATSAPP_DM" = "pairing" ] && echo -e "${GREEN}   ✅ Secure (pairing)${NC}" || echo -e "${YELLOW}   ⚠️  Using: $WHATSAPP_DM${NC}"

echo "Sandbox scope:      $SANDBOX_SCOPE"
[ "$SANDBOX_SCOPE" = "agent" ] && echo -e "${GREEN}   ✅ Explicit agent scope${NC}" || echo -e "${YELLOW}   ⚠️  Using: $SANDBOX_SCOPE${NC}"

# Check workspaces
echo ""
echo -e "${YELLOW}🏠 Workspace Check${NC}"

WORKSPACES=$(jq -r '.routing.agents | to_entries[] | "\(.key):\(.value.workspace)"' ~/.clawdbot/clawdbot.json)

while IFS=: read -r agent workspace; do
  if [ -d "$workspace" ]; then
    SIZE=$(du -sh "$workspace" 2>/dev/null | cut -f1)
    echo -e "${GREEN}✅${NC} $agent: $workspace ($SIZE)"
  else
    echo -e "${RED}❌${NC} $agent: $workspace (missing!)"
  fi
done <<< "$WORKSPACES"

# Check credentials
echo ""
echo -e "${YELLOW}🔐 Credentials Check${NC}"
if [ -d ~/.clawdbot/credentials ]; then
  CRED_COUNT=$(find ~/.clawdbot/credentials -type f | wc -l | tr -d ' ')
  echo -e "${GREEN}✅${NC} Credentials directory exists ($CRED_COUNT files)"
else
  echo -e "${RED}❌${NC} Credentials directory missing!"
fi

# Check sessions
echo ""
echo -e "${YELLOW}💾 Sessions Check${NC}"
if [ -d ~/.clawdbot/sessions ]; then
  SESSION_COUNT=$(find ~/.clawdbot/sessions -type f -name "*.jsonl" 2>/dev/null | wc -l | tr -d ' ')
  echo -e "${GREEN}✅${NC} Sessions directory exists ($SESSION_COUNT session files)"
else
  echo -e "${BLUE}ℹ️${NC}  No sessions directory (normal for fresh install)"
fi

# Check agents
echo ""
echo -e "${YELLOW}🤖 Multi-Agent Setup${NC}"
if [ -d ~/.clawdbot/agents ]; then
  AGENT_DIRS=$(find ~/.clawdbot/agents -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
  echo -e "${GREEN}✅${NC} Agents directory exists ($AGENT_DIRS agents)"
  
  # List agents
  for agent_dir in ~/.clawdbot/agents/*/; do
    if [ -d "$agent_dir" ]; then
      agent_name=$(basename "$agent_dir")
      echo "   - $agent_name"
    fi
  done
else
  echo -e "${BLUE}ℹ️${NC}  No agents directory"
fi

# Check git repo
echo ""
echo -e "${YELLOW}🔧 Git Repository${NC}"
if [ -d ~/code/clawdbot/.git ]; then
  cd ~/code/clawdbot
  CURRENT_COMMIT=$(git log -1 --oneline)
  CURRENT_BRANCH=$(git branch --show-current)
  echo -e "${GREEN}✅${NC} Git repository exists"
  echo "   Branch: $CURRENT_BRANCH"
  echo "   Commit: $CURRENT_COMMIT"
  
  # Check for uncommitted changes
  if [ -n "$(git status --short)" ]; then
    echo -e "${YELLOW}   ⚠️  Uncommitted changes:${NC}"
    git status --short | head -5
  fi
else
  echo -e "${RED}❌${NC} Git repository not found!"
fi

# Check clawdbot binary
echo ""
echo -e "${YELLOW}🔨 Clawdbot Binary${NC}"
CLAWDBOT_BIN=$(which clawdbot)
if [ -n "$CLAWDBOT_BIN" ]; then
  echo -e "${GREEN}✅${NC} clawdbot found: $CLAWDBOT_BIN"
  
  if [ -L "$CLAWDBOT_BIN" ]; then
    TARGET=$(readlink "$CLAWDBOT_BIN")
    echo "   Symlink to: $TARGET"
  fi
else
  echo -e "${RED}❌${NC} clawdbot not in PATH!"
fi

# Check gateway status
echo ""
echo -e "${YELLOW}🚀 Gateway Status${NC}"
cd ~/code/clawdbot
GATEWAY_STATUS=$(pnpm clawdbot gateway status 2>&1)
if echo "$GATEWAY_STATUS" | grep -q "running"; then
  echo -e "${GREEN}✅${NC} Gateway is running"
else
  echo -e "${YELLOW}⚠️${NC}  Gateway is not running"
fi

# Check recent backups
echo ""
echo -e "${YELLOW}💾 Recent Backups${NC}"
if [ -d ~/.clawdbot-backups ]; then
  BACKUP_COUNT=$(find ~/.clawdbot-backups -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
  echo -e "${GREEN}✅${NC} Backup directory exists ($BACKUP_COUNT backups)"
  
  # Show 3 most recent
  echo "   Recent backups:"
  ls -td ~/.clawdbot-backups/*/ 2>/dev/null | head -3 | while read backup; do
    SIZE=$(du -sh "$backup" 2>/dev/null | cut -f1)
    NAME=$(basename "$backup")
    echo "   - $NAME ($SIZE)"
  done
else
  echo -e "${BLUE}ℹ️${NC}  No backups yet (run backup script first)"
fi

# Check disk space
echo ""
echo -e "${YELLOW}💿 Disk Space${NC}"
DISK_AVAIL=$(df -h ~ | tail -1 | awk '{print $4}')
echo "Available: $DISK_AVAIL"

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}📊 Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

ISSUES=0

# Config
[ ! -f ~/.clawdbot/clawdbot.json ] && ISSUES=$((ISSUES+1))

# Workspaces
while IFS=: read -r agent workspace; do
  [ ! -d "$workspace" ] && ISSUES=$((ISSUES+1))
done <<< "$WORKSPACES"

# Credentials
[ ! -d ~/.clawdbot/credentials ] && ISSUES=$((ISSUES+1))

# Git
[ ! -d ~/code/clawdbot/.git ] && ISSUES=$((ISSUES+1))

# Binary
[ -z "$CLAWDBOT_BIN" ] && ISSUES=$((ISSUES+1))

if [ $ISSUES -eq 0 ]; then
  echo -e "${GREEN}✅ All checks passed! Setup looks good.${NC}"
  echo ""
  echo -e "${BLUE}💡 Ready to update:${NC}"
  echo "   ~/.skills/clawdbot-update/backup-clawdbot-full.sh"
else
  echo -e "${YELLOW}⚠️  Found $ISSUES issue(s). Review output above.${NC}"
fi

echo ""
