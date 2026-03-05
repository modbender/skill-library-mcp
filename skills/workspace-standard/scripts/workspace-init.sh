#!/usr/bin/env bash
# workspace-init.sh — Bootstrap workspace structure or add a new project.
#
# Usage:
#   ./workspace-init.sh                    # Bootstrap full workspace in current dir
#   ./workspace-init.sh --project my-app   # Add a new project
#   ./workspace-init.sh --path /some/dir   # Specify workspace path
#
# Options:
#   --project NAME   Create a single project (skip full bootstrap)
#   --path DIR       Workspace path (default: current directory)
#   --force          Overwrite existing files

set -euo pipefail

WORKSPACE="."
PROJECT=""
FORCE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --project) PROJECT="$2"; shift 2 ;;
    --path)    WORKSPACE="$2"; shift 2 ;;
    --force)   FORCE=true; shift ;;
    -h|--help)
      echo "Usage: workspace-init.sh [--project NAME] [--path DIR] [--force]"
      echo ""
      echo "Without --project: bootstrap full workspace structure"
      echo "With --project:    add a single project to existing workspace"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Colors
if [ -t 1 ]; then
  GRN='\033[0;32m'; DIM='\033[0;90m'; RST='\033[0m'
else
  GRN=''; DIM=''; RST=''
fi

# --- Defaults (overridden by .workspace-standard.yml if present) ---
PROJ_SUBDIRS="references plans research reports"
ENTITY_SEEDS="people servers decisions"

# --- Load config ---
CONFIG="$WORKSPACE/.workspace-standard.yml"
if [ -f "$CONFIG" ]; then
  # Parse subdirs list (lines starting with "    - " under projects.subdirs)
  _parse_list() {
    local in_section=false
    while IFS= read -r line; do
      if echo "$line" | grep -q "^${1}:"; then in_section=true; continue; fi
      if $in_section; then
        if echo "$line" | grep -q "^[[:space:]]*- "; then
          echo "$line" | sed 's/^[[:space:]]*- //'
        else
          break
        fi
      fi
    done < "$CONFIG"
  }
  PARSED=$(_parse_list "  subdirs")
  [ -n "$PARSED" ] && PROJ_SUBDIRS="$PARSED"
  PARSED=$(_parse_list "entities")
  [ -n "$PARSED" ] && ENTITY_SEEDS="$PARSED"
fi

created() { echo -e "${GRN}+${RST} $1"; }
skipped() { echo -e "${DIM}·${RST} $1 (exists)"; }

write_if_new() {
  local file="$1"
  local content="$2"
  if [ -f "$file" ] && ! $FORCE; then
    skipped "$file"
  else
    mkdir -p "$(dirname "$file")"
    echo "$content" > "$file"
    created "$file"
  fi
}

# --- Create a single project ---
create_project() {
  local name="$1"
  local base="$WORKSPACE/projects/$name"

  echo "Creating project: $name"
  for sub in $PROJ_SUBDIRS; do
    mkdir -p "$base/$sub"
  done

  write_if_new "$base/README.md" "---
role: reference
project: ${name}
status: active
created: $(date +%Y-%m-%d)
updated: $(date +%Y-%m-%d)
summary: \"TODO: describe ${name}\"
---

# ${name}

TODO: describe this project.

## Current State

TODO: what's the current state?

## Key Files

| Need | Location |
|------|----------|
| Architecture | references/ |
| Active plans | plans/ |
| Research | research/ |
| Reports | reports/ |"

  # Add to _index.md if it exists and project isn't already listed
  local index="$WORKSPACE/projects/_index.md"
  if [ -f "$index" ]; then
    if ! grep -qF "[$name]" "$index"; then
      echo "| [${name}](${name}/) | active | TODO: description |" >> "$index"
      created "Added ${name} to projects/_index.md"
    fi
  fi

  for sub in $PROJ_SUBDIRS; do
    created "$base/$sub/"
  done
}

# --- Single project mode ---
if [ -n "$PROJECT" ]; then
  create_project "$PROJECT"
  echo -e "\n${GRN}Project '${PROJECT}' created.${RST}"
  exit 0
fi

# --- Full workspace bootstrap ---
echo "Bootstrapping workspace: $(cd "$WORKSPACE" && pwd)"
echo ""

# Core directories
for d in memory memory/entities projects runbooks skills metrics scripts; do
  if [ -d "$WORKSPACE/$d" ]; then
    skipped "$d/"
  else
    mkdir -p "$WORKSPACE/$d"
    created "$d/"
  fi
done

# Project registry
write_if_new "$WORKSPACE/projects/_index.md" "---
role: reference
status: current
created: $(date +%Y-%m-%d)
updated: $(date +%Y-%m-%d)
summary: \"Registry of all projects in this workspace\"
---

# Projects

| Project | Status | Description |
|---------|--------|-------------|

## Structure Convention

Each project follows:

\`\`\`
projects/<name>/
├── README.md       # Overview, goals, current state
├── references/     # Durable facts
├── plans/          # Active and completed plans
├── research/       # Investigation notes
└── reports/        # Audits, reviews
\`\`\`"

# Entity README
write_if_new "$WORKSPACE/memory/entities/README.md" "# Entities

Structured knowledge about people, servers, decisions, and domains.

## Files

- \`people.md\` — Contacts and relationships
- \`servers.md\` — Infrastructure
- \`decisions.md\` — Key decisions made
- \`domains.md\` — DNS and domain info"

# Seed entity files
for ent in $ENTITY_SEEDS; do
  write_if_new "$WORKSPACE/memory/entities/${ent}.md" "# $(echo "$ent" | sed 's/./\U&/')

<!-- Add entries as they come up -->
"
done

# MEMORY.md seed (the workspace standard's core file)
write_if_new "$WORKSPACE/MEMORY.md" "# MEMORY.md — Current State

*Loaded every session. Keep under 100 lines. See workspace-standard skill for rules.*

---

## People

<!-- Add key contacts here -->

## Where to Find Things

| Need | Location |
|------|----------|
| Project registry | \`projects/_index.md\` |
| Debugging lessons | \`runbooks/lessons-learned.md\` |

## Urgent / Needs Attention

<!-- Nothing yet -->

*Last maintained: $(date +%Y-%m-%d)*"

# Runbooks seed
write_if_new "$WORKSPACE/runbooks/lessons-learned.md" "---
role: runbook
status: current
created: $(date +%Y-%m-%d)
updated: $(date +%Y-%m-%d)
summary: \"Hard-won debugging and operational lessons. Append-only, numbered.\"
---

# Lessons Learned

*Append new lessons with sequential numbers. Never delete — supersede instead.*

<!-- ## 1. First lesson title
- **Date:** YYYY-MM-DD
- **Context:** What happened
- **Root cause:** Why
- **Fix:** What fixed it
- **Prevention:** How to avoid next time
-->"

echo -e "\n${GRN}Workspace bootstrapped.${RST}"
echo -e "${DIM}Next: create your first project with: workspace-init.sh --project my-project${RST}"
