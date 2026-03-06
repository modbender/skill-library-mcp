#!/bin/bash
# test_memory.sh — Comprehensive test suite for Agent Brain v4
# Run: ./scripts/test_memory.sh
#
# Tests all commands, edge cases, and integration flows.
# Outputs PASS/FAIL for each test with a summary at the end.
# Works with both sqlite and json backends.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_SH="$SCRIPT_DIR/memory.sh"
MEMORY_DIR="$SCRIPT_DIR/../memory"
MEMORY_DB="$MEMORY_DIR/memory.db"
MEMORY_JSON="$MEMORY_DIR/memory.json"
BACKUP_DB="$MEMORY_DIR/memory.backup.db"
BACKUP_JSON="$MEMORY_DIR/memory.backup.json"
BACKUP_JSON_BAK="$MEMORY_DIR/memory.json.bak.backup"
export AGENT_BRAIN_SUPERMEMORY_SYNC="${AGENT_BRAIN_SUPERMEMORY_SYNC:-off}"

# --- Test Framework ---

PASS_COUNT=0
FAIL_COUNT=0
FAIL_DETAILS=""

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  echo "  PASS: $1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  echo "  FAIL: $1"
  FAIL_DETAILS="${FAIL_DETAILS}\n  - $1: $2"
}

assert_contains() {
  local output="$1"
  local expected="$2"
  local test_name="$3"
  if echo "$output" | grep -q "$expected"; then
    pass "$test_name"
  else
    fail "$test_name" "Expected '$expected' in output: $(echo "$output" | head -3)"
  fi
}

assert_not_contains() {
  local output="$1"
  local unexpected="$2"
  local test_name="$3"
  if echo "$output" | grep -q "$unexpected"; then
    fail "$test_name" "Did NOT expect '$unexpected' in output: $(echo "$output" | head -3)"
  else
    pass "$test_name"
  fi
}

assert_exit_code() {
  local actual="$1"
  local expected="$2"
  local test_name="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    pass "$test_name"
  else
    fail "$test_name" "Expected exit code $expected, got $actual"
  fi
}

