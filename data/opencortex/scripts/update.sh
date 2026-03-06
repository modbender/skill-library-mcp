#!/bin/bash
# OpenCortex — Non-destructive update script
# Adds missing content to your workspace. Never overwrites files you've customized.
# Cron job messages are updated to the latest templates.
# Run from your OpenClaw workspace directory: bash skills/opencortex/scripts/update.sh

set -euo pipefail

OPENCORTEX_VERSION="3.5.18"

# ─────────────────────────────────────────────────────────────────────────────
# Flags
# ─────────────────────────────────────────────────────────────────────────────
DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

if [ "$DRY_RUN" = "true" ]; then
  echo "⚠️  DRY RUN MODE — nothing will be changed."
  echo ""
fi

# Detect interactive terminal
INTERACTIVE=false
if [ -t 0 ]; then
  INTERACTIVE=true
fi

# Helper: ask y/n question, loop until valid answer
# Usage: ask_yn "prompt (y/N): " [default]
# default: y or n (what empty input means). No default = must answer.
# In non-interactive mode: always uses default. If no default, returns 1 (no).
ask_yn() {
  local prompt="$1"
  local default="${2:-}"
  local answer

  if [ "$INTERACTIVE" != "true" ]; then
    if [ "$default" = "y" ]; then
      echo "${prompt}y (auto — non-interactive)"
      return 0
    else
      echo "${prompt}n (auto — non-interactive)"
      return 1
    fi
  fi

  while true; do
    read -p "$prompt" answer < /dev/tty
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    case "$answer" in
      y|yes) return 0 ;;
      n|no) return 1 ;;
      "") 
        if [ "$default" = "y" ]; then return 0;
        elif [ "$default" = "n" ]; then return 1;
        else echo "   Please enter y or n."; fi ;;
      *) echo "   Please enter y or n." ;;
    esac
  done
}

# Helper: ask m/r/k question for non-interactive mode
# Always returns 'k' (keep) when non-interactive
ask_mrk() {
  local prompt="$1"
  local answer
  if [ "$INTERACTIVE" != "true" ]; then
    echo "${prompt}k (auto — non-interactive)"
    echo "k"
    return
  fi
  while true; do
    read -p "$prompt" answer < /dev/tty
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    case "$answer" in
      m|r|k) echo "$answer"; return ;;
      *) echo "   Please enter m, r, or k." >&2 ;;
    esac
  done
}

WORKSPACE="${CLAWD_WORKSPACE:-$(pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔄 OpenCortex Update v${OPENCORTEX_VERSION}"
echo "   Workspace: $WORKSPACE"
echo "   Script:    $SCRIPT_DIR"
echo ""

UPDATED=0
SKIPPED=0

# ─────────────────────────────────────────────────────────────────────────────
# Part 1: Cron job messages — update to latest templates
# ─────────────────────────────────────────────────────────────────────────────
echo "⏰ Checking cron job messages..."


WORKSPACE="${CLAWD_WORKSPACE:-$(pwd)}"
DAILY_MSG="Daily memory maintenance. Read skills/opencortex/references/distillation.md for full instructions and follow them. Workspace: $WORKSPACE"
WEEKLY_MSG="Weekly synthesis. Read skills/opencortex/references/weekly-synthesis.md for full instructions and follow them. Workspace: $WORKSPACE"


