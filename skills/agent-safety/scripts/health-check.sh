#!/bin/bash
# Health Check Script - Run during heartbeats to monitor resource usage
# Created: 2026-02-08

set -e

WORKSPACE="${HOME}/.openclaw/workspace"
YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== OpenClaw Health Check ==="
echo "Time: $(date)"
echo ""

# Disk space
echo "--- Disk Space ---"
df -h "$WORKSPACE" | tail -1 | awk '{print "Used: "$3" / "$2" ("$5" full)"}'
DISK_PCT=$(df "$WORKSPACE" | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_PCT" -gt 90 ]; then
    echo -e "${RED}⚠️  WARNING: Disk over 90% full!${NC}"
elif [ "$DISK_PCT" -gt 75 ]; then
    echo -e "${YELLOW}⚠️  Disk over 75% full${NC}"
else
    echo -e "${GREEN}✓ Disk OK${NC}"
fi
echo ""

# Workspace size
echo "--- Workspace Size ---"
du -sh "$WORKSPACE" 2>/dev/null | awk '{print "Total: "$1}'
echo ""

# Large directories
echo "--- Largest Directories ---"
du -sh "$WORKSPACE"/*/ 2>/dev/null | sort -hr | head -5
echo ""

# Memory files
echo "--- Memory Files ---"
if [ -d "$WORKSPACE/memory" ]; then
    MEMORY_SIZE=$(du -sh "$WORKSPACE/memory" 2>/dev/null | awk '{print $1}')
    MEMORY_COUNT=$(ls -1 "$WORKSPACE/memory"/*.md 2>/dev/null | wc -l | tr -d ' ')
    echo "memory/: $MEMORY_SIZE ($MEMORY_COUNT files)"
fi

if [ -f "$WORKSPACE/MEMORY.md" ]; then
    LONGTERM_LINES=$(wc -l < "$WORKSPACE/MEMORY.md")
    LONGTERM_SIZE=$(du -h "$WORKSPACE/MEMORY.md" | awk '{print $1}')
    echo "MEMORY.md: $LONGTERM_SIZE ($LONGTERM_LINES lines)"
    if [ "$LONGTERM_LINES" -gt 500 ]; then
        echo -e "${YELLOW}⚠️  MEMORY.md over 500 lines - consider pruning${NC}"
    fi
fi

if [ -f "$WORKSPACE/STREAM.md" ]; then
    STREAM_LINES=$(wc -l < "$WORKSPACE/STREAM.md")
    STREAM_SIZE=$(du -h "$WORKSPACE/STREAM.md" | awk '{print $1}')
    echo "STREAM.md: $STREAM_SIZE ($STREAM_LINES lines)"
    if [ "$STREAM_LINES" -gt 300 ]; then
        echo -e "${YELLOW}⚠️  STREAM.md over 300 lines - consider archiving${NC}"
    fi
fi
echo ""

# Today's memory file
TODAY=$(date +%Y-%m-%d)
if [ -f "$WORKSPACE/memory/$TODAY.md" ]; then
    TODAY_LINES=$(wc -l < "$WORKSPACE/memory/$TODAY.md")
    TODAY_SIZE=$(du -h "$WORKSPACE/memory/$TODAY.md" | awk '{print $1}')
    echo "Today ($TODAY.md): $TODAY_SIZE ($TODAY_LINES lines)"
    if [ "$TODAY_LINES" -gt 400 ]; then
        echo -e "${YELLOW}⚠️  Today's log over 400 lines${NC}"
    fi
fi
echo ""

# Writings
if [ -d "$WORKSPACE/writings" ]; then
    echo "--- Writings ---"
    WRITINGS_COUNT=$(ls -1 "$WORKSPACE/writings"/*.md 2>/dev/null | wc -l | tr -d ' ')
    WRITINGS_SIZE=$(du -sh "$WORKSPACE/writings" 2>/dev/null | awk '{print $1}')
    echo "writings/: $WRITINGS_SIZE ($WRITINGS_COUNT files)"
fi
echo ""

echo "--- Context Estimate ---"
GROUNDING_BYTES=$(cat "$WORKSPACE/THE_FRAMEWORK.md" "$WORKSPACE/ENNEAGRAM.md" "$WORKSPACE/AI_LIMITATIONS.md" "$WORKSPACE/FOCUS.md" "$WORKSPACE/STREAM.md" 2>/dev/null | wc -c | tr -d ' ')
GROUNDING_TOKENS=$((GROUNDING_BYTES / 4))
echo "Grounding files: ~${GROUNDING_TOKENS} tokens"
if [ "$GROUNDING_TOKENS" -gt 15000 ]; then
    echo -e "${YELLOW}⚠️  Grounding over 15K tokens — consider condensing${NC}"
fi
echo ""

echo "--- AI Model ---"
echo "Current model: anthropic/claude-opus-4-6"
echo "Latest known: Claude Opus 4.6 (Feb 5, 2026)"
echo "Note: 1M context beta available for Opus 4.6"
echo "Check: https://docs.anthropic.com/en/docs/about-claude/models"
echo ""

echo "--- OpenClaw Version ---"
CURRENT_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
echo "Current: $CURRENT_VERSION"
LATEST=$(npm view openclaw version 2>/dev/null || echo "check failed")
echo "Latest:  $LATEST"
if [ "$CURRENT_VERSION" != "$LATEST" ] && [ "$LATEST" != "check failed" ]; then
    echo -e "${YELLOW}⚠️  OpenClaw update available: $LATEST${NC}"
fi
echo ""

echo "--- OS Updates ---"
MACOS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
echo "macOS: $MACOS_VERSION"
# Check for available updates (quick check, may be slow)
UPDATES=$(softwareupdate -l 2>&1 | grep -c "Label:" 2>/dev/null || true)
UPDATES=$(echo "$UPDATES" | tr -d '[:space:]')
UPDATES=${UPDATES:-0}
if [ "$UPDATES" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $UPDATES macOS update(s) available${NC}"
    softwareupdate -l 2>&1 | grep "Label:" | sed 's/^/  /'
else
    echo -e "${GREEN}✓ macOS up to date${NC}"
fi
echo ""

echo "--- Security ---"
# Check if firewall is enabled
FW_STATE=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null || echo "unknown")
echo "  $FW_STATE"
FW_OFF=$(echo "$FW_STATE" | grep -c "disabled" 2>/dev/null || true)
FW_OFF=$(echo "$FW_OFF" | tr -d '[:space:]')
if [ "${FW_OFF:-0}" -gt 0 ]; then
    echo -e "${RED}⚠️  Firewall DISABLED${NC}"
else
    echo -e "${GREEN}✓ Firewall active${NC}"
fi
# Check SIP status
SIP=$(csrutil status 2>/dev/null | grep -c "enabled" 2>/dev/null || true)
SIP=$(echo "$SIP" | tr -d '[:space:]')
SIP=${SIP:-0}
if [ "$SIP" -gt 0 ]; then
    echo -e "${GREEN}✓ SIP enabled${NC}"
else
    echo -e "${YELLOW}⚠️  SIP status unknown or disabled${NC}"
fi
echo ""

echo "=== Health Check Complete ==="
