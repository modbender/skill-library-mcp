#!/bin/bash
# Memory Maintenance Agent v2 - Enhanced Review
# Reviews: daily notes + memory directory health + file organization
# Triggered daily at 23:00 via OpenClaw cron
# Outputs suggestions for human review; NEVER auto-applies

set -e

# Load environment
if [ -f "/Users/maxhutchinson/.openclaw/workspace/.env" ]; then
    set -a
    source /Users/maxhutchinson/.openclaw/workspace/.env
    set +a
fi

WORKSPACE="/Users/maxhutchinson/.openclaw/workspace"
OUTPUT_DIR="$WORKSPACE/agents/memory"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d-%H%M)

echo "[$TIMESTAMP] Starting memory maintenance v2 scan..."

# ============================================
# COLLECT DATA FOR REVIEW
# ============================================

# 1. Daily notes from last 7 days (existing)
DAILY_NOTES=""
for i in {0..6}; do
    DAY=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "${i} days ago" +%Y-%m-%d 2>/dev/null)
    NOTE_FILE="$WORKSPACE/memory/${DAY}.md"
    if [ -f "$NOTE_FILE" ]; then
        DAILY_NOTES="${DAILY_NOTES}

=== ${DAY}.md ===

$(cat "$NOTE_FILE")"
    fi
done

# 2. Memory directory inventory
MEMORY_DIR_LIST=$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" -o -name "*.txt" -o -name "*.json" 2>/dev/null | sort)
MEMORY_DIR_COUNT=$(echo "$MEMORY_DIR_LIST" | grep -c "." || echo "0")

# 3. Archive directory status
ARCHIVE_COUNT=$(find "$WORKSPACE/memory/archive" -type f 2>/dev/null | wc -l)

# 4. Files older than 30 days (candidates for archiving)
OLD_FILES=$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" -mtime +30 2>/dev/null | head -20)
OLD_FILES_COUNT=$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" -mtime +30 2>/dev/null | wc -l | tr -d ' ')

# 5. Non-standard files in memory/ (not YYYY-MM-DD.md format)
NON_STANDARD=$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" ! -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md" 2>/dev/null | head -20)
NON_STANDARD_COUNT=$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" ! -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md" 2>/dev/null | wc -l | tr -d ' ')

# 6. Current memory files for context
MEMORY_MD=$(cat "$WORKSPACE/MEMORY.md" 2>/dev/null || echo "")
USER_MD=$(cat "$WORKSPACE/USER.md" 2>/dev/null || echo "")

echo "[$TIMESTAMP] Found:"
echo "  - Daily notes: $(echo "$DAILY_NOTES" | grep -c "=== " || echo 0)"
echo "  - Memory dir files: $MEMORY_DIR_COUNT"
echo "  - Archive files: $ARCHIVE_COUNT"
echo "  - Files >30 days old: $OLD_FILES_COUNT"
echo "  - Non-standard names: $NON_STANDARD_COUNT"

# ============================================
# BUILD COMPREHENSIVE PROMPT
# ============================================

PROMPT=$(cat << 'PROMPTEOF'
TASK: Comprehensive Memory Maintenance Review

You are a memory maintenance agent. Review the workspace memory system and suggest improvements.

REVIEW_SCOPE:
1. Content review (daily notes → MEMORY.md updates)
2. Directory health (file organization, naming, archiving)
3. Data hygiene (duplicates, orphans, bloat)

INPUT DATA:

## Daily Notes (Last 7 Days):
PROMPTEOF
)

echo "$DAILY_NOTES" >> "$OUTPUT_DIR/.prompt.tmp"

cat >> "$OUTPUT_DIR/.prompt.tmp" << 'PROMPTEOF'

## Current MEMORY.md:
PROMPTEOF

echo "$MEMORY_MD" >> "$OUTPUT_DIR/.prompt.tmp"

cat >> "$OUTPUT_DIR/.prompt.tmp" << 'PROMPTEOF'

## Current USER.md:
PROMPTEOF

echo "$USER_MD" >> "$OUTPUT_DIR/.prompt.tmp"

cat >> "$OUTPUT_DIR/.prompt.tmp" << PROMPTEOF

## Memory Directory Status:
- Total files in memory/: $MEMORY_DIR_COUNT
- Files in archive/: $ARCHIVE_COUNT
- Files >30 days old (candidates for archive): $OLD_FILES_COUNT
- Non-standard filenames: $NON_STANDARD_COUNT

## Files Requiring Attention:

### Old Files (>30 days):
$OLD_FILES

### Non-Standard Filenames:
$NON_STANDARD

INSTRUCTIONS:

Generate TWO types of suggestions:

### Type A: Content Updates (to MEMORY.md)
Review daily notes and suggest additions/updates to MEMORY.md sections:
- Significant decisions and reasoning
- New preferences or constraints about Max
- Relationship updates (people, companies)
- Project status changes
- Infrastructure/tool changes
- Lessons learned

