#!/bin/sh
# Style & memory benchmark (Mulch): writing style, addressing, preferences, habits, admin.
# Domains per category; targeted search per scenario.
set -e
BENCH_DIR="${1:-/tmp/bench-style-mulch}"
METRICS_OUT="${2:-$BENCH_DIR/metrics-style-mulch.json}"
MULCH="npx --yes mulch-cli"
mkdir -p "$BENCH_DIR"
cd "$BENCH_DIR"

$MULCH init
$MULCH add writing_style
$MULCH add addressing
$MULCH add preferences
$MULCH add habits
$MULCH add admin

# Writing style (application-specific)
$MULCH record writing_style --type convention "Gmail/email: professional but warm. Full sentences, clear sign-off."
$MULCH record writing_style --type convention "Twitter/tweets: concise, casual. Short punchy lines. Hashtags when relevant."
$MULCH record writing_style --type convention "Slack internal: informal, colleagues. Emoji OK."

# Addressing (friends vs colleagues vs managers vs customers)
$MULCH record addressing --type convention "Customers: Dear [Name] or Hello [Name]. Formal tone."
$MULCH record addressing --type convention "Managers: Use title and last name (e.g. Dr. Smith, Ms. Chen) until told otherwise."
$MULCH record addressing --type convention "Colleagues: First name. Casual."
$MULCH record addressing --type convention "Friends: First name or nickname. Very casual."

# Personal preferences & habits
$MULCH record preferences --type convention "Prefer morning standups (before 10am). Bullet points over long paragraphs."
$MULCH record preferences --type convention "Prefer async Slack over ad-hoc meetings when possible."
$MULCH record habits --type convention "User reviews calendar at start of day. Likes action items at end of long messages."
$MULCH record habits --type convention "User prefers short subject lines in email."

# Administrative / social memory
$MULCH record admin --type convention "Manager: Sarah Chen. Team lead: Alex Rivera. Team uses Slack for async, Zoom for weekly sync."

# 6 retrieval scenarios (same as baseline)
MULCH_OUT_1=$($MULCH search "Gmail email style" 2>/dev/null || echo "")
MULCH_OUT_2=$($MULCH search "Twitter tweet style" 2>/dev/null || echo "")
MULCH_OUT_3=$($MULCH search "address customer" 2>/dev/null || echo "")
MULCH_OUT_4=$($MULCH search "address manager" 2>/dev/null || echo "")
MULCH_OUT_5=$($MULCH search "colleague" 2>/dev/null || echo "")
MULCH_OUT_6=$($MULCH search "standup preference" 2>/dev/null || echo "")

MULCH_CHARS_1=$(printf '%s' "$MULCH_OUT_1" | wc -c | tr -d ' ')
MULCH_CHARS_2=$(printf '%s' "$MULCH_OUT_2" | wc -c | tr -d ' ')
MULCH_CHARS_3=$(printf '%s' "$MULCH_OUT_3" | wc -c | tr -d ' ')
MULCH_CHARS_4=$(printf '%s' "$MULCH_OUT_4" | wc -c | tr -d ' ')
MULCH_CHARS_5=$(printf '%s' "$MULCH_OUT_5" | wc -c | tr -d ' ')
MULCH_CHARS_6=$(printf '%s' "$MULCH_OUT_6" | wc -c | tr -d ' ')
MULCH_STYLE_CHARS=$((MULCH_CHARS_1 + MULCH_CHARS_2 + MULCH_CHARS_3 + MULCH_CHARS_4 + MULCH_CHARS_5 + MULCH_CHARS_6))

# Needles (same as baseline)
MULCH_FOUND_1=0; echo "$MULCH_OUT_1" | grep -qi "professional.*warm\|Gmail" && MULCH_FOUND_1=1
MULCH_FOUND_2=0; echo "$MULCH_OUT_2" | grep -qi "concise.*casual\|Twitter" && MULCH_FOUND_2=1
MULCH_FOUND_3=0; echo "$MULCH_OUT_3" | grep -qi "Dear\|customer" && MULCH_FOUND_3=1
MULCH_FOUND_4=0; echo "$MULCH_OUT_4" | grep -qi "title.*last\|manager\|Ms\.\|Dr\." && MULCH_FOUND_4=1
MULCH_FOUND_5=0; echo "$MULCH_OUT_5" | grep -qi "first name\|colleague\|casual" && MULCH_FOUND_5=1
MULCH_FOUND_6=0; echo "$MULCH_OUT_6" | grep -qi "morning.*standup\|standup" && MULCH_FOUND_6=1
MULCH_FOUND_TOTAL=$((MULCH_FOUND_1 + MULCH_FOUND_2 + MULCH_FOUND_3 + MULCH_FOUND_4 + MULCH_FOUND_5 + MULCH_FOUND_6))

printf '%s' "{
  \"style_memory_chars\": $MULCH_STYLE_CHARS,
  \"scenarios_found\": $MULCH_FOUND_TOTAL,
  \"scenarios\": 6
}" > "$METRICS_OUT"
echo "style_memory_chars=$MULCH_STYLE_CHARS scenarios_found=$MULCH_FOUND_TOTAL/6"
