#!/usr/bin/env bash
# ============================================================
# scripts/v5/trend-analyzer.sh — Weekly Trend Analysis
#
# Compares the last N weeks of analysis results to detect:
#   - Emerging patterns (this week >> 4-week average)
#   - Resolved patterns (this week << 4-week average)
#   - Stable patterns (within normal range)
#
# Usage:
#   trend-analyzer.sh [--weeks 4] [--output output.json]
#
# Environment:
#   PROPOSALS_DIR       Proposals directory (default: data/proposals)
#   TRENDS_OUTPUT       Output file path
#   LOOKBACK_WEEKS      Weeks to look back (default: 4)
#   EMERGING_MULT       Emerging multiplier (default: 2.0 = 200% of avg)
#   RESOLVED_THRESH     Resolved threshold (default: 0.2 = 20% of avg)
#   SEA_TMP_DIR         Temp directory
#
# SECURITY MANIFEST:
#   - Reads: $PROPOSALS_DIR/*.json, data/benchmarks/*.json
#   - Writes: $TRENDS_OUTPUT
#   - Network: None
#   - Exec: None
# ============================================================
# shellcheck shell=bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SKILL_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# ── Configuration ──────────────────────────────────────────
PROPOSALS_DIR="${PROPOSALS_DIR:-$SKILL_DIR/data/proposals}"
TRENDS_OUTPUT="${TRENDS_OUTPUT:-${SEA_TMP_DIR:-/tmp/sea-v5}/trends-result.json}"
LOOKBACK_WEEKS="${LOOKBACK_WEEKS:-4}"
EMERGING_MULT="${EMERGING_MULT:-2.0}"
RESOLVED_THRESH="${RESOLVED_THRESH:-0.2}"
SEA_TMP="${SEA_TMP_DIR:-/tmp/sea-v5}"

# Parse CLI flags
for arg in "$@"; do
  case "$arg" in
    --weeks=*) LOOKBACK_WEEKS="${arg#--weeks=}" ;;
    --output=*) TRENDS_OUTPUT="${arg#--output=}" ;;
  esac
done

mkdir -p "$(dirname "$TRENDS_OUTPUT")" "$SEA_TMP" 2>/dev/null || true

log() { echo "[SEA-v5 trends] $*" >&2; }

