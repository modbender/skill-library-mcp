#!/usr/bin/env bash
# Editorial Boot Check — Fast session startup summary
# Run from AGENTS.md startup sequence

set -euo pipefail

EDITORIAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAIMS_DIR="$EDITORIAL_DIR/claims"
LEDGER_PATH="$EDITORIAL_DIR/ledger.json"
TIMELINE_PATH="$EDITORIAL_DIR/timeline.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Editorial State${NC}"
echo ""

# Active claims
if [ -d "$CLAIMS_DIR" ]; then
  CLAIM_COUNT=$(find "$CLAIMS_DIR" -maxdepth 1 -name "*.claim" -type f 2>/dev/null | wc -l)
  if [ "$CLAIM_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}🔥 Active Claims: $CLAIM_COUNT${NC}"
    find "$CLAIMS_DIR" -maxdepth 1 -name "*.claim" -type f -exec basename {} \; | sed 's/\.claim$//' | sed 's/^/   /'
    echo ""
  fi
fi

# Recent publications (last 48h)
if [ -f "$LEDGER_PATH" ]; then
  RECENT=$(node -e '
    const ledger = require("'"$LEDGER_PATH"'");
    const cutoff = Date.now() - (48 * 60 * 60 * 1000);
    const recent = ledger.filter(e => new Date(e.published_at) > cutoff);
    if (recent.length > 0) {
      console.log("📰 Recent Publications (48h):", recent.length);
      recent.slice(0, 5).forEach(e => {
        const date = e.published_at.split("T")[0];
        console.log(`   ${date} | ${e.channel} | ${e.author} | ${e.title}`);
      });
    }
  ' 2>/dev/null || true)
  
  if [ -n "$RECENT" ]; then
    echo -e "${GREEN}$RECENT${NC}"
    echo ""
  fi
fi

# Timeline gaps
if [ -f "$TIMELINE_PATH" ]; then
  TIMELINE_OUT=$(node -e '
    const timeline = require("'"$TIMELINE_PATH"'");
    const today = new Date().toISOString().split("T")[0];
    
    for (const [name, series] of Object.entries(timeline.series || {})) {
      const days = series.days || [];
      const lastDay = days[days.length - 1];
      const unpublished = days.filter(d => !d.published);
      
      if (unpublished.length > 0) {
        console.log("⚠️  Timeline Gaps in", name + ":");
        unpublished.slice(0, 3).forEach(d => {
          console.log(`   Day ${d.day} (${d.date}) — ${d.title || "Untitled"}`);
        });
      } else if (lastDay && lastDay.date === today) {
        console.log("✓ Timeline current:", name, "(Day " + lastDay.day + ")");
      }
    }
  ' 2>/dev/null || true)
  
  if [ -n "$TIMELINE_OUT" ]; then
    echo -e "${GREEN}$TIMELINE_OUT${NC}"
  fi
fi

echo ""
echo -e "${BLUE}Run 'node scripts/editorial.js status' for details${NC}"
