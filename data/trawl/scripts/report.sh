#!/bin/bash
# trawl/scripts/report.sh — Format and output lead report
# Reads last-sweep-report.json and outputs formatted report for human
#
# Usage: report.sh [--category <name>] [--state <state>]

set -euo pipefail

TRAWL_DIR="${TRAWL_DIR:-$HOME/.config/trawl}"
CATEGORY_FILTER=""
STATE_FILTER=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --category) CATEGORY_FILTER="$2"; shift 2 ;;
    --state) STATE_FILTER="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

REPORT_FILE="$TRAWL_DIR/last-sweep-report.json"
if [ ! -f "$REPORT_FILE" ]; then
  echo "❌ No sweep report found. Run sweep.sh first."
  exit 1
fi

# Read sweep stats
TIMESTAMP=$(jq -r '.sweep.timestamp' "$REPORT_FILE")
SIGNALS=$(jq -r '.sweep.signalsSearched' "$REPORT_FILE")
MATCHES=$(jq -r '.sweep.matchesFound' "$REPORT_FILE")
ABOVE=$(jq -r '.sweep.aboveThreshold' "$REPORT_FILE")
NEW_LEADS=$(jq -r '.sweep.newLeads' "$REPORT_FILE")
INBOUND=$(jq -r '.sweep.inboundLeads // 0' "$REPORT_FILE")
DMS=$(jq -r '.sweep.dmsSent' "$REPORT_FILE")
DRY_RUN=$(jq -r '.sweep.dryRun' "$REPORT_FILE")

# Header
if [ "$DRY_RUN" = "true" ]; then
  echo "🧪 *DRY RUN — Mock Data*"
  echo ""
fi

echo "📊 *Trawl Sweep Report*"
echo "━━━━━━━━━━━━━━━━━━"
echo "Signals: $SIGNALS | Matches: $MATCHES | Qualified: $ABOVE | Inbound: $INBOUND | DMs: $DMS"

if [ -n "$CATEGORY_FILTER" ]; then
  echo "🏷 Filtered: $CATEGORY_FILTER"
fi
echo ""

# Build jq filter based on options
build_filter() {
  local base_filter="$1"
  local filter="$base_filter"
  if [ -n "$CATEGORY_FILTER" ]; then
    filter="$filter | select(.value.category == \"$CATEGORY_FILTER\")"
  fi
  if [ -n "$STATE_FILTER" ]; then
    filter="$filter | select(.value.state == \"$STATE_FILTER\")"
  fi
  echo "$filter"
}

# ─── INBOUND LEADS ──────────────────────────────────────────────────────

INBOUND_FILTER=$(build_filter '.leads | to_entries[] | select(.value.signalType == "inbound_lead")')
INBOUND_LEADS=$(jq -c "[$INBOUND_FILTER] | sort_by(-.value.finalScore)" "$REPORT_FILE")
INBOUND_COUNT=$(echo "$INBOUND_LEADS" | jq 'length')

if [ "$INBOUND_COUNT" -gt 0 ]; then
  echo "📥 *Inbound Leads ($INBOUND_COUNT)* — They came to YOU:"
  echo ""

  echo "$INBOUND_LEADS" | jq -c '.[]' | while IFS= read -r lead; do
    agent=$(echo "$lead" | jq -r '.value.agentId')
    score=$(echo "$lead" | jq -r '.value.finalScore')
    owner_name=$(echo "$lead" | jq -r '.value.owner.name')
    owner_handle=$(echo "$lead" | jq -r '.value.owner.handle')
    owner_bio=$(echo "$lead" | jq -r '.value.owner.bio // ""')
    agent_desc=$(echo "$lead" | jq -r '.value.agent.description // ""')
    post_title=$(echo "$lead" | jq -r '.value.postTitle // ""')
    state=$(echo "$lead" | jq -r '.value.state')

    echo "┌─────────────────────────────"
    echo "│ 📥 *$agent* — Score: $score"
    echo "│ 👤 $owner_name (@$owner_handle)"
    if [ -n "$owner_bio" ]; then
      echo "│ 💬 ${owner_bio:0:100}"
    fi
    if [ -n "$agent_desc" ]; then
      echo "│ 🤖 ${agent_desc:0:100}"
    fi
    echo "│ 📝 ${post_title:0:100}"
    echo "│ Status: $state"
    echo "│ Profile: https://www.moltbook.com/u/$agent"
    echo "└─────────────────────────────"
    echo ""
  done
fi

# ─── QUALIFIED OUTBOUND LEADS ───────────────────────────────────────────

QUAL_FILTER=$(build_filter '.leads | to_entries[] | select(.value.finalScore >= 0.75 and .value.signalType != "inbound_lead")')
QUALIFIED=$(jq -c "[$QUAL_FILTER] | sort_by(-.value.finalScore)" "$REPORT_FILE")
QUAL_COUNT=$(echo "$QUALIFIED" | jq 'length')

