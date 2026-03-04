#!/usr/bin/env bash
set -euo pipefail

REPO_PATH=${1:-}
if [[ -z "$REPO_PATH" ]]; then
  echo "Usage: init_repo_pm.sh /absolute/path/to/repo" >&2
  exit 1
fi

cd "$REPO_PATH"

mkdir -p docs/pm docs/pm/bugs

# Write workflow docs if missing
if [[ ! -f docs/pm/KANBAN-SYSTEM.md ]]; then
cat > docs/pm/KANBAN-SYSTEM.md <<'EOF'
# Repo — Feature Kanban Workflow (Agent Coordination)

**Single source of truth for portfolio-level status:**
- `docs/roadmap/ROADMAP.md`

**Single source of truth for feature-level execution:**
- `docs/features/<feature>/KANBAN.md`

## Rules
1. One feature = one branch.
2. One feature = one kanban file.
3. ROADMAP is status, KANBAN is work.
4. No hidden work: code changes require KANBAN + ROADMAP updates and a PR link.
EOF
fi

if [[ ! -f docs/pm/FEATURE-KANBAN-TEMPLATE.md ]]; then
cat > docs/pm/FEATURE-KANBAN-TEMPLATE.md <<'EOF'
# <Feature Name> — Kanban

**Status:** backlog | in-progress | blocked | done
**Owner:** <agent>
**Branch:** <branch-name>
**PR:** <link>
**Last updated:** YYYY-MM-DD

## Goal

One sentence.

## Kanban

### Backlog
- [ ]

### Doing
- [ ]

### Blocked
- [ ]

### Done
- [ ]
EOF
fi

# Bug inbox (PM intake) — idempotent
if [[ ! -f docs/pm/bugs/README.md ]]; then
cat > docs/pm/bugs/README.md <<'EOF'
# Bugs & Fixes (PM Inbox)

This folder is the **bug intake + triage inbox**.

## Process
1. Create a bug file: `BUG-YYYY-MM-DD-<slug>.md`
2. Fill in repro steps + expected/actual + severity
3. Link it from the relevant feature `docs/features/<feature>/KANBAN.md` (Blocked/Doing)
4. When fixed: add PR link and mark status fixed

## Daily PM review responsibility
- Scan this folder and ensure each open bug is linked from at least one feature KANBAN.
EOF
fi

if [[ ! -f docs/pm/bugs/BUG-TEMPLATE.md ]]; then
cat > docs/pm/bugs/BUG-TEMPLATE.md <<'EOF'
# BUG: <title>

**Status:** open | in-progress | blocked | fixed
**Severity:** low | medium | high | critical
**Discovered:** YYYY-MM-DD
**Reporter:**

**Feature link:** `docs/features/<feature>/KANBAN.md`
**Related PR:**

## Repro Steps
1.
2.

## Expected

## Actual

## Suspected Area

## Fix Plan
- [ ]
EOF
fi

# Ensure features folders exist; add KANBAN if missing
if [[ -d docs/features ]]; then
  for d in docs/features/*; do
    [[ -d "$d" ]] || continue
    if [[ ! -f "$d/KANBAN.md" ]]; then
      cp docs/pm/FEATURE-KANBAN-TEMPLATE.md "$d/KANBAN.md"
    fi
  done
fi

# Patch AGENTS.md (append section if not present)
if [[ -f AGENTS.md ]]; then
  if ! rg -q "Feature Execution Workflow \(Kanban, Mandatory\)" AGENTS.md 2>/dev/null; then
cat >> AGENTS.md <<'EOF'

## Feature Execution Workflow (Kanban, Mandatory)

1. Pick a feature from `docs/roadmap/ROADMAP.md`.
2. Create/update `docs/features/<feature>/KANBAN.md` and set it to **in-progress**.
3. Create a dedicated branch: `feat/<feature-slug>-<short>`.
4. During work: move checkboxes between Backlog → Doing → Done.
5. Before review/merge: update KANBAN with branch + PR link and update ROADMAP status.
EOF
  fi
fi

echo "Initialized repo-kanban-pm workflow in: $REPO_PATH"