### Type B: Directory Maintenance
Review memory/ directory health:
1. **Archive candidates**: Files >30 days old that should move to memory/archive/
2. **Naming violations**: Files not matching YYYY-MM-DD.md pattern (suggest rename or removal)
3. **Orphaned content**: Files not referenced in MEMORY.md that should be integrated or deleted
4. **Consolidation opportunities**: Multiple small files that could merge
5. **Size issues**: Files >100KB that might need splitting

RULES:
- Be conservative - only suggest high-confidence changes
- Prioritize Type A (content) over Type B (cleanup)
- Never suggest deleting content without backup/archive plan
- Cite specific sources for every suggestion
- Flag any contradictions between notes and MEMORY.md

EXIT CRITERIA:
Return valid JSON only with this structure:

{
  "review_date": "YYYY-MM-DD",
  "summary": {
    "daily_notes_reviewed": number,
    "memory_dir_files": number,
    "archive_files": number,
    "issues_found": number,
    "human_readable_summary": "2-3 paragraphs"
  },
  "content_suggestions": [
    {
      "type": "add|update|delete",
      "section": "which MEMORY.md section",
      "current_text": "existing or null",
      "proposed_text": "new text",
      "rationale": "why this matters",
      "sources": ["memory/2026-02-01.md"],
      "confidence": "high|medium|low",
      "priority": "high|medium|low"
    }
  ],
  "maintenance_suggestions": [
    {
      "type": "archive|rename|delete|consolidate",
      "target": "filepath",
      "action": "specific action to take",
      "reason": "why this needs attention",
      "safe_to_auto": boolean,
      "backup_required": boolean
    }
  ],
  "contradictions": [
    {
      "topic": "what contradicts",
      "memory_says": "from MEMORY.md",
      "notes_say": "from daily notes",
      "resolution": "recommended fix"
    }
  ],
  "stats": {
    "content_suggestions_count": number,
    "maintenance_suggestions_count": number,
    "high_priority_count": number,
    "safe_to_auto_count": number
  }
}

Provide JSON only, no markdown code blocks.
PROMPTEOF

PROMPT=$(cat "$OUTPUT_DIR/.prompt.tmp")
rm -f "$OUTPUT_DIR/.prompt.tmp"

# ============================================
# RUN GEMINI ANALYSIS
# ============================================

echo "[$TIMESTAMP] Running Gemini analysis..."
RESULT_FILE=$(mktemp)

if ! gemini --model gemini-2.5-flash "$PROMPT" > "$RESULT_FILE" 2>&1; then
    echo "[$TIMESTAMP] ERROR: Gemini failed"
    cat "$RESULT_FILE"
    rm -f "$RESULT_FILE"
    exit 1
fi

# Extract JSON (handle wrapper text) - macOS compatible
JSON_FILE=$(mktemp)

# Try to extract JSON from markdown code blocks first
if grep -q "^\s*\`\`\`json" "$RESULT_FILE" 2>/dev/null; then
    # Extract content between ```json and ```
    awk '/^\s*```json/{start=1; next} /^\s*```/{if(start){start=0}} start{print}' "$RESULT_FILE" > "$JSON_FILE"
else
    # Extract content between first { and last }
    awk '/\{/{if(!start){start=1; brace=1}} start{buf=buf $0; for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="{")brace++; if(c=="}")brace--; if(brace==0){print buf; buf=""; start=0; break}}}' "$RESULT_FILE" | head -1 > "$JSON_FILE" 2>/dev/null
fi

# If that didn't work, use the whole file
if [ ! -s "$JSON_FILE" ]; then
    cat "$RESULT_FILE" > "$JSON_FILE"
fi

if ! jq empty "$JSON_FILE" 2>/dev/null; then
    echo "[$TIMESTAMP] ERROR: Invalid JSON from Gemini"
    cp "$RESULT_FILE" "$OUTPUT_DIR/error-v2-${TIMESTAMP}.txt"
    rm -f "$RESULT_FILE" "$JSON_FILE"
    exit 1
fi

mv "$JSON_FILE" "$OUTPUT_DIR/review-v2-${DATE}.json"

# ============================================
# GENERATE HUMAN-READABLE REPORT
# ============================================

SUMMARY=$(jq -r '.summary.human_readable_summary // "No summary provided"' "$OUTPUT_DIR/review-v2-${DATE}.json")
CONTENT_COUNT=$(jq '.content_suggestions | length' "$OUTPUT_DIR/review-v2-${DATE}.json")
MAINT_COUNT=$(jq '.maintenance_suggestions | length' "$OUTPUT_DIR/review-v2-${DATE}.json")
HIGH_PRIORITY=$(jq '[.content_suggestions[]? + .maintenance_suggestions[]? | select(.priority == "high" or (.priority == null and .safe_to_auto == false))] | length' "$OUTPUT_DIR/review-v2-${DATE}.json")
SAFE_AUTO=$(jq '[.maintenance_suggestions[] | select(.safe_to_auto == true)] | length' "$OUTPUT_DIR/review-v2-${DATE}.json")

echo "[$TIMESTAMP] Analysis complete:"
echo "  - Content suggestions: $CONTENT_COUNT"
echo "  - Maintenance tasks: $MAINT_COUNT"
echo "  - High priority: $HIGH_PRIORITY"
echo "  - Safe to auto-apply: $SAFE_AUTO"