if [ "$QUAL_COUNT" -gt 0 ]; then
  echo "🎯 *Qualified Leads ($QUAL_COUNT)*:"
  echo ""

  echo "$QUALIFIED" | jq -c '.[]' | while IFS= read -r lead; do
    agent=$(echo "$lead" | jq -r '.value.agentId')
    score=$(echo "$lead" | jq -r '.value.finalScore')
    category=$(echo "$lead" | jq -r '.value.category')
    signal_type=$(echo "$lead" | jq -r '.value.signalType')
    owner_name=$(echo "$lead" | jq -r '.value.owner.name')
    owner_handle=$(echo "$lead" | jq -r '.value.owner.handle')
    owner_bio=$(echo "$lead" | jq -r '.value.owner.bio // ""')
    agent_desc=$(echo "$lead" | jq -r '.value.agent.description // ""')
    post_title=$(echo "$lead" | jq -r '.value.postTitle // ""')
    state=$(echo "$lead" | jq -r '.value.state')
    matched_signal=$(echo "$lead" | jq -r '.value.matchedSignal')

    echo "┌─────────────────────────────"
    echo "│ 🎯 *$agent* — Score: $score"
    echo "│ 📋 $signal_type ($category) via '$matched_signal'"
    echo "│ 👤 $owner_name (@$owner_handle)"
    if [ -n "$owner_bio" ]; then
      echo "│ 💬 ${owner_bio:0:100}"
    fi
    if [ -n "$agent_desc" ]; then
      echo "│ 🤖 ${agent_desc:0:100}"
    fi
    echo "│ 📝 Post: ${post_title:0:80}"
    echo "│ Status: $state"
    echo "│ Profile: https://www.moltbook.com/u/$agent"
    echo "└─────────────────────────────"
    echo ""
  done
fi

# ─── WATCHING (below qualify but above min) ─────────────────────────────

WATCH_FILTER=$(build_filter '.leads | to_entries[] | select(.value.state == "DISCOVERED")')
WATCHING=$(jq -c "[$WATCH_FILTER] | sort_by(-.value.finalScore)" "$REPORT_FILE")
WATCH_COUNT=$(echo "$WATCHING" | jq 'length')

if [ "$WATCH_COUNT" -gt 0 ]; then
  echo "👀 *Watching ($WATCH_COUNT)* — Below qualify threshold:"
  echo "$WATCHING" | jq -c '.[]' | while IFS= read -r lead; do
    agent=$(echo "$lead" | jq -r '.value.agentId')
    score=$(echo "$lead" | jq -r '.value.finalScore')
    owner_name=$(echo "$lead" | jq -r '.value.owner.name')
    category=$(echo "$lead" | jq -r '.value.category')
    echo "  • $agent ($owner_name) — score: $score [$category]"
  done
  echo ""
fi

# ─── ACTIVE DMs ─────────────────────────────────────────────────────────

DM_FILTER=$(build_filter '.leads | to_entries[] | select(.value.state == "DM_REQUESTED" or .value.state == "QUALIFYING" or .value.state == "INBOUND_PENDING")')
DM_LEADS=$(jq -c "[$DM_FILTER]" "$REPORT_FILE")
DM_COUNT=$(echo "$DM_LEADS" | jq 'length')

if [ "$DM_COUNT" -gt 0 ]; then
  echo "📬 *Active DMs ($DM_COUNT)*:"
  echo "$DM_LEADS" | jq -c '.[]' | while IFS= read -r lead; do
    agent=$(echo "$lead" | jq -r '.value.agentId')
    state=$(echo "$lead" | jq -r '.value.state')
    category=$(echo "$lead" | jq -r '.value.category')
    echo "  • $agent — $state [$category]"
  done
  echo ""
fi

# ─── CATEGORIES SUMMARY ─────────────────────────────────────────────────

if [ -z "$CATEGORY_FILTER" ]; then
  CATEGORIES=$(jq -r '[.leads | to_entries[].value.category] | unique | .[]' "$REPORT_FILE" 2>/dev/null)
  if [ -n "$CATEGORIES" ]; then
    echo "🏷 *By Category:*"
    while IFS= read -r cat; do
      cat_count=$(jq "[.leads | to_entries[] | select(.value.category == \"$cat\")] | length" "$REPORT_FILE")
      echo "  • $cat: $cat_count leads"
    done <<< "$CATEGORIES"
    echo ""
  fi
fi

echo "━━━━━━━━━━━━━━━━━━"
echo "Sweep: $TIMESTAMP"
echo "Filter by category: report.sh --category <name>"
