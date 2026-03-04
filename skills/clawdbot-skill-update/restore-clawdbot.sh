#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Clawdbot Restore Script${NC}"
echo -e "${BLUE}===========================${NC}"
echo ""

# Check if backup directory is provided
if [ -z "$1" ]; then
  echo -e "${YELLOW}📁 Available backups:${NC}"
  if [ -d ~/.clawdbot-backups ]; then
    ls -lth ~/.clawdbot-backups/ | grep "^d" | head -5
  else
    echo "  No backups found"
  fi
  echo ""
  echo -e "${RED}Usage: $0 <backup-directory>${NC}"
  echo -e "${YELLOW}Example: $0 ~/.clawdbot-backups/pre-update-20260108-094500${NC}"
  exit 1
fi

BACKUP_DIR="$1"

# Validate backup directory
if [ ! -d "$BACKUP_DIR" ]; then
  echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
  exit 1
fi

echo -e "${GREEN}📁 Restoring from: $BACKUP_DIR${NC}"
echo ""

# Show backup info
if [ -f "$BACKUP_DIR/BACKUP_INFO.txt" ]; then
  echo -e "${BLUE}📋 Backup Info:${NC}"
  head -20 "$BACKUP_DIR/BACKUP_INFO.txt"
  echo ""
fi

# Check if backed up config exists
if [ ! -f "$BACKUP_DIR/clawdbot.json" ]; then
  echo -e "${RED}❌ Invalid backup: clawdbot.json not found!${NC}"
  exit 1
fi

# Confirmation
echo -e "${YELLOW}⚠️  WARNING: This will overwrite current configuration and workspaces!${NC}"
echo -e "${YELLOW}Press ENTER to continue or Ctrl+C to cancel...${NC}"
read -r

# Stop Gateway
echo ""
echo -e "${YELLOW}🛑 Stopping gateway...${NC}"
if [ -d ~/code/clawdbot ]; then
  cd ~/code/clawdbot
  pnpm clawdbot gateway stop 2>/dev/null || echo "Gateway already stopped"
  sleep 2
else
  echo -e "${YELLOW}⚠️  Clawdbot repo not found, skipping gateway stop${NC}"
fi

# Restore Config
echo ""
echo -e "${YELLOW}📋 Restoring config...${NC}"
cp "$BACKUP_DIR/clawdbot.json" ~/.clawdbot/clawdbot.json
echo -e "${GREEN}✅ Config restored${NC}"

# Restore Sessions
echo ""
echo -e "${YELLOW}💾 Restoring sessions...${NC}"
if [ -f "$BACKUP_DIR/sessions.tar.gz" ]; then
  rm -rf ~/.clawdbot/sessions
  tar -xzf "$BACKUP_DIR/sessions.tar.gz" -C ~/.clawdbot
  echo -e "${GREEN}✅ Sessions restored${NC}"
else
  echo -e "${BLUE}ℹ️  No sessions backup${NC}"
fi

# Restore Agents
echo ""
echo -e "${YELLOW}🤖 Restoring agents...${NC}"
if [ -f "$BACKUP_DIR/agents.tar.gz" ]; then
  rm -rf ~/.clawdbot/agents
  tar -xzf "$BACKUP_DIR/agents.tar.gz" -C ~/.clawdbot
  echo -e "${GREEN}✅ Agents restored${NC}"
else
  echo -e "${BLUE}ℹ️  No agents backup${NC}"
fi

# Restore Credentials
echo ""
echo -e "${YELLOW}🔐 Restoring credentials...${NC}"
if [ -f "$BACKUP_DIR/credentials.tar.gz" ]; then
  rm -rf ~/.clawdbot/credentials
  tar -xzf "$BACKUP_DIR/credentials.tar.gz" -C ~/.clawdbot
  echo -e "${GREEN}✅ Credentials restored${NC}"
else
  echo -e "${YELLOW}⚠️  No credentials backup${NC}"
fi

# Restore Cron
echo ""
echo -e "${YELLOW}⏰ Restoring cron...${NC}"
if [ -f "$BACKUP_DIR/cron.tar.gz" ]; then
  rm -rf ~/.clawdbot/cron
  tar -xzf "$BACKUP_DIR/cron.tar.gz" -C ~/.clawdbot
  echo -e "${GREEN}✅ Cron restored${NC}"
else
  echo -e "${BLUE}ℹ️  No cron backup${NC}"
fi

# Restore Sandboxes
echo ""
echo -e "${YELLOW}📦 Restoring sandboxes...${NC}"
if [ -f "$BACKUP_DIR/sandboxes.tar.gz" ]; then
  rm -rf ~/.clawdbot/sandboxes
  tar -xzf "$BACKUP_DIR/sandboxes.tar.gz" -C ~/.clawdbot
  echo -e "${GREEN}✅ Sandboxes restored${NC}"
