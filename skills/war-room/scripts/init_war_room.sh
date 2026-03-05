#!/bin/bash
# Usage: init_war_room.sh <project-name> [workspace-dir]
# Creates the war room folder structure for a new project.
# workspace-dir defaults to the current working directory.

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: init_war_room.sh <project-name> [workspace-dir]"
  echo "  project-name: kebab-case name for the project"
  echo "  workspace-dir: root directory (default: cwd)"
  exit 1
fi

PROJECT="$1"
WORKSPACE="${2:-.}"
DIR="${WORKSPACE}/war-rooms/${PROJECT}"

if [ -d "$DIR" ]; then
  echo "❌ War room already exists: $DIR"
  exit 1
fi

mkdir -p "$DIR"/{agents,comms,lessons,artifacts}

# BRIEF.md
cat > "$DIR/BRIEF.md" << 'BRIEF'
# War Room Brief

## Project
<!-- Name and one-line description -->

## Problem
<!-- What problem are we solving? For whom? -->

## Goals
<!-- 3-5 concrete goals for this session -->

## Constraints
<!-- Budget, timeline, technical, legal, etc. -->

## Known Risks
<!-- What might kill this project? -->

## Success Criteria
<!-- How do we know we're done? -->

## Agents Needed
<!-- List roles: ARCH, PM, DEV, UX, SEC, QA, CHAOS, etc. -->
BRIEF

# DECISIONS.md
cat > "$DIR/DECISIONS.md" << 'DECISIONS'
# DECISIONS

*Append-only log. Format: [D###] OWNER — decision — rationale*
*Only the domain owner writes their decisions. Others can CHALLENGE via comms/*

---
DECISIONS

# STATUS.md
cat > "$DIR/STATUS.md" << 'STATUS'
# STATUS

*Each agent updates their section after completing work.*
*Format: [TIMESTAMP] STATUS — summary (max 50 words)*

---
STATUS

# BLOCKERS.md
cat > "$DIR/BLOCKERS.md" << 'BLOCKERS'
# BLOCKERS

*Anything blocking progress that requires orchestrator action.*
*Format: [TIMESTAMP] ROLE — blocker description — impact*

---
BLOCKERS

# TLDR.md
cat > "$DIR/TLDR.md" << 'TLDR'
# TL;DR

<!-- Updated after consolidation. 10-line executive summary. -->

**Project:**
**Status:**
**Key Decisions:**
**Risks:**
**Next Step:**
TLDR

echo "✅ War room initialized: $DIR"
echo ""
echo "Structure:"
echo "  $DIR/"
echo "  ├── BRIEF.md        ← Fill this in first"
echo "  ├── DECISIONS.md"
echo "  ├── STATUS.md"
echo "  ├── BLOCKERS.md"
echo "  ├── TLDR.md"
echo "  ├── agents/         ← Agents create their own folders"
echo "  ├── comms/           ← Cross-agent messages"
echo "  ├── lessons/         ← Post-mortems"
echo "  └── artifacts/       ← Final outputs"
echo ""
echo "Next: Fill in BRIEF.md, copy DNA.md, then start waves."