# Assert a field value from exported JSON
assert_export_field() {
  local query="$1"
  local expected="$2"
  local test_name="$3"
  local actual
  actual=$("$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
result = eval('d' + sys.argv[1])
print(result)
" "$query" 2>&1)
  if [[ "$actual" == "$expected" ]]; then
    pass "$test_name"
  else
    fail "$test_name" "Expected $expected, got '$actual' for query $query"
  fi
}

# Extract entry ID from "Added: <uuid> (type)" output
extract_id() {
  echo "$1" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1
}

# Extract the NEW id from "Corrected: <old> -> <new>" output
extract_new_id() {
  echo "$1" | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | tail -1
}

# Read a field from a specific entry by ID (via export)
read_entry_field() {
  local entry_id="$1"
  local field="$2"
  "$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
for e in d['entries']:
    if e['id'] == sys.argv[1]:
        val = e.get(sys.argv[2])
        if isinstance(val, dict):
            print(val.get(sys.argv[3]) if len(sys.argv) > 3 else val)
        else:
            print(val)
        break
" "$entry_id" "$field" 2>&1
}

# Read a nested field from correction_meta (via export)
read_correction_field() {
  local entry_id="$1"
  local sub_field="$2"
  "$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
for e in d['entries']:
    if e['id'] == sys.argv[1]:
        meta = e.get('correction_meta') or {}
        print(meta.get(sys.argv[2], ''))
        break
" "$entry_id" "$sub_field" 2>&1
}

# Back up and restore memory (handles both backends)
backup_memory() {
  [[ -f "$MEMORY_DB" ]] && cp "$MEMORY_DB" "$BACKUP_DB"
  [[ -f "$MEMORY_JSON" ]] && cp "$MEMORY_JSON" "$BACKUP_JSON"
  [[ -f "$MEMORY_DIR/memory.json.bak" ]] && cp "$MEMORY_DIR/memory.json.bak" "$BACKUP_JSON_BAK"
}

restore_memory() {
  # Remove test artifacts
  rm -f "$MEMORY_DB" "$MEMORY_JSON" "$MEMORY_DIR/memory.json.bak"
  # Restore backups
  [[ -f "$BACKUP_DB" ]] && cp "$BACKUP_DB" "$MEMORY_DB" && rm "$BACKUP_DB"
  [[ -f "$BACKUP_JSON" ]] && cp "$BACKUP_JSON" "$MEMORY_JSON" && rm "$BACKUP_JSON"
  [[ -f "$BACKUP_JSON_BAK" ]] && cp "$BACKUP_JSON_BAK" "$MEMORY_DIR/memory.json.bak" && rm "$BACKUP_JSON_BAK"
}

clean_start() {
  rm -f "$MEMORY_DB" "$MEMORY_JSON" "$MEMORY_DIR/memory.json.bak"
}

# ============================================================
# TESTS
# ============================================================

echo "========================================="
echo " Agent Brain v4 — Test Suite"
echo "========================================="
echo ""

# Save existing memory if present
backup_memory
clean_start

# ----------------------------------------------------------
echo "[1/17] INIT"
# ----------------------------------------------------------
output=$("$MEMORY_SH" init 2>&1)
assert_contains "$output" "Initialized" "init creates memory file"
assert_export_field "['version']" "4" "init creates v4 schema"
assert_export_field "['session_counter']" "0" "init sets session_counter to 0"
assert_export_field ".get('last_decay')" "None" "init sets last_decay to null"
assert_export_field ".get('current_session')" "None" "init sets current_session to null"
meta_check=$("$SCRIPT_DIR/validate_meta.sh" 2>&1)
assert_contains "$meta_check" "Metadata valid" "metadata JSON validates"
if grep -q "../../supermemory/.env" "$MEMORY_SH"; then
  fail "memory.sh is standalone" "Found cross-skill env path ../../supermemory/.env"
else
  pass "memory.sh is standalone"
fi
if grep -q 'source "$SUPERMEMORY_ENV"' "$MEMORY_SH"; then
  fail "memory.sh env parsing is non-executing" "Found shell source of env file"
else
  pass "memory.sh env parsing is non-executing"
fi

# ----------------------------------------------------------
echo ""
echo "[2/17] ADD — basic entries"
# ----------------------------------------------------------
out1=$("$MEMORY_SH" add fact "User likes coffee" user "food,beverage" 2>&1)
ID1=$(extract_id "$out1")
assert_contains "$out1" "Added:" "add fact succeeds"
[[ -n "$ID1" ]] && pass "add returns UUID" || fail "add returns UUID" "No UUID found"

out2=$("$MEMORY_SH" add preference "Prefers dark mode" user "style.editor,ui" 2>&1)
ID2=$(extract_id "$out2")
assert_contains "$out2" "preference" "add preference succeeds"

out3=$("$MEMORY_SH" add procedure "Run linter before commit" user "workflow.git,code" 2>&1)
ID3=$(extract_id "$out3")

# With context
out4=$("$MEMORY_SH" add preference "Use tabs not spaces" user "style.code,formatting" "" "Python projects" 2>&1)
ID4=$(extract_id "$out4")
assert_contains "$out4" "Added:" "add with context succeeds"

# With source_url
out5=$("$MEMORY_SH" add ingested "TDD improves code quality" ingested "testing,methodology" "https://example.com/tdd" 2>&1)
ID5=$(extract_id "$out5")
assert_contains "$out5" "ingested" "add ingested with source_url succeeds"

# ----------------------------------------------------------
echo ""
echo "[3/17] ADD — field validation"
# ----------------------------------------------------------
# Check access_count starts at 1 (not 0)
ac=$(read_entry_field "$ID1" "access_count")
[[ "$ac" == "1" ]] && pass "new entries start with access_count=1" || fail "new entries start with access_count=1" "Got $ac"

# Check confidence assignment
conf_user=$(read_entry_field "$ID1" "confidence")
[[ "$conf_user" == "sure" ]] && pass "user-sourced entries get confidence=sure" || fail "user-sourced entries get confidence=sure" "Got $conf_user"

conf_ingested=$(read_entry_field "$ID5" "confidence")
[[ "$conf_ingested" == "likely" ]] && pass "ingested entries get confidence=likely" || fail "ingested entries get confidence=likely" "Got $conf_ingested"

# Check context field
ctx=$(read_entry_field "$ID4" "context")
[[ "$ctx" == "Python projects" ]] && pass "context field stored correctly" || fail "context field stored correctly" "Got $ctx"

# Check source_url field
url=$(read_entry_field "$ID5" "source_url")
[[ "$url" == "https://example.com/tdd" ]] && pass "source_url stored correctly" || fail "source_url stored correctly" "Got $url"

# ----------------------------------------------------------
echo ""
echo "[4/17] GET — weighted search + auto-touch"
# ----------------------------------------------------------
out_get=$("$MEMORY_SH" get "coffee" 2>&1)
assert_contains "$out_get" "User likes coffee" "get finds matching entry"
assert_contains "$out_get" "score:" "get shows relevance score"

# Check auto-touch incremented access_count
ac_after=$(read_entry_field "$ID1" "access_count")
[[ "$ac_after" == "2" ]] && pass "get auto-touches returned entries" || fail "get auto-touches returned entries" "access_count=$ac_after, expected 2"

# Search that should return nothing
out_empty=$("$MEMORY_SH" get "quantum physics" 2>&1)
assert_contains "$out_empty" "No matching" "get returns no results for unrelated query"

# Tag prefix matching
out_tag=$("$MEMORY_SH" get "style" 2>&1)
assert_contains "$out_tag" "dark mode" "get matches namespaced tag prefix (style matches style.editor)"

# Retrieval flags: policy + stores + explain
out_get_explain=$("$MEMORY_SH" get "coffee" --policy deep --stores semantic --explain 2>&1)
assert_contains "$out_get_explain" "explain:" "get --explain shows score components"
assert_contains "$out_get_explain" "/semantic)" "get prints memory class on results"
assert_contains "$out_get_explain" "semantic_mode=local" "get --explain reports semantic mode"

# Remote embeddings are opt-in and can be safely capped.
out_get_remote_default=$(AGENT_BRAIN_EMBEDDING_URL="http://127.0.0.1:9" "$MEMORY_SH" get "coffee" --explain 2>&1)
assert_contains "$out_get_remote_default" "semantic_mode=local" "remote embeddings stay off by default"
assert_contains "$out_get_remote_default" "semantic_reason=remote_disabled" "default remote reason is explicit"
out_get_remote_capped=$(AGENT_BRAIN_REMOTE_EMBEDDINGS=on AGENT_BRAIN_EMBEDDING_URL="http://127.0.0.1:9" AGENT_BRAIN_REMOTE_EMBEDDING_MAX_ENTRIES=0 "$MEMORY_SH" get "coffee" --explain 2>&1)
assert_contains "$out_get_remote_capped" "semantic_mode=local" "remote embeddings respect max entry cap"
assert_contains "$out_get_remote_capped" "semantic_reason=entry_limit" "capped remote reason is explicit"

out_get_store_filter=$("$MEMORY_SH" get "dark mode" --stores semantic 2>&1)
assert_contains "$out_get_store_filter" "No matching" "get --stores filters memory classes"

out_get_bad_policy=$("$MEMORY_SH" get "coffee" --policy turbo 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "get rejects invalid policy" || fail "get rejects invalid policy" "exit code was $ec"
assert_contains "$out_get_bad_policy" "Invalid arguments" "get invalid policy shows error"

out_get_bad_flag=$("$MEMORY_SH" get "coffee" --polciy deep 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "get rejects unknown flags" || fail "get rejects unknown flags" "exit code was $ec"
assert_contains "$out_get_bad_flag" "Unknown flag" "get unknown flag shows error"

# Hyphen-prefixed query terms are allowed with "--" separator
out_dash_entry=$("$MEMORY_SH" add fact "Tune JVM -Xms and -Xmx flags" user "jvm,flags" 2>&1)
assert_contains "$out_dash_entry" "Added:" "add entry with hyphen-prefixed terms succeeds"
out_get_dash=$("$MEMORY_SH" get -- "-xms flags" 2>&1)
assert_contains "$out_get_dash" "Tune JVM -Xms and -Xmx flags" "get supports hyphen-prefixed query terms with --"

out_get_bad_response=$("$MEMORY_SH" get "coffee" --response "great" 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "get rejects --response flag" || fail "get rejects --response flag" "exit code was $ec"
assert_contains "$out_get_bad_response" "does not accept" "get --response shows explicit error"

out_get_bad_feedback=$("$MEMORY_SH" get "coffee" --user-feedback "worked" 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "get rejects --user-feedback flag" || fail "get rejects --user-feedback flag" "exit code was $ec"
assert_contains "$out_get_bad_feedback" "does not accept" "get --user-feedback shows explicit error"

# ----------------------------------------------------------
echo ""
echo "[5/17] LIST"
# ----------------------------------------------------------
out_list=$("$MEMORY_SH" list 2>&1)
assert_contains "$out_list" "active entries" "list shows all active entries"
assert_contains "$out_list" "coffee" "list includes fact entry"

out_list_type=$("$MEMORY_SH" list preference 2>&1)
assert_contains "$out_list_type" "dark mode" "list filters by type"
assert_not_contains "$out_list_type" "coffee" "list type filter excludes other types"

# ----------------------------------------------------------
echo ""
echo "[6/17] UPDATE"
# ----------------------------------------------------------
out_upd=$("$MEMORY_SH" update "$ID2" confidence likely 2>&1)
assert_contains "$out_upd" "Updated" "update changes confidence"

# Verify change persisted
new_conf=$(read_entry_field "$ID2" "confidence")
[[ "$new_conf" == "likely" ]] && pass "update persists confidence change" || fail "update persists confidence change" "Got $new_conf"

# Update tags
"$MEMORY_SH" update "$ID2" tags "style.editor,ui,theme" >/dev/null 2>&1
tag_count=$("$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
for e in d['entries']:
    if e['id'] == sys.argv[1]:
        print(len(e['tags']))
        break
" "$ID2")
[[ "$tag_count" == "3" ]] && pass "update replaces tags correctly" || fail "update replaces tags correctly" "Got $tag_count tags"

# Disallowed field
out_bad=$("$MEMORY_SH" update "$ID1" id "hacked" 2>&1)
ec=$?
assert_contains "$out_bad" "ERROR" "update rejects disallowed field"

# Non-existent ID
out_miss=$("$MEMORY_SH" update "fake-id-000" confidence sure 2>&1)
ec=$?
assert_contains "$out_miss" "not found" "update reports missing entry"

# ----------------------------------------------------------
echo ""
echo "[7/17] CONFLICTS — improved detection"
# ----------------------------------------------------------
# Should detect: same topic, different claim
out_conf=$("$MEMORY_SH" conflicts "User likes tea instead of coffee" 2>&1)
assert_contains "$out_conf" "POTENTIAL_CONFLICTS" "conflicts detects related entry"
assert_contains "$out_conf" "overlap:" "conflicts reports overlap percentage"

# Should NOT false positive on stopwords only
out_no_conf=$("$MEMORY_SH" conflicts "I have a big dog" 2>&1)
assert_contains "$out_no_conf" "NO_CONFLICTS" "conflicts filters stopwords (no false positive)"

# Should NOT flag unrelated content sharing a common word
out_no_conf2=$("$MEMORY_SH" conflicts "The coffee table is broken" 2>&1)
# "coffee" is 1 meaningful word overlap, needs 2+
assert_contains "$out_no_conf2" "NO_CONFLICTS" "conflicts requires 2+ meaningful word overlap"

# ----------------------------------------------------------
echo ""
echo "[8/17] SIMILAR — TF-IDF"
# ----------------------------------------------------------
out_sim=$("$MEMORY_SH" similar "User enjoys drinking coffee every morning" 2>&1)
assert_contains "$out_sim" "SIMILAR_ENTRIES" "similar finds related entries"
assert_contains "$out_sim" "similarity:" "similar reports similarity score"
assert_contains "$out_sim" "coffee" "similar returns the correct entry"

# No similar entries
out_no_sim=$("$MEMORY_SH" similar "quantum entanglement theory" 2>&1)
assert_contains "$out_no_sim" "NO_SIMILAR" "similar returns nothing for unrelated query"

# Custom threshold
out_low=$("$MEMORY_SH" similar "coding practices" 0.05 2>&1)
# Should find something at very low threshold
# (may or may not, depends on corpus — just check it doesn't crash)
ec=$?
assert_exit_code "$ec" 0 "similar with custom threshold doesn't crash"

# ----------------------------------------------------------
echo ""
echo "[9/17] SUPERSEDE"
# ----------------------------------------------------------
out_new=$("$MEMORY_SH" add fact "User likes green tea" user "food,beverage" 2>&1)
ID_NEW=$(extract_id "$out_new")
out_sup=$("$MEMORY_SH" supersede "$ID1" "$ID_NEW" 2>&1)
assert_contains "$out_sup" "Superseded" "supersede marks old entry"

# Superseded entry should not appear in list
out_list2=$("$MEMORY_SH" list 2>&1)
assert_not_contains "$out_list2" "User likes coffee" "superseded entry hidden from list"
assert_contains "$out_list2" "green tea" "new entry visible in list"

# Superseded entry should not appear in get
out_get2=$("$MEMORY_SH" get "coffee" 2>&1)
assert_not_contains "$out_get2" "User likes coffee" "superseded entry hidden from get"

# ----------------------------------------------------------
echo ""
echo "[10/17] CORRECT — correction tracking + anti-pattern"
# ----------------------------------------------------------
out_corr=$("$MEMORY_SH" correct "$ID3" "Run linter AND tests before commit" "Original missed the test step" "workflow.git,code" 2>&1)
CORR_ID=$(extract_new_id "$out_corr")
assert_contains "$out_corr" "Corrected:" "correct creates correction entry"
assert_contains "$out_corr" "Wrong:" "correct shows wrong claim"
assert_contains "$out_corr" "Right:" "correct shows right claim"
assert_contains "$out_corr" "Reason:" "correct shows reason"

# Verify correction_meta
meta=$(read_correction_field "$CORR_ID" "wrong_claim")
assert_contains "$meta" "Run linter" "correction_meta stores wrong claim"

# Verify old entry is superseded
sup_by=$(read_entry_field "$ID3" "superseded_by")
[[ "$sup_by" == "$CORR_ID" ]] && pass "correct supersedes wrong entry" || fail "correct supersedes wrong entry" "superseded_by=$sup_by, expected $CORR_ID"

# Anti-pattern detection: need 3 corrections with same tag
out_wa=$("$MEMORY_SH" add fact "Wrong fact A" user "testing" 2>&1)
WA_ID=$(extract_id "$out_wa")
"$MEMORY_SH" correct "$WA_ID" "Right fact A" "mistake" "workflow.git" >/dev/null 2>&1

out_wb=$("$MEMORY_SH" add fact "Wrong fact B" user "testing" 2>&1)
WB_ID=$(extract_id "$out_wb")
out_ap=$("$MEMORY_SH" correct "$WB_ID" "Right fact B" "mistake" "workflow.git" 2>&1)
assert_contains "$out_ap" "ANTI_PATTERN_DETECTED" "anti-pattern detected after 3 corrections with same tag"

# ----------------------------------------------------------
echo ""
echo "[11/17] SUCCESS — tracking + auto-upgrade"
# ----------------------------------------------------------
# Downgrade an entry first so we can test auto-upgrade
"$MEMORY_SH" update "$ID4" confidence uncertain >/dev/null 2>&1

out_s1=$("$MEMORY_SH" success "$ID4" 2>&1)
assert_contains "$out_s1" "Success recorded" "success records first win"
assert_contains "$out_s1" "total: 1" "success shows count"

"$MEMORY_SH" success "$ID4" >/dev/null 2>&1
out_s3=$("$MEMORY_SH" success "$ID4" 2>&1)
assert_contains "$out_s3" "Auto-upgraded" "success auto-upgrades at 3"
assert_contains "$out_s3" "sure" "success upgrades to sure"

# Verify persistence
final_conf=$(read_entry_field "$ID4" "confidence")
[[ "$final_conf" == "sure" ]] && pass "auto-upgrade persists" || fail "auto-upgrade persists" "Got $final_conf"

# Success on non-existent ID
out_sfail=$("$MEMORY_SH" success "fake-id" 2>&1)
assert_contains "$out_sfail" "not found" "success reports missing entry"

# ----------------------------------------------------------
echo ""
echo "[12/17] SESSION"
# ----------------------------------------------------------
out_sess=$("$MEMORY_SH" session "Frontend refactor" 2>&1)
assert_contains "$out_sess" "Session 1" "session starts with counter"
assert_contains "$out_sess" "Frontend refactor" "session includes context"

# Entry added after session should have session_id
out_sessentry=$("$MEMORY_SH" add fact "React is great for UI" user "code.react,frontend" 2>&1)
SESS_ENTRY_ID=$(extract_id "$out_sessentry")
sid=$(read_entry_field "$SESS_ENTRY_ID" "session_id")
[[ "$sid" == "1" ]] && pass "entries get session_id from active session" || fail "entries get session_id from active session" "Got $sid"

# Second session increments counter
out_sess2=$("$MEMORY_SH" session "Backend work" 2>&1)
assert_contains "$out_sess2" "Session 2" "session counter increments"

# ----------------------------------------------------------
echo ""
echo "[12.5/17] LOOP — orchestrated retrieve/extract"
# ----------------------------------------------------------
count_before=$("$MEMORY_SH" export 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['entries']))")
out_loop=$("$MEMORY_SH" loop "My name is Marcus. We use Rust. I prefer concise replies." --policy deep --stores semantic,preference --explain 2>&1)
assert_contains "$out_loop" "LOOP_RETRIEVE" "loop runs retrieval stage"
assert_contains "$out_loop" "LOOP_EXTRACT" "loop runs extraction stage"
assert_contains "$out_loop" "added:" "loop reports added count"

count_after=$("$MEMORY_SH" export 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['entries']))")
if [[ "$count_after" -gt "$count_before" ]]; then
  pass "loop stores extracted memories"
else
  fail "loop stores extracted memories" "entries before=$count_before after=$count_after"
fi

out_rust=$("$MEMORY_SH" get "rust" --stores semantic 2>&1)
assert_contains "$out_rust" "Team uses Rust" "loop-extracted fact is retrievable"

out_loop_sensitive=$("$MEMORY_SH" loop "api_key=SECRET_12345 password=abc123" 2>&1)
assert_contains "$out_loop_sensitive" "skipped_sensitive" "loop blocks sensitive content extraction"

# Loop reinforcement behavior:
# 1) --response alone must NOT increment success_count
out_loop_target=$("$MEMORY_SH" add fact "Loop feedback target" user "feedback" 2>&1)
LOOP_TARGET_ID=$(extract_id "$out_loop_target")
"$MEMORY_SH" loop "loop feedback target" --response "Great, done" >/dev/null 2>&1
sc_no_feedback=$(read_entry_field "$LOOP_TARGET_ID" "success_count")
[[ "$sc_no_feedback" == "0" ]] && pass "loop --response does not auto-reinforce" || fail "loop --response does not auto-reinforce" "success_count=$sc_no_feedback"

# 2) explicit --user-feedback should reinforce
"$MEMORY_SH" loop "loop feedback target" --user-feedback "that worked great" >/dev/null 2>&1
sc_with_feedback=$(read_entry_field "$LOOP_TARGET_ID" "success_count")
[[ "$sc_with_feedback" == "1" ]] && pass "loop --user-feedback reinforces success" || fail "loop --user-feedback reinforces success" "success_count=$sc_with_feedback"

# ----------------------------------------------------------
echo ""
echo "[13/17] TAGS — hierarchy"
# ----------------------------------------------------------
out_tags=$("$MEMORY_SH" tags 2>&1)
assert_contains "$out_tags" "code" "tags shows root tag"
# Should show child tags
assert_contains "$out_tags" ".react" "tags shows namespaced children"

# ----------------------------------------------------------
echo ""
echo "[14/17] REFLECT + CONSOLIDATE + STATS + DECAY"
# ----------------------------------------------------------
out_refl=$("$MEMORY_SH" reflect 2>&1)
assert_contains "$out_refl" "MEMORY REFLECTION" "reflect runs without error"
assert_contains "$out_refl" "active" "reflect shows active count"
assert_contains "$out_refl" "CORRECTIONS" "reflect shows corrections"
assert_contains "$out_refl" "TOP SUCCESSES" "reflect shows successes"
assert_contains "$out_refl" "TOP TAGS" "reflect shows tag distribution"

out_cons=$("$MEMORY_SH" consolidate 2>&1)
# With enough entries sharing tags, should find clusters
ec=$?
assert_exit_code "$ec" 0 "consolidate runs without error"

out_stats=$("$MEMORY_SH" stats 2>&1)
assert_contains "$out_stats" "Version: 4" "stats shows v4"
assert_contains "$out_stats" "Sessions: 2" "stats shows session count"
assert_contains "$out_stats" "correction" "stats shows correction type"
assert_contains "$out_stats" "Last decay:" "stats shows last decay time"

out_decay=$("$MEMORY_SH" decay 2>&1)
assert_contains "$out_decay" "Decayed" "decay runs without error"

# ----------------------------------------------------------
echo ""
echo "[15/17] EDGE CASES + ERROR HANDLING"
# ----------------------------------------------------------

# Missing required arguments
out_notype=$("$MEMORY_SH" add 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "add without args fails" || fail "add without args fails" "exit code was $ec"

out_noquery=$("$MEMORY_SH" get 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "get without query fails" || fail "get without query fails" "exit code was $ec"

out_noid=$("$MEMORY_SH" touch 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "touch without id fails" || fail "touch without id fails" "exit code was $ec"

out_nosup=$("$MEMORY_SH" supersede 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "supersede without args fails" || fail "supersede without args fails" "exit code was $ec"

out_nocorr=$("$MEMORY_SH" correct 2>&1)
ec=$?
[[ $ec -ne 0 ]] && pass "correct without args fails" || fail "correct without args fails" "exit code was $ec"

# Special characters in content
out_special=$("$MEMORY_SH" add fact "User's favorite: \"quotes\" & <brackets>" user "special" 2>&1)
assert_contains "$out_special" "Added:" "add handles special characters"
SPEC_ID=$(extract_id "$out_special")

# Verify special chars round-trip
spec_content=$(read_entry_field "$SPEC_ID" "content")
assert_contains "$spec_content" "quotes" "special characters survive round-trip"

# Unicode content
out_unicode=$("$MEMORY_SH" add fact "Likes sushi and ramen" user "food" 2>&1)
assert_contains "$out_unicode" "Added:" "add handles unicode content"

# Very long content
long_str=$(python3 -c "print('x' * 500)")
out_long=$("$MEMORY_SH" add fact "$long_str" user "test" 2>&1)
assert_contains "$out_long" "Added:" "add handles long content (500 chars)"

# Empty tags
out_notags=$("$MEMORY_SH" add fact "No tags entry" user "" 2>&1)
assert_contains "$out_notags" "Added:" "add works with empty tags"

# Unknown command
out_unk=$("$MEMORY_SH" foobar 2>&1)
assert_contains "$out_unk" "Usage:" "unknown command shows help"

# Export produces valid JSON
out_export=$("$MEMORY_SH" export 2>&1)
echo "$out_export" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null
ec=$?
assert_exit_code "$ec" 0 "export produces valid JSON"

# ----------------------------------------------------------
echo ""
echo "[16/17] JSON BACKEND + V2 → V4 MIGRATION"
# ----------------------------------------------------------
# Clean slate for migration test
clean_start

# Create a v2 JSON file manually
mkdir -p "$MEMORY_DIR"
cat > "$MEMORY_JSON" << 'MIGEOF'
{
  "version": 2,
  "entries": [
    {
      "id": "migrate-test-001",
      "type": "fact",
      "content": "Old v2 entry",
      "source": "user",
      "source_url": null,
      "tags": ["legacy"],
      "created": "2025-06-01T00:00:00Z",
      "last_accessed": "2025-06-01T00:00:00Z",
      "access_count": 5,
      "confidence": "sure",
      "superseded_by": null
    }
  ]
}
MIGEOF

# Use JSON backend for migration test
export AGENT_BRAIN_BACKEND=json
out_mig=$("$MEMORY_SH" stats 2>&1)
assert_contains "$out_mig" "Migrated memory to v4" "v2 file auto-migrates to v4"
assert_contains "$out_mig" "Version: 4" "migrated file reports v4"

# Check new fields added to old entry
mig_fields=$("$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
e = d['entries'][0]
missing = []
for field in ['context', 'session_id', 'success_count', 'correction_meta', 'memory_class']:
    if field not in e:
        missing.append(field)
print('OK' if not missing else ','.join(missing))
")
[[ "$mig_fields" == "OK" ]] && pass "migration adds all new fields to existing entries" || fail "migration adds all new fields to existing entries" "Missing: $mig_fields"

# Check top-level fields added
mig_top=$("$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
missing = []
for field in ['last_decay', 'session_counter', 'current_session']:
    if field not in d:
        missing.append(field)
print('OK' if not missing else ','.join(missing))
")
[[ "$mig_top" == "OK" ]] && pass "migration adds all top-level fields" || fail "migration adds all top-level fields" "Missing: $mig_top"

# Migration preserves existing data
mig_ac=$("$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d['entries'][0]['access_count'])
")
[[ "$mig_ac" == "5" ]] && pass "migration preserves existing access_count" || fail "migration preserves existing access_count" "Got $mig_ac"

# Migration is idempotent (running again shouldn't change anything)
"$MEMORY_SH" stats >/dev/null 2>&1
mig_v=$("$MEMORY_SH" export 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d['version'])
")
[[ "$mig_v" == "4" ]] && pass "migration is idempotent" || fail "migration is idempotent" "Version became $mig_v"

# Unset to restore default backend
unset AGENT_BRAIN_BACKEND


# ============================================================
echo "[17/17] ACTIVITY LOG"
# ============================================================

clean_start

"$MEMORY_SH" init >/dev/null 2>&1

# Log starts empty
log_empty=$("$MEMORY_SH" log 2>&1)
assert_contains "$log_empty" "No activity" "log is empty on fresh init"

# Add generates log entry
add_out=$("$MEMORY_SH" add fact "Log test entry" user "testing" 2>&1)
log_after_add=$("$MEMORY_SH" log 2>&1)
assert_contains "$log_after_add" "add" "log records add operation"
assert_contains "$log_after_add" "Log test entry" "log shows entry content"

# Get generates log entry
"$MEMORY_SH" get "log test" >/dev/null 2>&1
log_after_get=$("$MEMORY_SH" log 2>&1)
assert_contains "$log_after_get" "get" "log records get operation"
assert_contains "$log_after_get" "query=" "log shows query details"

# Log count filter works
log_one=$("$MEMORY_SH" log 1 2>&1)
line_count=$(echo "$log_one" | wc -l | tr -d ' ')
[[ "$line_count" -le 2 ]] && pass "log count filter limits output" || fail "log count filter limits output" "Got $line_count lines"

# Log action filter works
log_adds=$("$MEMORY_SH" log 50 add 2>&1)
assert_contains "$log_adds" "add" "log action filter returns matching actions"
assert_not_contains "$log_adds" "get" "log action filter excludes other actions"

# Session generates log entry
"$MEMORY_SH" session "Log test session" >/dev/null 2>&1
log_after_session=$("$MEMORY_SH" log 2>&1)
assert_contains "$log_after_session" "session" "log records session operation"


# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "========================================="
echo " RESULTS"
echo "========================================="
echo ""
echo "  Passed: $PASS_COUNT"
echo "  Failed: $FAIL_COUNT"
echo "  Total:  $((PASS_COUNT + FAIL_COUNT))"

if [[ $FAIL_COUNT -gt 0 ]]; then
  echo ""
  echo "  FAILURES:"
  echo -e "$FAIL_DETAILS"
fi

echo ""

# Restore original memory
restore_memory

# Exit with failure code if any tests failed
[[ $FAIL_COUNT -eq 0 ]] && exit 0 || exit 1
