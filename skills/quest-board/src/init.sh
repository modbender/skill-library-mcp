#!/usr/bin/env bash
set -euo pipefail

# Quest Board — Init Script
# Scans the workspace and generates a skeleton quest-board-registry.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Walk up to find the workspace root (where claw.json or AGENTS.md lives)
WS="${QUEST_BOARD_WORKSPACE:-$(cd "$SKILL_DIR/../.." && pwd)}"
REG="$WS/quest-board-registry.json"

if [[ -f "$REG" ]]; then
  echo "⚠️  $REG already exists. Remove it first if you want to regenerate."
  exit 1
fi

echo "🔍 Scanning workspace: $WS"

# Collect top-level directories that contain .md files as candidate projects
declare -A projects
index=0

for dir in "$WS"/*/; do
  [[ -d "$dir" ]] || continue
  dirname="$(basename "$dir")"

  # Skip hidden dirs, node_modules, skills dir itself
  [[ "$dirname" == .* ]] && continue
  [[ "$dirname" == "node_modules" ]] && continue
  [[ "$dirname" == "skills" ]] && continue

  # Check if directory has any .md files
  md_count=$(find "$dir" -maxdepth 2 -name '*.md' 2>/dev/null | wc -l)
  [[ "$md_count" -eq 0 ]] && continue

  # Collect up to 5 .md files as representative files
  files=()
  while IFS= read -r f; do
    rel="${f#"$WS/"}"
    files+=("\"$rel\"")
  done < <(find "$dir" -maxdepth 2 -name '*.md' 2>/dev/null | head -5)

  files_json=$(IFS=,; echo "${files[*]}")

  # Sanitize dirname for use as JSON key
  key=$(echo "$dirname" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')

  projects[$key]="{
      \"name\": \"$dirname\",
      \"status\": \"active\",
      \"priority\": \"\",
      \"progress\": 0,
      \"desc\": \"Auto-discovered from $dirname/ ($md_count md files)\",
      \"files\": [$files_json]
    }"

  index=$((index + 1))
done

# Also pick up top-level .md files as a misc project
top_md=()
while IFS= read -r f; do
  rel="${f#"$WS/"}"
  top_md+=("\"$rel\"")
done < <(find "$WS" -maxdepth 1 -name '*.md' ! -name 'AGENTS.md' ! -name 'SOUL.md' ! -name 'USER.md' ! -name 'MEMORY.md' ! -name 'TOOLS.md' ! -name 'HEARTBEAT.md' 2>/dev/null | head -10)

if [[ ${#top_md[@]} -gt 0 ]]; then
  top_files_json=$(IFS=,; echo "${top_md[*]}")
  projects["misc-notes"]="{
      \"name\": \"Miscellaneous Notes\",
      \"status\": \"active\",
      \"priority\": \"\",
      \"progress\": 0,
      \"desc\": \"Top-level markdown files not in any project folder\",
      \"files\": [$top_files_json]
    }"
fi

# Build the JSON
{
  echo '{'
  echo '  "_meta": {'
  echo "    \"version\": 1,"
  echo "    \"description\": \"Quest Board project registry\","
  echo "    \"lastUpdated\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo "    \"workspace\": \"$WS/\""
  echo '  },'
  echo '  "projects": {'

  first=true
  for key in "${!projects[@]}"; do
    if $first; then first=false; else echo ','; fi
    printf '    "%s": %s' "$key" "${projects[$key]}"
  done

  echo ''
  echo '  },'
  echo '  "research": {},'
  echo '  "infra": {}'
  echo '}'
} > "$REG"

count="${#projects[@]}"
echo "✅ Generated $REG with $count project(s)."
echo "   Review and refine the entries — this is just a skeleton."