# Create markdown report
{
echo "# Memory Maintenance Review v2: ${DATE}"
echo ""
echo "## Summary"
echo "$SUMMARY"
echo ""
echo "## Quick Stats"
echo "- **Content suggestions:** $CONTENT_COUNT"
echo "- **Maintenance tasks:** $MAINT_COUNT"
echo "- **High priority:** $HIGH_PRIORITY"
echo "- **Safe to auto-apply:** $SAFE_AUTO"
echo ""
echo "---"
echo ""
echo "## Content Suggestions for MEMORY.md"
echo ""
} > "$OUTPUT_DIR/review-v2-${DATE}.md"

# Add content suggestions
jq -r '.content_suggestions[]? | "
### " + (.priority | ascii_upcase) + ": " + (.type | ascii_upcase) + " - " + .section + "

**Confidence:** " + .confidence + "

**Rationale:** " + .rationale + "

**Current:**
" + (.current_text // "(new addition)") + "

**Proposed:**
" + .proposed_text + "

**Sources:** " + (.sources | join(", ")) + "

---
"' "$OUTPUT_DIR/review-v2-${DATE}.json" >> "$OUTPUT_DIR/review-v2-${DATE}.md"

# Add maintenance section
{
echo ""
echo "## Directory Maintenance Tasks"
echo ""
echo "| Action | Target | Reason | Safe to Auto |"
echo "|--------|--------|--------|--------------|"
} >> "$OUTPUT_DIR/review-v2-${DATE}.md"

jq -r '.maintenance_suggestions[]? | "| " + .type + " | `" + .target + "` | " + .reason + " | " + (if .safe_to_auto then "✅ Yes" else "❌ No" end) + " |"' "$OUTPUT_DIR/review-v2-${DATE}.json" >> "$OUTPUT_DIR/review-v2-${DATE}.md"

# Add contradictions if any
CONTRADICTIONS=$(jq '.contradictions | length' "$OUTPUT_DIR/review-v2-${DATE}.json")
if [ "$CONTRADICTIONS" -gt 0 ]; then
    {
        echo ""
        echo "## ⚠️ Contradictions Found"
        echo ""
    } >> "$OUTPUT_DIR/review-v2-${DATE}.md"
    jq -r '.contradictions[] | "
### " + .topic + "

**MEMORY.md says:** " + .memory_says + "

**Daily notes say:** " + .notes_say + "

**Recommended resolution:** " + .resolution + "

---
"' "$OUTPUT_DIR/review-v2-${DATE}.json" >> "$OUTPUT_DIR/review-v2-${DATE}.md"
fi

# Add actions section
{
echo ""
echo "---"
echo ""
echo "## Next Steps"
echo ""
echo "### To apply content suggestions:"
echo '```bash'
echo "# Review and apply manually, OR:"
echo "Apply memory suggestions from ${DATE}"
echo '```'
echo ""
echo "### To apply maintenance tasks:"
echo '```bash'
echo "# Dry run (see what would happen):"
echo "bash agents/cron/memory-maintenance-apply.sh --dry-run ${DATE}"
echo ""
echo "# Apply safe changes only:"
echo "bash agents/cron/memory-maintenance-apply.sh --safe ${DATE}"
echo ""
echo "# Apply all (including manual review items):"
echo "bash agents/cron/memory-maintenance-apply.sh --all ${DATE}"
echo '```'
echo ""
echo "### To dismiss:"
echo "Tell me: \"Dismiss memory review ${DATE}\""
echo ""
echo "---"
echo ""
echo "*Generated: ${TIMESTAMP}*"
echo "*Review file: agents/memory/review-v2-${DATE}.json*"
} >> "$OUTPUT_DIR/review-v2-${DATE}.md"

# Create alert if high priority items exist
if [ "$HIGH_PRIORITY" -gt 0 ]; then
    {
        echo "# 🔔 Memory Maintenance Alert v2"
        echo ""
        echo "**Date:** ${DATE}"
        echo "**High Priority Items:** ${HIGH_PRIORITY}"
        echo "**Content Suggestions:** ${CONTENT_COUNT}"
        echo "**Maintenance Tasks:** ${MAINT_COUNT}"
        echo ""
        echo "**Quick Actions:**"
        echo "- Read full review: agents/memory/review-v2-${DATE}.md"
        echo "- Apply safe changes: bash agents/cron/memory-maintenance-apply.sh --safe ${DATE}"
        echo "- Review all: Apply memory suggestions from ${DATE}"
    } > "$OUTPUT_DIR/ALERT-review-v2-${DATE}.md"
    echo "[$TIMESTAMP] ALERT created: $OUTPUT_DIR/ALERT-review-v2-${DATE}.md"
fi

# Cleanup
rm -f "$RESULT_FILE"

echo "[$TIMESTAMP] Memory maintenance v2 complete."
echo "[$TIMESTAMP] Review: $OUTPUT_DIR/review-v2-${DATE}.md"