else
  echo -e "${BLUE}ℹ️  No sandboxes backup${NC}"
fi

# Restore Workspaces (DYNAMIC!)
echo ""
echo -e "${YELLOW}🏠 Restoring workspaces (reading from restored config)...${NC}"

# Read workspaces from restored config
WORKSPACE_DATA=$(jq -r '.routing.agents // {} | to_entries[] | "\(.key)|\(.value.workspace // "none")|\(.value.name // .key)"' ~/.clawdbot/clawdbot.json)

if [ -z "$WORKSPACE_DATA" ]; then
  echo -e "${BLUE}ℹ️  No agents configured${NC}"
else
  RESTORED_COUNT=0
  
  while IFS='|' read -r agent_id workspace agent_name; do
    if [ "$workspace" != "none" ]; then
      SAFE_NAME=$(echo "$agent_id" | tr '/' '_' | tr ' ' '-')
      BACKUP_FILE="$BACKUP_DIR/workspace-${SAFE_NAME}.tar.gz"
      
      if [ -f "$BACKUP_FILE" ]; then
        echo -e "  📦 Restoring ${BLUE}$agent_id${NC} ($agent_name)..."
        echo "     Path: $workspace"
        
        # Create workspace directory if it doesn't exist
        mkdir -p "$workspace"
        
        # Extract backup
        tar -xzf "$BACKUP_FILE" -C "$workspace"
        
        SIZE=$(du -sh "$workspace" 2>/dev/null | cut -f1)
        echo -e "     ${GREEN}✅ Restored ($SIZE)${NC}"
        
        RESTORED_COUNT=$((RESTORED_COUNT+1))
      else
        echo -e "  ${YELLOW}⚠️${NC}  No backup found for '$agent_id' (expected: $BACKUP_FILE)"
      fi
    fi
  done <<< "$WORKSPACE_DATA"
  
  echo ""
  echo -e "${GREEN}✅ Restored $RESTORED_COUNT workspace(s)${NC}"
fi

# Restore Git (optional)
echo ""
echo -e "${YELLOW}🔧 Git restore...${NC}"
if [ -f "$BACKUP_DIR/git-version.txt" ]; then
  GIT_COMMIT=$(head -1 "$BACKUP_DIR/git-version.txt" | awk '{print $1}')
  echo "Backup was from: $GIT_COMMIT"
  echo -e "${YELLOW}Restore git to this version? (y/N)${NC}"
  read -r response
  if [[ "$response" =~ ^[Yy]$ ]]; then
    if [ -d ~/code/clawdbot ]; then
      cd ~/code/clawdbot
      git checkout "$GIT_COMMIT"
      pnpm install
      pnpm build
      echo -e "${GREEN}✅ Git restored to $GIT_COMMIT${NC}"
    else
      echo -e "${RED}❌ Git repository not found${NC}"
    fi
  else
    echo -e "${BLUE}ℹ️  Keeping current git version${NC}"
  fi
fi

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Restore Complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📊 Restored Components:${NC}"
[ -f ~/.clawdbot/clawdbot.json ] && echo -e "${GREEN}✅${NC} Configuration"
[ -d ~/.clawdbot/sessions ] && echo -e "${GREEN}✅${NC} Sessions"
[ -d ~/.clawdbot/agents ] && echo -e "${GREEN}✅${NC} Agents"
[ -d ~/.clawdbot/credentials ] && echo -e "${GREEN}✅${NC} Credentials"
[ -d ~/.clawdbot/cron ] && echo -e "${GREEN}✅${NC} Cron jobs"
[ -d ~/.clawdbot/sandboxes ] && echo -e "${GREEN}✅${NC} Sandboxes"

# Count restored workspaces
if [ -n "$WORKSPACE_DATA" ]; then
  while IFS='|' read -r agent_id workspace agent_name; do
    if [ "$workspace" != "none" ] && [ -d "$workspace" ]; then
      SIZE=$(du -sh "$workspace" 2>/dev/null | cut -f1)
      echo -e "${GREEN}✅${NC} Workspace: $agent_id ($SIZE)"
    fi
  done <<< "$WORKSPACE_DATA"
fi

echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Verify config: jq '.' ~/.clawdbot/clawdbot.json | less"
echo "2. Validate setup: ~/.skills/clawdbot-update/validate-setup.sh"
echo "3. Start gateway: cd ~/code/clawdbot && pnpm clawdbot gateway start"
echo "4. Check status: pnpm clawdbot gateway status"
echo ""
