#!/bin/sh
# Style & memory benchmark (baseline): writing style, addressing, preferences, habits, admin.
# One mixed file; agent loads full file to answer "how do I write Gmail?" etc.
set -e
BENCH_DIR="${1:-/tmp/bench-style-baseline}"
METRICS_OUT="${2:-$BENCH_DIR/metrics-style-baseline.json}"
mkdir -p "$BENCH_DIR"
cd "$BENCH_DIR"

mkdir -p .learnings
# Single mixed file: writing style, addressing, preferences, habits, admin/social memory
cat > .learnings/PREFERENCES.md << 'PREFS'
# Preferences & memory (baseline: one mixed file)

## Writing style (application-specific)
- **Gmail / email:** Professional but warm. Full sentences, clear sign-off.
- **Twitter / tweets:** Concise, casual. Short punchy lines. Hashtags when relevant.
- **Slack internal:** Informal, colleagues. Emoji OK.

## Addressing (friends vs colleagues vs managers vs customers)
- **Customers:** Dear [Name] or Hello [Name]. Formal tone.
- **Managers:** Use title and last name (e.g. Dr. Smith, Ms. Chen) until told otherwise.
- **Colleagues:** First name. Casual.
- **Friends:** First name or nickname. Very casual.

## Personal preferences
- Prefer morning standups (before 10am).
- Prefer bullet points over long paragraphs for updates.
- Prefer async Slack over ad-hoc meetings when possible.

## Habits
- User reviews calendar at start of day.
- User likes action items at end of long messages.
- User prefers short subject lines in email.

## Administrative / social memory
- Manager: Sarah Chen. Team lead: Alex Rivera.
- Team uses Slack for async, Zoom for weekly sync.
- Key customer contacts in CRM; always check before cold outreach.
PREFS

# To answer any one "style/memory" question, agent typically loads the whole file
BASELINE_STYLE_CHARS=$(cat .learnings/PREFERENCES.md | wc -c | tr -d ' ')

# Needles for 6 scenarios (must appear in file for "found")
# 1 Gmail voice, 2 Twitter voice, 3 address customer, 4 address manager, 5 colleague, 6 standup preference
BASELINE_FOUND_1=0; grep -qi "professional.*warm\|Gmail" .learnings/PREFERENCES.md && BASELINE_FOUND_1=1
BASELINE_FOUND_2=0; grep -qi "concise.*casual\|Twitter" .learnings/PREFERENCES.md && BASELINE_FOUND_2=1
BASELINE_FOUND_3=0; grep -qi "Dear\|customer" .learnings/PREFERENCES.md && BASELINE_FOUND_3=1
BASELINE_FOUND_4=0; grep -qi "title.*last\|manager\|Ms\.\|Dr\." .learnings/PREFERENCES.md && BASELINE_FOUND_4=1
BASELINE_FOUND_5=0; grep -qi "first name\|colleague\|casual" .learnings/PREFERENCES.md && BASELINE_FOUND_5=1
BASELINE_FOUND_6=0; grep -qi "morning.*standup\|standup" .learnings/PREFERENCES.md && BASELINE_FOUND_6=1
BASELINE_FOUND_TOTAL=$((BASELINE_FOUND_1 + BASELINE_FOUND_2 + BASELINE_FOUND_3 + BASELINE_FOUND_4 + BASELINE_FOUND_5 + BASELINE_FOUND_6))

printf '%s' "{
  \"style_memory_chars\": $BASELINE_STYLE_CHARS,
  \"scenarios_found\": $BASELINE_FOUND_TOTAL,
  \"scenarios\": 6
}" > "$METRICS_OUT"
echo "style_memory_chars=$BASELINE_STYLE_CHARS scenarios_found=$BASELINE_FOUND_TOTAL/6"