main() {
  log "Trend analysis starting"
  log "PROPOSALS_DIR: $PROPOSALS_DIR"
  log "Lookback: $LOOKBACK_WEEKS weeks"
  log "Emerging threshold: ${EMERGING_MULT}x average"
  log "Resolved threshold: ${RESOLVED_THRESH}x average"

  # Run trend analysis in Python
  python3 - \
    "$PROPOSALS_DIR" \
    "$TRENDS_OUTPUT" \
    "$LOOKBACK_WEEKS" \
    "$EMERGING_MULT" \
    "$RESOLVED_THRESH" << 'PYEOF' 2>/dev/null || true
import json, sys, os, re
from pathlib import Path
from datetime import datetime, timedelta

proposals_dir   = Path(sys.argv[1])
output_file     = sys.argv[2]
lookback_weeks  = int(sys.argv[3])
emerging_mult   = float(sys.argv[4])
resolved_thresh = float(sys.argv[5])

def load_proposals(directory):
    """Load all proposal JSON files from a directory."""
    proposals = []
    if not directory.exists():
        return proposals
    for f in sorted(directory.glob("*.json")):
        try:
            with open(f) as fh:
                data = json.load(fh)
                # Handle both single proposals and arrays
                if isinstance(data, list):
                    proposals.extend(data)
                elif isinstance(data, dict):
                    proposals.append(data)
        except Exception:
            continue
    return proposals

proposals = load_proposals(proposals_dir)
print(f"[SEA-v5 trends] Loaded {len(proposals)} proposals", file=sys.stderr)

# Group proposals by week
now = datetime.utcnow()
weeks = []
for i in range(lookback_weeks):
    week_end   = now - timedelta(weeks=i)
    week_start = week_end - timedelta(weeks=1)
    week_proposals = []
    for p in proposals:
        created = p.get('created_at', p.get('timestamp', ''))
        if not created:
            continue
        try:
            # Parse date (accept YYYY-MM-DD or ISO format)
            if 'T' in str(created):
                dt = datetime.fromisoformat(str(created).replace('Z', '+00:00'))
                dt = dt.replace(tzinfo=None)
            else:
                dt = datetime.strptime(str(created)[:10], '%Y-%m-%d')
            if week_start <= dt < week_end:
                week_proposals.append(p)
        except Exception:
            continue
    weeks.append({
        "week": i,
        "start": week_start.strftime('%Y-%m-%d'),
        "end": week_end.strftime('%Y-%m-%d'),
        "proposals": week_proposals,
        "count": len(week_proposals),
        "avg_quality": (
            sum(p.get('quality_score', 5) for p in week_proposals) / len(week_proposals)
            if week_proposals else 0.0
        ),
        "frustration_count": sum(p.get('frustration_count', 0) for p in week_proposals),
        "exec_retry_count": sum(p.get('exec_retries', 0) for p in week_proposals),
    })

# Latest week vs average of older weeks
latest = weeks[0] if weeks else {}
older  = weeks[1:] if len(weeks) > 1 else []

avg_frustration = (
    sum(w['frustration_count'] for w in older) / len(older)
    if older else 0.0
)
avg_exec_retry = (
    sum(w['exec_retry_count'] for w in older) / len(older)
    if older else 0.0
)
avg_proposals = (
    sum(w['count'] for w in older) / len(older)
    if older else 0.0
)

# Classify trends
trends = {}

# Frustration trend
latest_frust = latest.get('frustration_count', 0)
if avg_frustration > 0:
    if latest_frust > avg_frustration * emerging_mult:
        trends['frustration'] = {
            'status': 'emerging',
            'current': latest_frust,
            'average': round(avg_frustration, 2),
            'ratio': round(latest_frust / avg_frustration, 2),
            'description': f'Frustration signals INCREASING ({latest_frust} vs avg {avg_frustration:.1f})'
        }
    elif latest_frust < avg_frustration * resolved_thresh:
        trends['frustration'] = {
            'status': 'resolved',
            'current': latest_frust,
            'average': round(avg_frustration, 2),
            'ratio': round(latest_frust / avg_frustration, 2),
            'description': f'Frustration signals RESOLVED ({latest_frust} vs avg {avg_frustration:.1f})'
        }
    else:
        trends['frustration'] = {
            'status': 'stable',
            'current': latest_frust,
            'average': round(avg_frustration, 2),
            'ratio': round(latest_frust / avg_frustration, 2) if avg_frustration > 0 else 1.0,
            'description': 'Frustration signals stable'
        }
else:
    trends['frustration'] = {
        'status': 'no_baseline',
        'current': latest_frust,
        'description': 'Not enough history for trend (need 2+ weeks)'
    }

# Exec retry trend
latest_exec = latest.get('exec_retry_count', 0)
if avg_exec_retry > 0:
    if latest_exec > avg_exec_retry * emerging_mult:
        trends['exec_retry'] = {
            'status': 'emerging',
            'current': latest_exec,
            'average': round(avg_exec_retry, 2),
            'description': f'Exec retries INCREASING ({latest_exec} vs avg {avg_exec_retry:.1f})'
        }
    elif latest_exec < avg_exec_retry * resolved_thresh:
        trends['exec_retry'] = {
            'status': 'resolved',
            'current': latest_exec,
            'average': round(avg_exec_retry, 2),
            'description': f'Exec retries RESOLVED ({latest_exec} vs avg {avg_exec_retry:.1f})'
        }
    else:
        trends['exec_retry'] = {
            'status': 'stable',
            'current': latest_exec,
            'average': round(avg_exec_retry, 2),
            'description': 'Exec retries stable'
        }
else:
    trends['exec_retry'] = {
        'status': 'no_baseline',
        'current': latest_exec,
        'description': 'Not enough history for trend'
    }

# Identify emerging and resolved for summary
emerging = [k for k, v in trends.items() if v.get('status') == 'emerging']
resolved = [k for k, v in trends.items() if v.get('status') == 'resolved']

result = {
    "generated_at": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
    "lookback_weeks": lookback_weeks,
    "weekly_data": [
        {
            "week": w['week'],
            "start": w['start'],
            "end": w['end'],
            "proposal_count": w['count'],
            "avg_quality": round(w['avg_quality'], 2),
            "frustration_count": w['frustration_count'],
            "exec_retry_count": w['exec_retry_count']
        }
        for w in weeks
    ],
    "trends": trends,
    "emerging": emerging,
    "resolved": resolved,
    "patterns": {k: v for k, v in trends.items()},
    "summary": {
        "emerging_count": len(emerging),
        "resolved_count": len(resolved),
        "stable_count": len([k for k, v in trends.items() if v.get('status') == 'stable']),
        "has_insufficient_data": len([k for k, v in trends.items() if 'no_baseline' in v.get('status', '')]) > 0
    }
}

with open(output_file, 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"[SEA-v5 trends] Complete: {len(emerging)} emerging, {len(resolved)} resolved", file=sys.stderr)
PYEOF

  log "Trend analysis complete: $TRENDS_OUTPUT"
}

main "$@"