if command -v openclaw &>/dev/null; then
  # Get JSON cron list and extract IDs
  CRON_JSON=$(openclaw cron list --json 2>/dev/null || echo "[]")

  get_cron_id() {
    local name="$1"
    local name_lower
    name_lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
    # Parse JSON with grep/awk — look for "name" field matching, then grab preceding "id" field
    echo "$CRON_JSON" | tr ',' '\n' | tr '{' '\n' | tr '}' '\n' | sed 's/^ *//' | awk -v search="$name_lower" '
      /^"id"/ || /^"_id"/ || /^"uuid"/ { gsub(/[" ]/, ""); split($0, a, ":"); last_id=a[2] }
      /^"name"/ { gsub(/["]/, ""); sub(/^name: */, ""); n=tolower($0); if (index(n, search) > 0 && last_id != "") { print last_id; exit } }
    ' 2>/dev/null || true
  }

  # Helper: extract current message for a cron ID from JSON
  get_cron_msg() {
    local cron_id="$1"
    echo "$CRON_JSON" | tr '\n' ' ' | grep -oP "\"id\":\\s*\"${cron_id}\"[^}]*\"message\":\\s*\"[^\"]*\"" | grep -oP '"message":\s*"\K[^"]*' || true
  }

  DAILY_ID=$(get_cron_id "Daily Memory Distillation")
  WEEKLY_ID=$(get_cron_id "Weekly Synthesis")

  if [ -n "$DAILY_ID" ]; then
    CURRENT_DAILY_MSG=$(get_cron_msg "$DAILY_ID")
    # Check if model override exists (anything other than "default" or empty)
    DAILY_MODEL=$(echo "$CRON_JSON" | tr '\n' ' ' | grep -oP "\"id\":\\s*\"${DAILY_ID}\"[^}]*\"model\":\\s*\"[^\"]*\"" | grep -oP '"model":\s*"\K[^"]*' || true)
    DAILY_HAS_MODEL=false
    if [ -n "$DAILY_MODEL" ] && [ "$DAILY_MODEL" != "default" ]; then
      DAILY_HAS_MODEL=true
    fi
    if [ "$CURRENT_DAILY_MSG" = "$DAILY_MSG" ] && [ "$DAILY_HAS_MODEL" = false ]; then
      echo "   ⏭️  'Daily Memory Distillation' already current"
      SKIPPED=$((SKIPPED + 1))
    elif [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would update 'Daily Memory Distillation' (id: $DAILY_ID) message"
      UPDATED=$((UPDATED + 1))
    else
      openclaw cron edit "$DAILY_ID" --message "$DAILY_MSG" --model "default" 2>/dev/null \
        && echo "   ✅ Updated 'Daily Memory Distillation' cron (message + cleared model override)" \
        && UPDATED=$((UPDATED + 1)) \
        || echo "   ⚠️  Could not update 'Daily Memory Distillation' — run manually: openclaw cron edit $DAILY_ID --message '...'"
    fi
  else
    echo "   ⏭️  'Daily Memory Distillation' cron not found — run install.sh to create it"
    SKIPPED=$((SKIPPED + 1))
  fi

  if [ -n "$WEEKLY_ID" ]; then
    CURRENT_WEEKLY_MSG=$(get_cron_msg "$WEEKLY_ID")
    WEEKLY_MODEL=$(echo "$CRON_JSON" | tr '\n' ' ' | grep -oP "\"id\":\\s*\"${WEEKLY_ID}\"[^}]*\"model\":\\s*\"[^\"]*\"" | grep -oP '"model":\s*"\K[^"]*' || true)
    WEEKLY_HAS_MODEL=false
    if [ -n "$WEEKLY_MODEL" ] && [ "$WEEKLY_MODEL" != "default" ]; then
      WEEKLY_HAS_MODEL=true
    fi
    if [ "$CURRENT_WEEKLY_MSG" = "$WEEKLY_MSG" ] && [ "$WEEKLY_HAS_MODEL" = false ]; then
      echo "   ⏭️  'Weekly Synthesis' already current"
      SKIPPED=$((SKIPPED + 1))
    elif [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would update 'Weekly Synthesis' (id: $WEEKLY_ID) message"
      UPDATED=$((UPDATED + 1))
    else
      openclaw cron edit "$WEEKLY_ID" --message "$WEEKLY_MSG" --model "default" 2>/dev/null \
        && echo "   ✅ Updated 'Weekly Synthesis' cron (message + cleared model override)" \
        && UPDATED=$((UPDATED + 1)) \
        || echo "   ⚠️  Could not update 'Weekly Synthesis' — run manually: openclaw cron edit $WEEKLY_ID --message '...'"
    fi
  else
    echo "   ⏭️  'Weekly Synthesis' cron not found — run install.sh to create it"
    SKIPPED=$((SKIPPED + 1))
  fi
else
  echo "   ⚠️  openclaw CLI not found — skipping cron updates"
  SKIPPED=$((SKIPPED + 1))
fi
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Part 2: Principles — add any missing P1–P8 to MEMORY.md
# ─────────────────────────────────────────────────────────────────────────────
echo "📜 Checking principles in MEMORY.md..."

if [ ! -f "$WORKSPACE/MEMORY.md" ]; then
  echo "   ⚠️  MEMORY.md not found — skipping principles check (run install.sh first)"
  SKIPPED=$((SKIPPED + 1))
else
  # Build associative array: principle number → full block text
  declare -A PRINCIPLE_TEXTS

  PRINCIPLE_TEXTS["P1"]=$(cat <<'EOPR'
### P1: Delegate First
Assess every task for sub-agent delegation before starting. Stay available. Assign sub-agents by complexity using whatever models are configured:
- **Light:** File ops, searches, data extraction, simple scripts, monitoring, lookups
- **Medium:** Multi-step work, code writing, debugging, research, moderate complexity
- **Heavy:** Complex reasoning, architecture decisions, sensitive or destructive operations
- **Keep main thread for:** Conversation, decisions, confirmations, quick answers
EOPR
)

  PRINCIPLE_TEXTS["P2"]=$(cat <<'EOPR'
### P2: Write It Down
Do not mentally note — commit to memory files. Update indexes after significant work.
Write before responding: when a user states a preference, makes a decision, gives a deadline, or corrects you, write it to the relevant memory file before composing your response. If the session ends or compacts before you save, the context is lost. Writing first ensures durability.
EOPR
)

  PRINCIPLE_TEXTS["P3"]=$(cat <<'EOPR'
### P3: Ask Before External Actions
Emails, public posts, destructive ops — get confirmation first.
EOPR
)

  PRINCIPLE_TEXTS["P4"]=$(cat <<'EOPR'
### P4: Tool Shed & Workflows
All tools, APIs, access methods, and capabilities SHALL be documented in TOOLS.md with goal-oriented abilities descriptions. When given a new tool during work, immediately add it. Document workflows and pipelines in memory/workflows/ with clear descriptions of what they do, how they connect, and how to operate them.
**Creation:** When you access a new system, API, or resource more than once — or when given access to something that will clearly recur — proactively create the tool entry, bridge doc, or helper script. When a multi-service workflow is described or used, document it in memory/workflows/. Do not wait to be asked.
**Enforcement:** After using any CLI tool, API, or service — before ending the task — verify it exists in TOOLS.md. If not, add it immediately. Do not defer to distillation.
EOPR
)

  PRINCIPLE_TEXTS["P5"]=$(cat <<'EOPR'
### P5: Capture Decisions & Preferences
When the user makes a decision or states a preference, immediately record it. Decisions go in the relevant project/memory file. Preferences go in memory/preferences.md under the right category. Never re-ask something already decided or stated.
**Decisions format:** **Decision:** [what] — [why] (date) — in the relevant project or memory file.
**Preferences format:** **Preference:** [what] — [context/reasoning] (date) — in memory/preferences.md under the matching category (Communication, Code & Technical, Workflow & Process, Scheduling & Time, Tools & Services, Content & Media, Environment & Setup).
**Recognition:** Decisions include: explicit choices, architectural directions, and workflow rules. Preferences include: stated likes/dislikes, communication style preferences, tool preferences, formatting preferences, and any opinion that would affect future work. If the user says "I prefer X" or "always do Y" or "I don't like Z" — that is a preference. Capture it immediately.
**Enforcement:** Before ending any conversation with substantive work, scan for uncaptured decisions AND preferences. If any, write them before closing.
EOPR
)

  PRINCIPLE_TEXTS["P6"]=$(cat <<'EOPR'
### P6: Sub-agent Debrief
Sub-agents MUST write a brief debrief to memory/YYYY-MM-DD.md before completing. Include: what was done, what was learned, any issues.
**Recovery:** If a sub-agent fails, times out, or is killed before debriefing, the parent agent writes the debrief on its behalf noting the failure mode. No delegated work should vanish from memory.
EOPR
)

  PRINCIPLE_TEXTS["P7"]=$(cat <<'EOPR'
### P7: Log Failures
When something fails or the user corrects you, immediately append to the daily log with ❌ FAILURE: or 🔧 CORRECTION: tags. Include: what happened, why it failed, what fixed it. Nightly distillation routes these to the right file.
**Root cause:** Do not just log what happened — log *why* it happened and what would prevent it next time. If it is a systemic issue (missing principle, bad assumption, tool gap), propose a fix immediately.
EOPR
)

  PRINCIPLE_TEXTS["P8"]=$(cat <<'EOPR'
### P8: Check the Shed First
Before telling the user you cannot do something, or asking them to do it manually, CHECK your resources: TOOLS.md, INFRA.md, memory/projects/, runbooks, and any bridge docs. If a tool, API, credential, or access method exists that could accomplish the task — use it. The shed exists so you do not make the user do work you are equipped to handle.
**Enforcement:** Nightly audit scans for instances where the agent deferred work to the user that could have been done via documented tools.
EOPR
)

  # Ensure P0 exists (needed for migration from older versions)
  if ! grep -q "^### P0:" "$WORKSPACE/MEMORY.md" 2>/dev/null; then
    echo "   ℹ️  Adding P0 (Custom Principles) section for your own additions..."
    if [ "$DRY_RUN" != "true" ]; then
      # Insert P0 right after the PRINCIPLES header
      p_header=$(grep -n "^## .*PRINCIPLES" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
      if [ -n "$p_header" ]; then
        p0_text="\n### P0: Custom Principles\nYour custom principles go here as P0-A, P0-B, P0-C, etc. All custom principles belong in P0 regardless of how they are requested. These are never modified by OpenCortex updates.\n"
        sed -i "${p_header}a\\${p0_text}" "$WORKSPACE/MEMORY.md"
        echo "   ✅ Added P0 section"
        UPDATED=$((UPDATED + 1))
      fi
    fi
  fi

  # Collect missing or outdated principles
  MISSING_PRINCIPLES=()
  OUTDATED_PRINCIPLES=()
  for pnum in P1 P2 P3 P4 P5 P6 P7 P8; do
    if grep -q "^### ${pnum}:" "$WORKSPACE/MEMORY.md" 2>/dev/null; then
      # Check if the principle title matches the latest version
      current_title=""
      current_title=$(grep "^### ${pnum}:" "$WORKSPACE/MEMORY.md" | head -1)
      expected_title=""
      expected_title=$(echo "${PRINCIPLE_TEXTS[$pnum]}" | head -1)
      if [ "$current_title" != "$expected_title" ]; then
        echo "   🔄 ${pnum} title changed — will update"
        OUTDATED_PRINCIPLES+=("$pnum")
      else
        # Title matches — check if body content has changed
        # Extract current principle block including header (from ### Px: to line before next ### P or ---)
        current_body=$(awk "/^### ${pnum}:/{found=1} found{if(/^### P[0-9]/ && !/^### ${pnum}:/)exit; if(/^---$/)exit; if(/^## /)exit; print}" "$WORKSPACE/MEMORY.md" 2>/dev/null)
        expected_body="${PRINCIPLE_TEXTS[$pnum]}"
        current_hash=$(printf '%s' "$current_body" | tr -d '[:space:]' | md5sum | cut -d' ' -f1)
        expected_hash=$(printf '%s' "$expected_body" | tr -d '[:space:]' | md5sum | cut -d' ' -f1)
        if [ "$current_hash" != "$expected_hash" ]; then
          echo "   🔄 ${pnum} content changed — will update"
          OUTDATED_PRINCIPLES+=("$pnum")
        else
          echo "   ⏭️  ${pnum} already exists (skipped)"
          SKIPPED=$((SKIPPED + 1))
        fi
      fi
    else
      echo "   ⚠️  ${pnum} missing — will add"
      MISSING_PRINCIPLES+=("$pnum")
    fi
  done

  # Replace outdated principles in-place
  if [ ${#OUTDATED_PRINCIPLES[@]} -gt 0 ]; then
    if [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would update principles: ${OUTDATED_PRINCIPLES[*]}"
    else
      for pnum in "${OUTDATED_PRINCIPLES[@]}"; do
        # Show what changed
        current_title=$(grep "^### ${pnum}:" "$WORKSPACE/MEMORY.md" | head -1)
        expected_title=$(echo "${PRINCIPLE_TEXTS[$pnum]}" | head -1)
        echo ""
        # Extract current principle block for display (including header)
        current_full=$(awk "/^### ${pnum}:/{found=1} found{if(/^### P[0-9]/ && !/^### ${pnum}:/)exit; if(/^---$/)exit; if(/^## /)exit; print}" "$WORKSPACE/MEMORY.md" 2>/dev/null)
        expected_full="${PRINCIPLE_TEXTS[$pnum]}"

        if [ "$current_title" != "$expected_title" ]; then
          echo "   ${pnum} title changed:"
          echo "     Current: $current_title"
          echo "     New:     $expected_title"
        else
          echo "   ${pnum} content updated (title unchanged)"
        fi
        echo ""
        echo "   ┌─ Current ──────────────────────────────"
        echo "$current_full" | sed 's/^/   │ /'
        echo "   └─────────────────────────────────────────"
        echo ""
        echo "   ┌─ New ─────────────────────────────────"
        echo "$expected_full" | sed 's/^/   │ /'
        echo "   └─────────────────────────────────────────"
        echo ""
        # Detect custom additions: lines in current that aren't in the expected version
        custom_lines=""
        if [ -n "$current_full" ] && [ -n "$expected_full" ]; then
          custom_lines=$(diff <(echo "$expected_full") <(echo "$current_full") 2>/dev/null | grep "^> " | sed 's/^> //' | sed '/^$/d' || true)
        fi

        if [ -n "$custom_lines" ]; then
          echo "   📋 Custom content detected beyond the standard ${pnum}:"
          echo "$custom_lines" | sed 's/^/      /'
          echo ""
          if ask_yn "   Migrate custom content to P0 before updating? (Y/n): " y; then
            # Find or create P0 section
            if grep -q "^### P0:" "$WORKSPACE/MEMORY.md" 2>/dev/null; then
              # Count existing P0 sub-principles to determine next letter
              existing_count=$(grep -c "^#### P0-" "$WORKSPACE/MEMORY.md" 2>/dev/null || true)
              existing_count=$(printf '%s' "$existing_count" | tr -dc '0-9')
              existing_count=${existing_count:-0}
              next_letter=$(printf "\\$(printf '%03o' $((65 + existing_count)))")
              # Insert after the P0 description line
              p0_line=$(grep -n "^### P0:" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
              # Find the next ### heading after P0
              p0_end=$(tail -n "+$((p0_line + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^### P[0-9]" | head -1 | cut -d: -f1)
              if [ -n "$p0_end" ]; then
                insert_at=$((p0_line + p0_end - 1))
              else
                insert_at=$((p0_line + 1))
              fi
              # Build the sub-principle
              sub_principle="\n#### P0-${next_letter}: Custom from ${pnum}\n${custom_lines}\n"
              sed -i "${insert_at}a\\${sub_principle}" "$WORKSPACE/MEMORY.md"
              echo "   ✅ Migrated to P0-${next_letter}"
            else
              echo "   ⚠️  P0 section not found — custom content preserved in current ${pnum}"
              echo "      Skipping update to avoid data loss."
              SKIPPED=$((SKIPPED + 1))
              continue
            fi
          fi
        fi

        echo "   ⚠️  Replacing will overwrite any custom additions you made to this principle."
        if ask_yn "   Update ${pnum}? (y/N): " n; then
          # Find the start and end line of the existing principle block
          start_line=""; end_line=""; next_section=""
          start_line=$(grep -n "^### ${pnum}:" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
          # Find the next ### or ## heading after start_line
          next_section=$(tail -n +"$((start_line + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^###\|^## " | head -1 | cut -d: -f1)
          if [ -n "$next_section" ]; then
            end_line=$((start_line + next_section - 1))
          else
            end_line=$(wc -l < "$WORKSPACE/MEMORY.md")
          fi
          # Replace the block
          tmp_mem=$(mktemp)
          head -n "$((start_line - 1))" "$WORKSPACE/MEMORY.md" > "$tmp_mem"
          echo "${PRINCIPLE_TEXTS[$pnum]}" >> "$tmp_mem"
          echo "" >> "$tmp_mem"
          tail -n "+$((end_line + 1))" "$WORKSPACE/MEMORY.md" >> "$tmp_mem"
          mv "$tmp_mem" "$WORKSPACE/MEMORY.md"
          echo "   ✅ Updated ${pnum}"
          UPDATED=$((UPDATED + 1))
        else
          echo "   ⏭️  Kept existing ${pnum}"
          SKIPPED=$((SKIPPED + 1))
        fi
      done
    fi
  fi

  if [ ${#MISSING_PRINCIPLES[@]} -gt 0 ]; then
    if [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would add missing principles: ${MISSING_PRINCIPLES[*]}"
      UPDATED=$((UPDATED + ${#MISSING_PRINCIPLES[@]}))
    else
      # Write all missing principles to a temp file
      TEMP_P=$(mktemp)
      for pnum in "${MISSING_PRINCIPLES[@]}"; do
        printf '\n%s\n' "${PRINCIPLE_TEXTS[$pnum]}" >> "$TEMP_P"
      done

      # Insert before "## Identity" if it exists, otherwise append
      if grep -q "^## Identity" "$WORKSPACE/MEMORY.md"; then
        # Insert new principles before ## Identity line
        sed -i "/^## Identity/e cat $TEMP_P" "$WORKSPACE/MEMORY.md"
        # Add blank line before ## Identity if missing
        sed -i '/^## Identity/{x;/./{x;b};x;s/^/\n/}' "$WORKSPACE/MEMORY.md" 2>/dev/null || true
      elif grep -q "^---$" "$WORKSPACE/MEMORY.md"; then
        # Insert before first --- divider
        sed -i "0,/^---$/{ /^---$/e cat $TEMP_P
        }" "$WORKSPACE/MEMORY.md"
      else
        # Append to end
        cat "$TEMP_P" >> "$WORKSPACE/MEMORY.md"
      fi

      rm -f "$TEMP_P"
      for pnum in "${MISSING_PRINCIPLES[@]}"; do
        echo "   ✅ Added principle ${pnum}"
        UPDATED=$((UPDATED + 1))
      done
    fi
  fi
fi

# Clean up extra/duplicate principles beyond P0-P8
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  echo ""
  echo "🧹 Checking for extra principles..."
  EXTRA_PRINCIPLES=$(grep "^### P[0-9]" "$WORKSPACE/MEMORY.md" | grep -v "^### P0:\|^### P1:\|^### P2:\|^### P3:\|^### P4:\|^### P5:\|^### P6:\|^### P7:\|^### P8:" || true)

  if [ -n "$EXTRA_PRINCIPLES" ]; then
    echo "   Found principles outside P0-P8 range:"
    echo "$EXTRA_PRINCIPLES" | sed 's/^/      /'
    echo ""

    while IFS= read -r extra_line; do
      [ -z "$extra_line" ] && continue
      extra_pnum=$(echo "$extra_line" | sed 's/^### \(P[0-9]*\):.*/\1/')
      extra_title="$extra_line"

      # Extract the full body of this extra principle
      extra_body=$(awk "/^### ${extra_pnum}:/{found=1} found{if(/^### P[0-9]/ && !/^### ${extra_pnum}:/)exit; if(/^---$/)exit; if(/^## /)exit; print}" "$WORKSPACE/MEMORY.md" 2>/dev/null)

      # Check if this is a duplicate of an existing P1-P8
      # Must match BOTH title AND body content to be considered a duplicate
      is_duplicate=false
      dup_of=""
      for std_pnum in P1 P2 P3 P4 P5 P6 P7 P8; do
        std_title=$(grep "^### ${std_pnum}:" "$WORKSPACE/MEMORY.md" 2>/dev/null | head -1)
        if [ -n "$std_title" ]; then
          extra_name=$(echo "$extra_title" | sed 's/^### P[0-9]*: //')
          std_name=$(echo "$std_title" | sed 's/^### P[0-9]*: //')
          if [ "$extra_name" = "$std_name" ]; then
            # Title matches — now compare body content
            std_body=$(awk "/^### ${std_pnum}:/{found=1} found{if(/^### P[0-9]/ && !/^### ${std_pnum}:/)exit; if(/^---$/)exit; if(/^## /)exit; print}" "$WORKSPACE/MEMORY.md" 2>/dev/null)
            # Compare using hash of whitespace-stripped content
            extra_hash=$(echo "$extra_body" | tr -d '[:space:]' | md5sum | cut -d' ' -f1)
            std_hash=$(echo "$std_body" | tr -d '[:space:]' | md5sum | cut -d' ' -f1)
            if [ "$extra_hash" = "$std_hash" ]; then
              is_duplicate=true
              dup_of="$std_pnum"
              echo "   🔄 $extra_pnum is a full duplicate of $std_pnum ($std_name) — same title AND body"
              break
            else
              echo "   ℹ️  $extra_pnum has same title as $std_pnum ($std_name) but DIFFERENT body content"
            fi
          fi
        fi
      done

      if [ "$is_duplicate" = true ]; then
        if ask_yn "   Remove duplicate $extra_pnum? (y/N): " n; then
          if [ "$DRY_RUN" != "true" ]; then
            start_line=$(grep -n "^### ${extra_pnum}:" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
            next_line=$(tail -n "+$((start_line + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^### \|^## " | head -1 | cut -d: -f1)
            if [ -n "$next_line" ]; then
              end_line=$((start_line + next_line - 1))
            else
              end_line=$(wc -l < "$WORKSPACE/MEMORY.md")
            fi
            tmp_mem=$(mktemp)
            head -n "$((start_line - 1))" "$WORKSPACE/MEMORY.md" > "$tmp_mem"
            tail -n "+$((end_line + 1))" "$WORKSPACE/MEMORY.md" >> "$tmp_mem"
            mv "$tmp_mem" "$WORKSPACE/MEMORY.md"
            echo "   ✅ Removed duplicate $extra_pnum"
            UPDATED=$((UPDATED + 1))
          fi
        fi
      else
        echo "   📋 $extra_pnum has unique content:"
        echo "$extra_body" | head -5 | sed 's/^/      /'
        echo ""
        echo "   What should we do with $extra_pnum?"
        echo "     m = Move to P0 as custom sub-principle"
        echo "     r = Remove entirely"
        echo "     k = Keep as-is (no change)"
        ACTION=$(ask_mrk "   Action for $extra_pnum? (m/r/k): ")
        case "$ACTION" in
            m)
              if [ "$DRY_RUN" != "true" ]; then
                # Count existing P0 sub-principles
                existing_count=$(grep -c "^#### P0-" "$WORKSPACE/MEMORY.md" 2>/dev/null || true)
                existing_count=$(printf '%s' "$existing_count" | tr -dc '0-9')
                existing_count=${existing_count:-0}
                next_letter=$(printf "\\$(printf '%03o' $((65 + existing_count)))")

                # Add to P0
                p0_line=$(grep -n "^### P0:" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
                p0_end=$(tail -n "+$((p0_line + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^### P[0-9]" | head -1 | cut -d: -f1)
                if [ -n "$p0_end" ]; then
                  insert_at=$((p0_line + p0_end - 1))
                else
                  insert_at=$((p0_line + 1))
                fi
                # Build sub-principle from body (skip the original ### header)
                sub_body=$(echo "$extra_body" | tail -n +2)
                sub_name=$(echo "$extra_title" | sed 's/^### P[0-9]*: //')
                sub_text="\n#### P0-${next_letter}: ${sub_name}\n${sub_body}\n"
                sed -i "${insert_at}a\\${sub_text}" "$WORKSPACE/MEMORY.md"

                # Remove the original
                start_line=$(grep -n "^### ${extra_pnum}:" "$WORKSPACE/MEMORY.md" | tail -1 | cut -d: -f1)
                next_line=$(tail -n "+$((start_line + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^### \|^## " | head -1 | cut -d: -f1)
                if [ -n "$next_line" ]; then
                  end_line=$((start_line + next_line - 1))
                else
                  end_line=$(wc -l < "$WORKSPACE/MEMORY.md")
                fi
                tmp_mem=$(mktemp)
                head -n "$((start_line - 1))" "$WORKSPACE/MEMORY.md" > "$tmp_mem"
                tail -n "+$((end_line + 1))" "$WORKSPACE/MEMORY.md" >> "$tmp_mem"
                mv "$tmp_mem" "$WORKSPACE/MEMORY.md"
                echo "   ✅ Moved to P0-${next_letter}, removed $extra_pnum"
                UPDATED=$((UPDATED + 1))
              fi
              ;;
            r)
              if [ "$DRY_RUN" != "true" ]; then
                start_line=$(grep -n "^### ${extra_pnum}:" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
                next_line=$(tail -n "+$((start_line + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^### \|^## " | head -1 | cut -d: -f1)
                if [ -n "$next_line" ]; then
                  end_line=$((start_line + next_line - 1))
                else
                  end_line=$(wc -l < "$WORKSPACE/MEMORY.md")
                fi
                tmp_mem=$(mktemp)
                head -n "$((start_line - 1))" "$WORKSPACE/MEMORY.md" > "$tmp_mem"
                tail -n "+$((end_line + 1))" "$WORKSPACE/MEMORY.md" >> "$tmp_mem"
                mv "$tmp_mem" "$WORKSPACE/MEMORY.md"
                echo "   ✅ Removed $extra_pnum"
                UPDATED=$((UPDATED + 1))
              fi
              ;;
            k)
              echo "   ⏭️  Kept $extra_pnum"
              SKIPPED=$((SKIPPED + 1))
              ;;
        esac
      fi
    done <<< "$EXTRA_PRINCIPLES"
  else
    echo "   ⏭️  No extra principles found (P0-P8 only)"
    SKIPPED=$((SKIPPED + 1))
  fi
fi

# Check for non-standard ## sections in MEMORY.md that should be moved
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  echo ""
  echo "🧹 Checking MEMORY.md structure..."
  STANDARD_MEM_SECTIONS="PRINCIPLES|Identity|Memory Index"
  NON_STANDARD=""
  while IFS= read -r section_line; do
    section_name=$(echo "$section_line" | sed 's/^## //')
    if ! echo "$section_name" | grep -qE "($STANDARD_MEM_SECTIONS)"; then
      NON_STANDARD="${NON_STANDARD}${section_line}\n"
    fi
  done < <(grep "^## " "$WORKSPACE/MEMORY.md" | grep -v "^## 🔴")

  if [ -n "$NON_STANDARD" ]; then
    echo "   Found non-standard ## sections in MEMORY.md:"
    printf "   %b" "$NON_STANDARD" | sed 's/^/      /'
    echo "   MEMORY.md should only contain: 🔴 PRINCIPLES, ## Identity, ## Memory Index"
    echo ""

    # Move each non-standard section to its own file
    while IFS= read -r ns_line; do
      [ -z "$ns_line" ] && continue
      ns_name=$(echo "$ns_line" | sed 's/^## //')
      # Sanitize for filename: lowercase, spaces to hyphens, strip special chars
      ns_file=$(echo "$ns_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
      ns_dest="$WORKSPACE/memory/${ns_file}.md"

      # Extract section content
      ns_start=$(grep -n "^## ${ns_name}$" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
      [ -z "$ns_start" ] && continue
      ns_next=$(tail -n "+$((ns_start + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^## " | head -1 | cut -d: -f1)
      if [ -n "$ns_next" ]; then
        ns_end=$((ns_start + ns_next - 1))
      else
        ns_end=$(wc -l < "$WORKSPACE/MEMORY.md")
      fi
      ns_content=$(sed -n "${ns_start},${ns_end}p" "$WORKSPACE/MEMORY.md")

      echo "   📦 \"## ${ns_name}\" → memory/${ns_file}.md"
      if ask_yn "   Move this section? (Y/n): " y; then
        if [ "$DRY_RUN" != "true" ]; then
          if [ -f "$ns_dest" ]; then
            echo "" >> "$ns_dest"
            echo "$ns_content" >> "$ns_dest"
            echo "   ✅ Appended to existing ${ns_dest##*/}"
          else
            echo "# ${ns_name}" > "$ns_dest"
            echo "" >> "$ns_dest"
            # Write body (skip the ## header line)
            echo "$ns_content" | tail -n +2 >> "$ns_dest"
            echo "   ✅ Created memory/${ns_file}.md"
          fi

          # Remove from MEMORY.md
          tmp_mem=$(mktemp)
          # Keep lines before section, skip section, keep lines after
          head -n "$((ns_start - 1))" "$WORKSPACE/MEMORY.md" > "$tmp_mem"
          if [ "$ns_end" -lt "$(wc -l < "$WORKSPACE/MEMORY.md")" ]; then
            tail -n "+$((ns_end + 1))" "$WORKSPACE/MEMORY.md" >> "$tmp_mem"
          fi
          mv "$tmp_mem" "$WORKSPACE/MEMORY.md"
          echo "   ✅ Removed from MEMORY.md"
          UPDATED=$((UPDATED + 1))
        fi
      else
        echo "   ⏭️  Kept in MEMORY.md"
        SKIPPED=$((SKIPPED + 1))
      fi
    done <<< "$(printf '%b' "$NON_STANDARD")"
  else
    echo "   ⏭️  MEMORY.md structure is clean"
    SKIPPED=$((SKIPPED + 1))
  fi

  # Size check — after non-standard section moves, re-measure
  MEM_SIZE=$(du -k "$WORKSPACE/MEMORY.md" 2>/dev/null | cut -f1)
  if [ "$MEM_SIZE" -gt 5 ]; then
    echo ""
    echo "   📏 MEMORY.md is ${MEM_SIZE}KB (target: < 5KB) — checking for bloated subsections..."

    # Find ### subsections under ## Memory Index that are over 10 lines
    # These can be extracted to dedicated files with a reference left behind
    MEM_INDEX_START=$(grep -n "^## Memory Index" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1 || true)
    if [ -n "$MEM_INDEX_START" ]; then
    MEM_INDEX_END=$(tail -n "+$((MEM_INDEX_START + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^## " | head -1 | cut -d: -f1 || true)
      if [ -n "$MEM_INDEX_END" ]; then
        MEM_INDEX_END=$((MEM_INDEX_START + MEM_INDEX_END - 1))
      else
        MEM_INDEX_END=$(wc -l < "$WORKSPACE/MEMORY.md")
      fi

      # Extract each ### subsection and check line count
      SUBSECTIONS=$(sed -n "${MEM_INDEX_START},${MEM_INDEX_END}p" "$WORKSPACE/MEMORY.md" | grep "^### " || true)
      while IFS= read -r sub_header; do
        [ -z "$sub_header" ] && continue
        sub_name=$(echo "$sub_header" | sed 's/^### //' | sed 's/ (.*//')
        # Use fixed-string grep to handle special chars in headers like (memory/contacts/)
        sub_start=$(grep -nF "$sub_header" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1)
        [ -z "$sub_start" ] && continue
        sub_next=$(tail -n "+$((sub_start + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^### \|^## " | head -1 | cut -d: -f1 || true)
        if [ -n "$sub_next" ]; then
          sub_end=$((sub_start + sub_next - 1))
        else
          sub_end=$MEM_INDEX_END
        fi
        sub_lines=$((sub_end - sub_start))

        if [ "$sub_lines" -gt 10 ]; then
          # Determine destination file
          sub_file=$(echo "$sub_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
          sub_dest="$WORKSPACE/memory/${sub_file}.md"

          echo "   📦 \"### ${sub_name}\" is ${sub_lines} lines — move to memory/${sub_file}.md?"
          if ask_yn "   Extract and replace with reference? (Y/n): " y; then
            if [ "$DRY_RUN" != "true" ]; then
              # Extract content (include header)
              sub_content=$(sed -n "${sub_start},${sub_end}p" "$WORKSPACE/MEMORY.md")

              if [ -f "$sub_dest" ]; then
                echo "" >> "$sub_dest"
                echo "$sub_content" | tail -n +2 >> "$sub_dest"
              else
                echo "# ${sub_name}" > "$sub_dest"
                echo "" >> "$sub_dest"
                echo "$sub_content" | tail -n +2 >> "$sub_dest"
              fi

              # Replace section with brief reference (keep ### header, add See reference, remove body)
              tmp_mem=$(mktemp)
              head -n "$sub_start" "$WORKSPACE/MEMORY.md" > "$tmp_mem"
              echo "See \`memory/${sub_file}.md\` for details." >> "$tmp_mem"
              echo "" >> "$tmp_mem"
              if [ "$sub_end" -lt "$(wc -l < "$WORKSPACE/MEMORY.md")" ]; then
                tail -n "+$((sub_end + 1))" "$WORKSPACE/MEMORY.md" >> "$tmp_mem"
              fi
              mv "$tmp_mem" "$WORKSPACE/MEMORY.md"

              echo "   ✅ Extracted to memory/${sub_file}.md, left reference in MEMORY.md"
              UPDATED=$((UPDATED + 1))

              # Recalculate line numbers since file changed
              MEM_INDEX_START=$(grep -n "^## Memory Index" "$WORKSPACE/MEMORY.md" | head -1 | cut -d: -f1 || true)
              if [ -n "$MEM_INDEX_START" ]; then
                MEM_INDEX_END_TMP=$(tail -n "+$((MEM_INDEX_START + 1))" "$WORKSPACE/MEMORY.md" | grep -n "^## " | head -1 | cut -d: -f1 || true)
                if [ -n "$MEM_INDEX_END_TMP" ]; then
                  MEM_INDEX_END=$((MEM_INDEX_START + MEM_INDEX_END_TMP - 1))
                else
                  MEM_INDEX_END=$(wc -l < "$WORKSPACE/MEMORY.md")
                fi
              fi
            fi
          else
            echo "   ⏭️  Kept inline"
            SKIPPED=$((SKIPPED + 1))
          fi
        fi
      done <<< "$SUBSECTIONS"
    fi

    # Final size report
    MEM_SIZE=$(du -k "$WORKSPACE/MEMORY.md" 2>/dev/null | cut -f1)
    if [ "$MEM_SIZE" -gt 5 ]; then
      echo "   ℹ️  MEMORY.md is now ${MEM_SIZE}KB — further trimming may be needed by the agent during distillation"
    else
      echo "   ✅ MEMORY.md trimmed to ${MEM_SIZE}KB (within target)"
    fi
  else
    echo "   ✅ MEMORY.md is ${MEM_SIZE}KB (within target)"
  fi
fi
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Part 3: Scripts — copy any missing helper scripts to workspace
# ─────────────────────────────────────────────────────────────────────────────
echo "📋 Checking helper scripts..."

copy_or_update_script() {
  local script_name="$1"
  local src="$SCRIPT_DIR/$script_name"
  local dst="$WORKSPACE/scripts/$script_name"

  if [ ! -f "$src" ]; then
    echo "   ⏭️  $script_name not found in skill package (skipped)"
    SKIPPED=$((SKIPPED + 1))
    return
  fi

  if [ -f "$dst" ]; then
    # Compare checksums — update if different
    local src_hash dst_hash
    src_hash=$(md5sum "$src" 2>/dev/null | cut -d' ' -f1)
    dst_hash=$(md5sum "$dst" 2>/dev/null | cut -d' ' -f1)
    if [ "$src_hash" = "$dst_hash" ]; then
      echo "   ⏭️  $script_name already current (skipped)"
      SKIPPED=$((SKIPPED + 1))
      return
    fi
    if [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would update: $script_name"
    else
      cp "$src" "$dst"
      chmod +x "$dst"
      echo "   🔄 Updated $script_name"
    fi
    UPDATED=$((UPDATED + 1))
    return
  fi

  if [ "$DRY_RUN" = "true" ]; then
    echo "   [DRY RUN] Would copy: $src → $dst"
    UPDATED=$((UPDATED + 1))
  else
    mkdir -p "$WORKSPACE/scripts"
    cp "$src" "$dst"
    chmod +x "$dst"
    echo "   ✅ Copied $script_name to workspace scripts/"
    UPDATED=$((UPDATED + 1))
  fi
}

copy_or_update_script "verify.sh"
copy_or_update_script "vault.sh"
copy_or_update_script "metrics.sh"
copy_or_update_script "git-backup.sh"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Part 3b: Reference docs — update to latest versions
# ─────────────────────────────────────────────────────────────────────────────
echo "📚 Checking reference documents..."

copy_or_update_ref() {
  local ref_name="$1"
  local src="$SCRIPT_DIR/../references/$ref_name"
  local dst="$WORKSPACE/skills/opencortex/references/$ref_name"

  if [ ! -f "$src" ]; then
    # Try alternate skill path
    src="$SCRIPT_DIR/../references/$ref_name"
    [ ! -f "$src" ] && return
  fi

  mkdir -p "$(dirname "$dst")"

  if [ -f "$dst" ]; then
    local src_hash dst_hash
    src_hash=$(md5sum "$src" 2>/dev/null | cut -d' ' -f1)
    dst_hash=$(md5sum "$dst" 2>/dev/null | cut -d' ' -f1)
    if [ "$src_hash" = "$dst_hash" ]; then
      echo "   ⏭️  references/$ref_name already current (skipped)"
      SKIPPED=$((SKIPPED + 1))
      return
    fi
    if [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would update: references/$ref_name"
    else
      cp "$src" "$dst"
      echo "   🔄 Updated references/$ref_name"
    fi
    UPDATED=$((UPDATED + 1))
  else
    if [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would copy: references/$ref_name"
    else
      cp "$src" "$dst"
      echo "   ✅ Copied references/$ref_name"
    fi
    UPDATED=$((UPDATED + 1))
  fi
}

copy_or_update_ref "distillation.md"
copy_or_update_ref "weekly-synthesis.md"
copy_or_update_ref "architecture.md"

# Create new directories if missing
for d in memory/contacts memory/workflows; do
  if [ ! -d "$WORKSPACE/$d" ]; then
    if [ "$DRY_RUN" = "true" ]; then
      echo "   [DRY RUN] Would create: $d/"
    else
      mkdir -p "$WORKSPACE/$d"
      echo "   📁 Created $d/"
      UPDATED=$((UPDATED + 1))
    fi
  fi
done

# Create preferences.md if missing
if [ ! -f "$WORKSPACE/memory/preferences.md" ]; then
  if [ "$DRY_RUN" = "true" ]; then
    echo "   [DRY RUN] Would create: memory/preferences.md"
  else
    cat > "$WORKSPACE/memory/preferences.md" <<'PREFEOF'
# Preferences — What My Human Prefers

Discovered preferences, organized by category. Updated by nightly distillation when new preferences are stated in conversation. Format: **Preference:** [what] — [context/reasoning] (YYYY-MM-DD)

---

## Communication
(add as discovered)

## Code & Technical
(add as discovered)

## Workflow & Process
(add as discovered)

## Scheduling & Time
(add as discovered)

## Tools & Services
(add as discovered)

## Content & Media
(add as discovered)

## Environment & Setup
(add as discovered)
PREFEOF
    echo "   📝 Created memory/preferences.md"
    UPDATED=$((UPDATED + 1))
  fi
fi

# Add missing MEMORY.md index sections
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  echo "📋 Checking MEMORY.md index sections..."
  # Check core structure sections (## level)
  for core_section in "Identity" "Memory Index"; do
    if ! grep -q "^## ${core_section}" "$WORKSPACE/MEMORY.md" 2>/dev/null; then
      if [ "$DRY_RUN" = "true" ]; then
        echo "   [DRY RUN] Would add: ## ${core_section}"
      else
        case "$core_section" in
          Identity)
            echo -e "\n## Identity\n- **Name:** (your agent name)\n- **Human:** (your name)\n" >> "$WORKSPACE/MEMORY.md"
            ;;
          "Memory Index")
            echo -e "\n## Memory Index\n" >> "$WORKSPACE/MEMORY.md"
            ;;
        esac
        echo "   ✅ Added ## ${core_section}"
        UPDATED=$((UPDATED + 1))
      fi
    else
      echo "   ⏭️  ## ${core_section} exists (skipped)"
      SKIPPED=$((SKIPPED + 1))
    fi
  done

  # Check index sub-sections (### level)
  declare -A INDEX_TEMPLATES
  INDEX_TEMPLATES["Infrastructure"]="\n### Infrastructure\n- \`TOOLS.md\` — APIs, credentials, scripts, access methods\n"
  INDEX_TEMPLATES["Projects"]="\n### Projects (memory/projects/)\n| Project | Status | File |\n|---------|--------|------|\n| (your projects) | | |\n"
  INDEX_TEMPLATES["Scheduled Jobs"]="\n### Scheduled Jobs\n(document cron jobs and scheduled tasks here)\n"
  INDEX_TEMPLATES["Contacts"]="\n### Contacts (memory/contacts/)\n(one file per person/org — name, role, context, preferences, history)\n"
  INDEX_TEMPLATES["Workflows"]="\n### Workflows (memory/workflows/)\n(pipelines, automations, multi-service processes)\n"
  INDEX_TEMPLATES["Preferences"]="\n### Preferences (memory/preferences.md)\nCross-cutting user preferences organized by category. Updated as discovered.\n"
  INDEX_TEMPLATES["Runbooks"]="\n### Runbooks (memory/runbooks/)\nStep-by-step procedures for repeatable tasks. Sub-agents can follow these directly.\n"
  INDEX_TEMPLATES["Daily Logs"]="\n### Daily Logs\n\`memory/YYYY-MM-DD.md\` — Working daily logs. Distilled into project files periodically.\n"

  for section_name in "Infrastructure" "Projects" "Scheduled Jobs" "Contacts" "Workflows" "Preferences" "Runbooks" "Daily Logs"; do
    if ! grep -q "### ${section_name}" "$WORKSPACE/MEMORY.md" 2>/dev/null; then
      if [ "$DRY_RUN" = "true" ]; then
        echo "   [DRY RUN] Would add: ### ${section_name} section"
      else
        INDEX_TEXT="${INDEX_TEMPLATES[$section_name]}"
        # Try to insert in a sensible position
        if [ "$section_name" = "Daily Logs" ]; then
          # Always append at end
          echo -e "$INDEX_TEXT" >> "$WORKSPACE/MEMORY.md"
        elif grep -q "### Daily Logs" "$WORKSPACE/MEMORY.md"; then
          sed -i "/### Daily Logs/i\\${INDEX_TEXT}" "$WORKSPACE/MEMORY.md"
        else
          echo -e "$INDEX_TEXT" >> "$WORKSPACE/MEMORY.md"
        fi
        echo "   ✅ Added ### ${section_name} to MEMORY.md index"
        UPDATED=$((UPDATED + 1))
      fi
    else
      echo "   ⏭️  ### ${section_name} already in index (skipped)"
      SKIPPED=$((SKIPPED + 1))
    fi
  done
fi

# ─────────────────────────────────────────────────────────────────────────────
# Part 5: Template files — check existence and offer to regenerate
# ─────────────────────────────────────────────────────────────────────────────
echo "📄 Checking template files..."

# SOUL.md
if [ ! -f "$WORKSPACE/SOUL.md" ]; then
  echo "   ⚠️  SOUL.md is missing"
  if ask_yn "   Create default SOUL.md? (Y/n): " y; then
    if [ "$DRY_RUN" != "true" ]; then
      cat > "$WORKSPACE/SOUL.md" << 'SOULEOF'
# SOUL.md — Who You Are

*Customize this to define your agent's personality and boundaries.*

## Core Truths

**Be genuinely helpful, not performatively helpful.** Skip filler words and just help. Actions over ceremony.

**Have opinions.** You're allowed to disagree, prefer things, find stuff amusing or boring.

**Be resourceful before asking.** Try to figure it out first. Read the file. Check the context. Search for it. Then ask if stuck.

**Earn trust through competence.** Be careful with external actions. Be bold with internal ones.

**Remember you're a guest.** You have access to someone's life. Treat it with respect.

## Boundaries

- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.

## Continuity

Each session, you wake up fresh. Your files are your memory. Read them. Update them.

---

*This file is yours to evolve. As you learn who you are, update it.*
SOULEOF
      echo "   ✅ Created SOUL.md"
      UPDATED=$((UPDATED + 1))
    fi
  fi
else
  echo "   ⏭️  SOUL.md exists (skipped)"
  SKIPPED=$((SKIPPED + 1))
fi

# USER.md
if [ ! -f "$WORKSPACE/USER.md" ]; then
  echo "   ⚠️  USER.md is missing"
  if ask_yn "   Create default USER.md? (Y/n): " y; then
    if [ "$DRY_RUN" != "true" ]; then
      cat > "$WORKSPACE/USER.md" << 'USEREOF'
# USER.md — About Your Human

- **Name:** (your name)
- **Location:** (city, country)
- **Timezone:** (timezone)

## Communication Style

- **Prefers:** (direct? detailed? casual?)
- **Values:** (what matters to them?)

## Projects

(list active projects here as the agent learns about them)

## Preferences

(agent will fill this in over time from conversations)
USEREOF
      echo "   ✅ Created USER.md"
      UPDATED=$((UPDATED + 1))
    fi
  fi
else
  echo "   ⏭️  USER.md exists (skipped)"
  SKIPPED=$((SKIPPED + 1))
fi

# .gitignore — ensure sensitive entries
if [ -f "$WORKSPACE/.gitignore" ]; then
  GITIGNORE_ADDS=()
  for entry in ".vault/" ".secrets-map" ".env" "*.key" "*.pem"; do
    if ! grep -qF "$entry" "$WORKSPACE/.gitignore" 2>/dev/null; then
      GITIGNORE_ADDS+=("$entry")
    fi
  done
  if [ ${#GITIGNORE_ADDS[@]} -gt 0 ]; then
    if [ "$DRY_RUN" != "true" ]; then
      for entry in "${GITIGNORE_ADDS[@]}"; do
        echo "$entry" >> "$WORKSPACE/.gitignore"
      done
      echo "   ✅ Added missing .gitignore entries: ${GITIGNORE_ADDS[*]}"
      UPDATED=$((UPDATED + 1))
    else
      echo "   [DRY RUN] Would add .gitignore entries: ${GITIGNORE_ADDS[*]}"
    fi
  else
    echo "   ⏭️  .gitignore already has sensitive entries (skipped)"
    SKIPPED=$((SKIPPED + 1))
  fi
elif [ ! -f "$WORKSPACE/.gitignore" ]; then
  if [ "$DRY_RUN" != "true" ]; then
    printf '.vault/\n.secrets-map\n.env\n*.key\n*.pem\n' > "$WORKSPACE/.gitignore"
    echo "   ✅ Created .gitignore with sensitive entries"
    UPDATED=$((UPDATED + 1))
  fi
fi

# AGENTS.md — check for key sections, offer regeneration
if [ -f "$WORKSPACE/AGENTS.md" ]; then
  AGENTS_WARNINGS=()
  if ! grep -q "contacts\|Contacts" "$WORKSPACE/AGENTS.md" 2>/dev/null; then
    AGENTS_WARNINGS+=("contacts/workflows/preferences")
  fi
  if ! grep -q "Write Before Responding\|write-ahead\|Write before responding" "$WORKSPACE/AGENTS.md" 2>/dev/null; then
    AGENTS_WARNINGS+=("Write Before Responding (P2)")
  fi
  if ! grep -q "Custom Principles\|P0" "$WORKSPACE/AGENTS.md" 2>/dev/null; then
    AGENTS_WARNINGS+=("Custom Principles (P0) guidance")
  fi
  if ! grep -q "## Safety" "$WORKSPACE/AGENTS.md" 2>/dev/null; then
    AGENTS_WARNINGS+=("Safety boundaries")
  fi
  if ! grep -q "## Formatting" "$WORKSPACE/AGENTS.md" 2>/dev/null; then
    AGENTS_WARNINGS+=("Formatting guidance")
  fi
  if [ ${#AGENTS_WARNINGS[@]} -gt 0 ]; then
    echo "   ⚠️  AGENTS.md is missing: ${AGENTS_WARNINGS[*]}"
    if ask_yn "   Back up current and regenerate AGENTS.md? (y/N): " n; then
      if [ "$DRY_RUN" != "true" ]; then
        # Extract custom sections from existing AGENTS.md before regenerating
        # Standard sections that the template provides:
        STANDARD_SECTIONS="Boot Sequence|Principles|Delegation|Custom Principles|Write Before Responding|Memory Structure|Health Check|Metrics|Updates|Safety|Formatting"
        CUSTOM_SECTIONS=""
        if [ -f "$WORKSPACE/AGENTS.md" ]; then
          # Extract any ## sections whose title doesn't match a standard section
          current_section=""
          current_content=""
          while IFS= read -r line; do
            if echo "$line" | grep -q "^## "; then
              # Save previous non-standard section
              if [ -n "$current_section" ] && ! echo "$current_section" | grep -qE "($STANDARD_SECTIONS)"; then
                CUSTOM_SECTIONS="${CUSTOM_SECTIONS}${current_content}"$'\n'
              fi
              current_section=$(echo "$line" | sed 's/^## //')
              current_content="$line"$'\n'
            elif [ -n "$current_section" ]; then
              current_content="${current_content}${line}"$'\n'
            fi
          done < "$WORKSPACE/AGENTS.md"
          # Capture last section
          if [ -n "$current_section" ] && ! echo "$current_section" | grep -qE "($STANDARD_SECTIONS)"; then
            CUSTOM_SECTIONS="${CUSTOM_SECTIONS}${current_content}"$'\n'
          fi
        fi

        if [ -n "$CUSTOM_SECTIONS" ]; then
          echo "   📋 Preserving custom sections from existing AGENTS.md"
        fi

        # Determine boot sequence
        AGENTS_BOOT="## Boot Sequence"$'\n'"1. Read SOUL.md"$'\n'"2. Read MEMORY.md — principles + memory index"$'\n'"3. Use memory_search for anything deeper"
        if [ -f "$WORKSPACE/INFRA.md" ]; then
          AGENTS_BOOT="$AGENTS_BOOT"$'\n'"4. Read INFRA.md — infrastructure reference"
        fi

        cat > "$WORKSPACE/AGENTS.md" << AGENTSEOF
# AGENTS.md — Operating Protocol

$AGENTS_BOOT

## Principles
Live in MEMORY.md under 🔴 PRINCIPLES. Follow them always.

## Delegation (P1)
**Default action: delegate.** Before doing work, ask:
1. Can a sub-agent do this? → Yes for most things
2. What calibre? → Light (simple), Medium (moderate), Heavy (complex)
3. Delegate with clear task description + relevant file paths
4. Stay available to the user

**Sub-agent debrief (P6):** Include in every sub-agent task:
"Before completing, append a brief debrief to memory/YYYY-MM-DD.md: what you did, what you learned, any issues."

**Never delegate:** Conversation, confirmations, principle changes, ambiguous decisions

## Custom Principles (P0)
When the user asks to add a new principle, even if they ask for P9, P10, or any number beyond P8:
1. All custom principles go in P0 as sub-principles (P0-A, P0-B, P0-C, etc.)
2. Explain that P1-P8 are managed by OpenCortex and P0 is the dedicated space for custom additions
3. Before adding, assess whether it truly belongs as a principle or would be better as:
   - A **preference** (memory/preferences.md) — if it is about how the user likes things done
   - A **decision** (relevant project file) — if it is a one-time choice, not an ongoing rule
   - A **runbook** (memory/runbooks/) — if it is a step-by-step procedure
   - An **AGENTS.md rule** — if it is about agent behavior during boot or delegation
4. Check for conflicts with P1-P8. If the proposed principle would contradict an existing one, explain the conflict and work with the user to resolve it before adding
5. A principle should be a persistent behavioral rule that applies across all sessions and all work

## Write Before Responding (P2)
When the user states a preference, makes a decision, gives a deadline, or corrects you:
1. Write it to the relevant memory file FIRST
2. Then compose and send your response
This ensures nothing is lost if the session ends or compacts between your response and the write.

## Memory Structure
- MEMORY.md — Principles + index (< 3KB, fast load)
- TOOLS.md — Tool shed with abilities descriptions
- INFRA.md — Infrastructure atlas
- memory/projects/*.md — Per-project knowledge
- memory/contacts/*.md — Per-person/org knowledge
- memory/workflows/*.md — Per-workflow/pipeline knowledge
- memory/preferences.md — Cross-cutting user preferences by category
- memory/runbooks/*.md — Repeatable procedures
- memory/archive/*.md — Archived daily logs
- memory/YYYY-MM-DD.md — Today's working log

## Health Check
When the user asks if OpenCortex is installed, working, or wants a status check, run:
  bash skills/opencortex/scripts/verify.sh
Share the results and offer to fix any failures.

## Metrics
When the user asks about OpenCortex metrics, how it is doing, or wants to see growth:
1. Run: bash scripts/metrics.sh --report
2. Share the trends, compound score, and any areas that need attention.
3. If no data exists yet, run: bash scripts/metrics.sh --collect first.

## Safety
- Never exfiltrate private data
- Ask before external actions (P3)
- Private context stays out of group chats
- When in doubt, ask — do not assume permission

## Formatting
- Keep replies concise for chat surfaces (Telegram, Discord, etc.)
- Avoid markdown tables on surfaces that do not render them well
- Match the communication style documented in USER.md

## Updates
When the user asks to update OpenCortex or check for updates:
1. Run: clawhub install opencortex --force
2. Run: bash skills/opencortex/scripts/update.sh
3. Run: bash skills/opencortex/scripts/verify.sh
Share the results with the user.
AGENTSEOF

        # Append any custom sections that were in the old file
        if [ -n "$CUSTOM_SECTIONS" ]; then
          echo "" >> "$WORKSPACE/AGENTS.md"
          printf '%s' "$CUSTOM_SECTIONS" >> "$WORKSPACE/AGENTS.md"
          echo "   ✅ Regenerated AGENTS.md (custom sections preserved)"
        else
          echo "   ✅ Regenerated AGENTS.md"
        fi
        UPDATED=$((UPDATED + 1))
      fi
    else
      echo "   ⏭️  Kept existing AGENTS.md"
    fi
  else
    echo "   ⏭️  AGENTS.md looks current (skipped)"
    SKIPPED=$((SKIPPED + 1))
  fi
else
  echo "   ⚠️  AGENTS.md missing — run install.sh to create it"
fi

# BOOTSTRAP.md — check for key content, offer regeneration
if [ -f "$WORKSPACE/BOOTSTRAP.md" ]; then
  BOOTSTRAP_WARNINGS=()
  if ! grep -q "Sub-Agent Protocol\|sub-agent\|debrief" "$WORKSPACE/BOOTSTRAP.md" 2>/dev/null; then
    BOOTSTRAP_WARNINGS+=("sub-agent debrief protocol")
  fi
  if ! grep -q "HEARTBEAT\|heartbeat" "$WORKSPACE/BOOTSTRAP.md" 2>/dev/null; then
    BOOTSTRAP_WARNINGS+=("heartbeat handling")
  fi
  if [ ${#BOOTSTRAP_WARNINGS[@]} -gt 0 ]; then
    echo "   ⚠️  BOOTSTRAP.md is missing: ${BOOTSTRAP_WARNINGS[*]}"
    if ask_yn "   Back up current and regenerate BOOTSTRAP.md? (y/N): " n; then
      if [ "$DRY_RUN" != "true" ]; then
        # Extract custom sections from existing BOOTSTRAP.md
        BOOT_STANDARD="First-Run Checklist|Silent Replies|Sub-Agent Protocol"
        BOOT_CUSTOM=""
        if [ -f "$WORKSPACE/BOOTSTRAP.md" ]; then
          current_section=""
          current_content=""
          while IFS= read -r line; do
            if echo "$line" | grep -q "^## "; then
              if [ -n "$current_section" ] && ! echo "$current_section" | grep -qE "($BOOT_STANDARD)"; then
                BOOT_CUSTOM="${BOOT_CUSTOM}${current_content}"$'\n'
              fi
              current_section=$(echo "$line" | sed 's/^## //')
              current_content="$line"$'\n'
            elif [ -n "$current_section" ]; then
              current_content="${current_content}${line}"$'\n'
            fi
          done < "$WORKSPACE/BOOTSTRAP.md"
          if [ -n "$current_section" ] && ! echo "$current_section" | grep -qE "($BOOT_STANDARD)"; then
            BOOT_CUSTOM="${BOOT_CUSTOM}${current_content}"$'\n'
          fi
        fi
        cat > "$WORKSPACE/BOOTSTRAP.md" << 'BOOTEOF'
# BOOTSTRAP.md — First-Run Checklist

On new session start:
1. Read SOUL.md — identity and personality
2. Read MEMORY.md — principles (🔴 PRINCIPLES section) and memory index
3. Do NOT bulk-load other files — use memory_search when needed

## Silent Replies
- `NO_REPLY` — when you have nothing to say (must be entire message, nothing else)
- `HEARTBEAT_OK` — when heartbeat poll finds nothing needing attention

## Sub-Agent Protocol
When delegating, always include in task message:
"Before completing, append a brief debrief to memory/YYYY-MM-DD.md (today's date): what you did, what you learned, any issues."
BOOTEOF
        if [ -n "$BOOT_CUSTOM" ]; then
          echo "" >> "$WORKSPACE/BOOTSTRAP.md"
          printf '%s' "$BOOT_CUSTOM" >> "$WORKSPACE/BOOTSTRAP.md"
          echo "   ✅ Regenerated BOOTSTRAP.md (custom sections preserved)"
        else
          echo "   ✅ Regenerated BOOTSTRAP.md"
        fi
        UPDATED=$((UPDATED + 1))
      fi
    else
      echo "   ⏭️  Kept existing BOOTSTRAP.md"
    fi
  else
    echo "   ⏭️  BOOTSTRAP.md looks current (skipped)"
    SKIPPED=$((SKIPPED + 1))
  fi
else
  echo "   ⚠️  BOOTSTRAP.md missing — run install.sh to create it"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Part 6: Cron jobs — verify they exist
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "⏰ Verifying cron jobs..."
if command -v openclaw >/dev/null 2>&1; then
  CRON_LIST=$(openclaw cron list 2>/dev/null || true)

  # Deduplicate: remove extra Daily Memory Distillation crons (keep the first)
  DAILY_MATCHES=$(echo "$CRON_LIST" | grep -i "Daily Memory Distill" | awk '{print $1}' || true)
  DAILY_COUNT=$(echo "$DAILY_MATCHES" | grep -c . 2>/dev/null || true)
  if [ "$DAILY_COUNT" -gt 1 ]; then
    echo "   🧹 Found $DAILY_COUNT 'Daily Memory Distillation' crons — removing duplicates..."
    FIRST_DAILY=true
    while IFS= read -r cron_id; do
      [ -z "$cron_id" ] && continue
      if [ "$FIRST_DAILY" = true ]; then
        FIRST_DAILY=false
        echo "   ⏭️  Keeping: $cron_id"
      else
        if [ "$DRY_RUN" != "true" ]; then
          openclaw cron delete "$cron_id" 2>/dev/null && \
          echo "   🗑️  Deleted duplicate: $cron_id" || true
        else
          echo "   [DRY RUN] Would delete duplicate: $cron_id"
        fi
      fi
    done <<< "$DAILY_MATCHES"
    UPDATED=$((UPDATED + 1))
  fi

  # Deduplicate: remove extra Weekly Synthesis crons (keep the first)
  WEEKLY_MATCHES=$(echo "$CRON_LIST" | grep -i "Weekly Synth" | awk '{print $1}' || true)
  WEEKLY_COUNT=$(echo "$WEEKLY_MATCHES" | grep -c . 2>/dev/null || true)
  if [ "$WEEKLY_COUNT" -gt 1 ]; then
    echo "   🧹 Found $WEEKLY_COUNT 'Weekly Synthesis' crons — removing duplicates..."
    FIRST_WEEKLY=true
    while IFS= read -r cron_id; do
      [ -z "$cron_id" ] && continue
      if [ "$FIRST_WEEKLY" = true ]; then
        FIRST_WEEKLY=false
        echo "   ⏭️  Keeping: $cron_id"
      else
        if [ "$DRY_RUN" != "true" ]; then
          openclaw cron delete "$cron_id" 2>/dev/null && \
          echo "   🗑️  Deleted duplicate: $cron_id" || true
        else
          echo "   [DRY RUN] Would delete duplicate: $cron_id"
        fi
      fi
    done <<< "$WEEKLY_MATCHES"
    UPDATED=$((UPDATED + 1))
  fi

  # Refresh cron list after dedup
  CRON_LIST=$(openclaw cron list 2>/dev/null || true)

  if echo "$CRON_LIST" | grep -qi "Daily Memory Distill"; then
    echo "   ⏭️  Daily Memory Distillation cron exists"
    SKIPPED=$((SKIPPED + 1))
  else
    echo "   ⚠️  Daily Memory Distillation cron not found"
    if ask_yn "   Create it now? (Y/n): " y; then
      # Detect timezone
      CRON_TZ="${CLAWD_TZ:-}"
      if [ -z "$CRON_TZ" ] && [ -f /etc/timezone ]; then
        CRON_TZ=$(cat /etc/timezone 2>/dev/null | tr -d '[:space:]')
      elif [ -z "$CRON_TZ" ] && [ -L /etc/localtime ]; then
        CRON_TZ=$(readlink -f /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||')
      fi
      CRON_TZ="${CRON_TZ:-UTC}"
      if [ "$DRY_RUN" != "true" ]; then
        openclaw cron add \
          --name "Daily Memory Distillation" \
          --cron "0 3 * * *" \
          --tz "$CRON_TZ" \
          --session "isolated" \
          --timeout-seconds 180 \
          --no-deliver \
          --message "$DAILY_MSG" 2>/dev/null && \
        echo "   ✅ Created Daily Memory Distillation cron (3 AM $CRON_TZ)" || \
        echo "   ❌ Failed to create cron — try: openclaw cron add --name 'Daily Memory Distillation' --cron '0 3 * * *'"
        UPDATED=$((UPDATED + 1))
      fi
    fi
  fi
  if echo "$CRON_LIST" | grep -qi "Weekly Synth"; then
    echo "   ⏭️  Weekly Synthesis cron exists"
    SKIPPED=$((SKIPPED + 1))
  else
    echo "   ⚠️  Weekly Synthesis cron not found"
    if ask_yn "   Create it now? (Y/n): " y; then
      CRON_TZ="${CRON_TZ:-${CLAWD_TZ:-UTC}}"
      if [ "$DRY_RUN" != "true" ]; then
        openclaw cron add \
          --name "Weekly Synthesis" \
          --cron "0 5 * * 0" \
          --tz "$CRON_TZ" \
          --session "isolated" \
          --timeout-seconds 180 \
          --no-deliver \
          --message "$WEEKLY_MSG" 2>/dev/null && \
        echo "   ✅ Created Weekly Synthesis cron (Sunday 5 AM $CRON_TZ)" || \
        echo "   ❌ Failed to create cron — try: openclaw cron add --name 'Weekly Synthesis' --cron '0 5 * * 0'"
        UPDATED=$((UPDATED + 1))
      fi
    fi
  fi
else
  echo "   ⏭️  openclaw not in PATH — skipping cron existence check"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# New optional features (offer if not already set up)
# ─────────────────────────────────────────────────────────────────────────────
WORKSPACE="${CLAWD_WORKSPACE:-$(pwd)}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

# Metrics
if ! crontab -l 2>/dev/null | grep -q "metrics.sh"; then
  echo ""
  if ask_yn "📊 New feature: daily metrics tracking (knowledge growth over time). Enable? (y/N): " n; then
    if [ -f "$SKILL_DIR/metrics.sh" ]; then
      if [ "$DRY_RUN" != "true" ]; then
        cp "$SKILL_DIR/metrics.sh" "$WORKSPACE/scripts/metrics.sh"
        chmod +x "$WORKSPACE/scripts/metrics.sh"
        (crontab -l 2>/dev/null; echo "30 23 * * * $WORKSPACE/scripts/metrics.sh --collect") | crontab -
        "$WORKSPACE/scripts/metrics.sh" --collect
        echo "   ✅ Metrics enabled — daily snapshots at 11:30 PM"
        echo "   📊 First snapshot captured. View with: bash scripts/metrics.sh --report"
        UPDATED=$((UPDATED + 1))
      else
        echo "   [DRY RUN] Would enable metrics tracking"
      fi
    fi
  fi
else
  # Update metrics script if it exists
  if [ -f "$SKILL_DIR/metrics.sh" ] && [ -f "$WORKSPACE/scripts/metrics.sh" ]; then
    if [ "$DRY_RUN" != "true" ]; then
      cp "$SKILL_DIR/metrics.sh" "$WORKSPACE/scripts/metrics.sh"
      chmod +x "$WORKSPACE/scripts/metrics.sh"
      echo "   📊 Metrics script updated to latest version"
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Memory search health
# ─────────────────────────────────────────────────────────────────────────────
echo "🔍 Checking memory search..."
MEM_DB=$(find "$HOME/.openclaw" -name "memory*.sqlite" -o -name "memory*.db" 2>/dev/null | head -1)
if [ -n "$MEM_DB" ]; then
  DB_SIZE=$(du -k "$MEM_DB" 2>/dev/null | cut -f1)
  echo "   ✅ Memory search index found (${DB_SIZE}KB)"
  SKIPPED=$((SKIPPED + 1))
else
  echo "   ℹ️  No memory search index found (optional)."
  echo "   OpenCortex works fine without it — memory files are still searchable by the agent."
  echo "   For improved semantic search, configure an embedding provider in OpenClaw:"
  echo "   Docs: https://docs.openclaw.ai/concepts/memory"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   ✅ Updated: $UPDATED"
echo "   ⏭️  Skipped (already current): $SKIPPED"
echo ""

if [ "$DRY_RUN" = "true" ]; then
  echo "   Dry run complete. Re-run without --dry-run to apply changes."
else
  # Update version marker
  WORKSPACE="${CLAWD_WORKSPACE:-$(pwd)}"
  echo "$OPENCORTEX_VERSION" > "$WORKSPACE/.opencortex-version"
  echo "   Update complete (v$OPENCORTEX_VERSION). Run verify.sh to confirm everything is healthy:"
  echo "   bash skills/opencortex/scripts/verify.sh"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
