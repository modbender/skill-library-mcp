#!/usr/bin/env bash
# Test runner for osori scripts
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PASSED=0
FAILED=0
ERRORS=()

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo -e "  ${GREEN}✓${NC} $desc"; PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}✗${NC} $desc"; echo "    expected: $expected"; echo "    actual:   $actual"
    FAILED=$((FAILED + 1)); ERRORS+=("$desc")
  fi
}

assert_contains() {
  local desc="$1" haystack="$2" needle="$3"
  if [[ "$haystack" == *"$needle"* ]]; then
    echo -e "  ${GREEN}✓${NC} $desc"; PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}✗${NC} $desc"; echo "    expected to contain: $needle"; echo "    actual: $haystack"
    FAILED=$((FAILED + 1)); ERRORS+=("$desc")
  fi
}

assert_not_contains() {
  local desc="$1" haystack="$2" needle="$3"
  if [[ "$haystack" != *"$needle"* ]]; then
    echo -e "  ${GREEN}✓${NC} $desc"; PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}✗${NC} $desc"; echo "    expected NOT to contain: $needle"
    FAILED=$((FAILED + 1)); ERRORS+=("$desc")
  fi
}

assert_file_exists() {
  local desc="$1" file="$2"
  if [[ -f "$file" ]]; then
    echo -e "  ${GREEN}✓${NC} $desc"; PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}✗${NC} $desc"; echo "    file not found: $file"
    FAILED=$((FAILED + 1)); ERRORS+=("$desc")
  fi
}

project_count() {
  local file="$1"
  python3 - "$file" << 'PYEOF'
import json, sys
with open(sys.argv[1], encoding='utf-8') as f:
    data = json.load(f)
if isinstance(data, list):
    print(len(data))
elif isinstance(data, dict):
    print(len(data.get('projects', [])))
else:
    print(0)
PYEOF
}

setup_test() {
  TEST_TMP="$(mktemp -d)"
  mkdir -p "$TEST_TMP/fake-project"
  git -C "$TEST_TMP/fake-project" init -q 2>/dev/null || true
  git -C "$TEST_TMP/fake-project" config user.email "test@example.com"
  git -C "$TEST_TMP/fake-project" config user.name "osori-test"
  echo "hello" > "$TEST_TMP/fake-project/README.md"
  git -C "$TEST_TMP/fake-project" add README.md >/dev/null 2>&1
  git -C "$TEST_TMP/fake-project" commit -m "init" >/dev/null 2>&1 || true
  export OSORI_REGISTRY="$TEST_TMP/osori.json"
}

teardown_test() {
  rm -rf "$TEST_TMP"
  unset OSORI_REGISTRY
  unset OSORI_ROOT_KEY
}

# ─── TESTS ───

echo "=== test_add_project_schema_v2 ==="
setup_test
output=$(bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "myproject" 2>&1)
assert_contains "add prints Added" "$output" "Added"
assert_file_exists "registry created" "$TEST_TMP/osori.json"
content=$(cat "$TEST_TMP/osori.json")
assert_contains "registry has schema field" "$content" '"schema": "osori.registry"'
assert_contains "registry has version field" "$content" '"version": 2'
assert_contains "registry has projects container" "$content" '"projects": ['
assert_contains "registry has root field" "$content" '"root": "default"'
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "project count is one" "1" "$count"
teardown_test

echo ""
echo "=== test_add_duplicate ==="
setup_test
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "duptest" >/dev/null 2>&1
output=$(bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "duptest" 2>&1)
assert_contains "duplicate detected" "$output" "Already registered"
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "only one entry" "1" "$count"
teardown_test

echo ""
echo "=== test_scan_projects ==="
setup_test
for name in proj-a proj-b proj-c; do
  mkdir -p "$TEST_TMP/repos/$name"
  git -C "$TEST_TMP/repos/$name" init -q 2>/dev/null
  git -C "$TEST_TMP/repos/$name" config user.email "test@example.com"
  git -C "$TEST_TMP/repos/$name" config user.name "osori-test"
  echo "$name" > "$TEST_TMP/repos/$name/README.md"
  git -C "$TEST_TMP/repos/$name" add README.md >/dev/null 2>&1
  git -C "$TEST_TMP/repos/$name" commit -m "init" >/dev/null 2>&1 || true
done
output=$(bash "$PROJECT_ROOT/scripts/scan-projects.sh" "$TEST_TMP/repos" --depth 2 2>&1)
assert_contains "scan reports additions" "$output" "Added 3"
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "three projects registered" "3" "$count"
teardown_test

echo ""
echo "=== test_legacy_registry_auto_migration ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {
    "name": "legacy-proj",
    "path": "/tmp/legacy",
    "repo": "",
    "lang": "unknown",
    "tags": [],
    "description": "",
    "addedAt": "2026-02-10"
  }
]
JSONEOF
output=$(bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "new-proj" 2>&1)
assert_contains "legacy migration notice" "$output" "Migrated registry on load"
content=$(cat "$TEST_TMP/osori.json")
assert_contains "migrated schema present" "$content" '"schema": "osori.registry"'
assert_contains "legacy preserved" "$content" '"legacy-proj"'
assert_contains "new project preserved" "$content" '"new-proj"'
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "two projects after migration+add" "2" "$count"
backup_count=$(find "$TEST_TMP" -name 'osori.json.bak-*' | wc -l | tr -d ' ')
assert_eq "backup created on migration" "1" "$backup_count"
teardown_test

echo ""
echo "=== test_corrupted_registry_recovery ==="
setup_test
printf '{ this is broken json ' > "$TEST_TMP/osori.json"
output=$(bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "recover-proj" 2>&1)
assert_contains "corruption recovery notice" "$output" "registry corrupted"
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "one project after recovery" "1" "$count"
broken_count=$(find "$TEST_TMP" -name 'osori.json.broken-*' | wc -l | tr -d ' ')
assert_eq "broken backup created" "1" "$broken_count"
teardown_test

echo ""
echo "=== test_doctor_detects_basic_issues ==="
setup_test
# create missing path project + invalid repo format
cat > "$TEST_TMP/osori.json" << JSONEOF
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [{"key": "default", "label": "Default", "paths": []}],
  "projects": [
    {
      "name": "bad-path",
      "path": "$TEST_TMP/no-such-dir",
      "repo": "invalid repo format",
      "lang": "unknown",
      "tags": [],
      "description": "",
      "addedAt": "2026-02-16",
      "root": "default"
    }
  ]
}
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" 2>&1 || true)
assert_contains "doctor detects missing path" "$out" "project.path_missing"
assert_contains "doctor detects invalid repo" "$out" "project.repo_invalid_format"
teardown_test

echo ""
echo "=== test_doctor_detects_duplicates ==="
setup_test
cat > "$TEST_TMP/osori.json" << JSONEOF
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [{"key": "default", "label": "Default", "paths": []}],
  "projects": [
    {"name": "dup", "path": "$TEST_TMP/fake-project", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"},
    {"name": "dup", "path": "$TEST_TMP/fake-project", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"}
  ]
}
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" 2>&1 || true)
assert_contains "doctor duplicate name" "$out" "project.duplicate_name"
assert_contains "doctor duplicate path" "$out" "project.duplicate_path"
teardown_test

echo ""
echo "=== test_doctor_detects_root_reference_missing ==="
setup_test
cat > "$TEST_TMP/osori.json" << JSONEOF
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [{"key": "default", "label": "Default", "paths": []}],
  "projects": [
    {"name": "x", "path": "$TEST_TMP/fake-project", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "work"}
  ]
}
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" 2>&1 || true)
assert_contains "doctor root mismatch" "$out" "project.root_reference_missing"
teardown_test

echo ""
echo "=== test_doctor_json_output ==="
setup_test
out_json=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --json 2>&1)
assert_contains "doctor json has status" "$out_json" '"status"'
assert_contains "doctor json has counts" "$out_json" '"counts"'
assert_contains "doctor json has findings" "$out_json" '"findings"'
teardown_test

echo ""
echo "=== test_doctor_fix_legacy_migration ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {
    "name": "legacy-proj",
    "path": "/tmp/legacy",
    "repo": "",
    "lang": "unknown",
    "tags": [],
    "description": "",
    "addedAt": "2026-02-10"
  }
]
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --fix 2>&1)
assert_contains "doctor fix migration info" "$out" "fix.migration_applied"
content=$(cat "$TEST_TMP/osori.json")
assert_contains "doctor fix migrated schema" "$content" '"schema": "osori.registry"'
teardown_test

echo ""
echo "=== test_doctor_fix_dedupe ==="
setup_test
cat > "$TEST_TMP/osori.json" << JSONEOF
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [{"key": "default", "label": "Default", "paths": []}],
  "projects": [
    {"name": "dup", "path": "$TEST_TMP/fake-project", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"},
    {"name": "dup", "path": "$TEST_TMP/fake-project", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"}
  ]
}
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --fix 2>&1)
assert_contains "doctor fix dedupe message" "$out" "fix.dedupe_applied"
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "doctor fix removed duplicate" "1" "$count"
teardown_test

echo ""
echo "=== test_doctor_fix_corrupted_registry ==="
setup_test
printf '{ broken json' > "$TEST_TMP/osori.json"
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --fix 2>&1)
assert_contains "doctor corrupted detected" "$out" "registry.corrupted"
count=$(project_count "$TEST_TMP/osori.json")
assert_eq "doctor fix reinitialized registry" "0" "$count"
broken_count=$(find "$TEST_TMP" -name 'osori.json.broken-*' | wc -l | tr -d ' ')
assert_eq "doctor fix saved broken backup" "1" "$broken_count"
teardown_test

echo ""
echo "=== test_telegram_doctor_command ==="
setup_test
doctor_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" doctor --json 2>&1)
assert_contains "telegram doctor returns json" "$doctor_out" '"status"'
teardown_test

echo ""
echo "=== test_doctor_preview_first_default ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {"name": "prev-proj", "path": "/tmp/prev", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16"}
]
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" 2>&1)
assert_contains "doctor default shows preview" "$out" "Preview only"
assert_contains "doctor default shows plan" "$out" "Fix Plan"
# Verify no changes were applied (file should still be legacy array)
first_char=$(head -c1 "$TEST_TMP/osori.json")
assert_eq "doctor default did not modify file" "[" "$first_char"
teardown_test

echo ""
echo "=== test_doctor_dry_run_never_applies ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {"name": "dry-proj", "path": "/tmp/dry", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16"}
]
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --dry-run 2>&1)
assert_contains "doctor dry-run message" "$out" "Dry-run mode"
assert_contains "doctor dry-run shows plan" "$out" "Fix Plan"
first_char=$(head -c1 "$TEST_TMP/osori.json")
assert_eq "doctor dry-run did not modify file" "[" "$first_char"
teardown_test

echo ""
echo "=== test_doctor_dry_run_overrides_fix ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {"name": "override-proj", "path": "/tmp/override", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16"}
]
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --fix --dry-run 2>&1)
assert_contains "doctor dry-run overrides fix" "$out" "Dry-run mode"
first_char=$(head -c1 "$TEST_TMP/osori.json")
assert_eq "doctor dry-run+fix did not modify file" "[" "$first_char"
teardown_test

echo ""
echo "=== test_doctor_fix_applies_changes ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {"name": "fix-proj", "path": "/tmp/fix-proj", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16"}
]
JSONEOF
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --fix 2>&1)
assert_contains "doctor fix applied" "$out" "Fix applied"
content=$(cat "$TEST_TMP/osori.json")
assert_contains "doctor fix migrated" "$content" '"schema": "osori.registry"'
teardown_test

echo ""
echo "=== test_doctor_json_has_plan_and_risk ==="
setup_test
cat > "$TEST_TMP/osori.json" << 'JSONEOF'
[
  {"name": "json-proj", "path": "/tmp/json-proj", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16"}
]
JSONEOF
out_json=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --json 2>&1)
assert_contains "doctor json has plan" "$out_json" '"plan"'
assert_contains "doctor json has riskSummary" "$out_json" '"riskSummary"'
assert_contains "doctor json has dryRun" "$out_json" '"dryRun"'
teardown_test

echo ""
echo "=== test_doctor_risk_levels_in_plan ==="
setup_test
printf '{ broken json' > "$TEST_TMP/osori.json"
out_json=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --json 2>&1)
# Corrupted registry should produce high risk plan
assert_contains "doctor corrupted has high risk" "$out_json" '"high"'
assert_contains "doctor plan has reinitialize" "$out_json" '"reinitialize"'
teardown_test

echo ""
echo "=== test_doctor_high_risk_blocked_without_yes ==="
setup_test
printf '{ broken json' > "$TEST_TMP/osori.json"
out=$(bash "$PROJECT_ROOT/scripts/doctor.sh" --fix 2>&1)
assert_contains "doctor high risk blocked" "$out" "blocked"
teardown_test

echo ""
echo "=== test_fingerprints_view ==="
setup_test
git -C "$TEST_TMP/fake-project" remote add origin "https://github.com/example/osori-test.git"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "finger-proj" >/dev/null 2>&1
output=$(bash "$PROJECT_ROOT/scripts/project-fingerprints.sh" "finger-proj" 2>&1)
assert_contains "fingerprints includes project" "$output" "finger-proj"
assert_contains "fingerprints includes remote" "$output" "https://github.com/example/osori-test.git"
assert_contains "fingerprints includes last commit" "$output" "last commit:"
assert_contains "fingerprints includes PR count field" "$output" "open PRs:"
assert_contains "fingerprints includes issue count field" "$output" "open issues:"
teardown_test

echo ""
echo "=== test_github_cache_ttl ==="
setup_test

# fake gh command to count invocations
mkdir -p "$TEST_TMP/fakebin"
COUNT_FILE="$TEST_TMP/gh-call-count.txt"
echo 0 > "$COUNT_FILE"
cat > "$TEST_TMP/fakebin/gh" << 'SHEOF'
#!/usr/bin/env bash
set -euo pipefail
COUNT_FILE="${OSORI_FAKE_GH_COUNT_FILE:?}"
count=$(cat "$COUNT_FILE" 2>/dev/null || echo 0)
echo $((count+1)) > "$COUNT_FILE"
if [[ "${1:-}" == "pr" && "${2:-}" == "list" ]]; then
  echo '[{"number":1},{"number":2}]'
elif [[ "${1:-}" == "issue" && "${2:-}" == "list" ]]; then
  echo '[{"number":10}]'
else
  echo '[]'
fi
SHEOF
chmod +x "$TEST_TMP/fakebin/gh"

# prepare project with repo slug
mkdir -p "$TEST_TMP/cache-proj"
git -C "$TEST_TMP/cache-proj" init -q 2>/dev/null
git -C "$TEST_TMP/cache-proj" config user.email "test@example.com"
git -C "$TEST_TMP/cache-proj" config user.name "osori-test"
echo "cache" > "$TEST_TMP/cache-proj/README.md"
git -C "$TEST_TMP/cache-proj" add README.md >/dev/null 2>&1
git -C "$TEST_TMP/cache-proj" commit -m "init" >/dev/null 2>&1 || true
git -C "$TEST_TMP/cache-proj" remote add origin "https://github.com/example/cache-proj.git"

bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/cache-proj" --name "cache-proj" >/dev/null 2>&1

# first run: miss => 2 calls (pr + issue)
PATH="$TEST_TMP/fakebin:$PATH" OSORI_FAKE_GH_COUNT_FILE="$COUNT_FILE" OSORI_CACHE_FILE="$TEST_TMP/osori-cache.json" OSORI_CACHE_TTL=600 \
  bash "$PROJECT_ROOT/scripts/project-fingerprints.sh" cache-proj >/dev/null 2>&1
count1=$(cat "$COUNT_FILE")
assert_eq "cache miss triggers two gh calls" "2" "$count1"

# second run with same TTL: hit => no additional calls
PATH="$TEST_TMP/fakebin:$PATH" OSORI_FAKE_GH_COUNT_FILE="$COUNT_FILE" OSORI_CACHE_FILE="$TEST_TMP/osori-cache.json" OSORI_CACHE_TTL=600 \
  bash "$PROJECT_ROOT/scripts/project-fingerprints.sh" cache-proj >/dev/null 2>&1
count2=$(cat "$COUNT_FILE")
assert_eq "cache hit avoids extra gh calls" "2" "$count2"

# third run with TTL 0: miss => +2 calls
PATH="$TEST_TMP/fakebin:$PATH" OSORI_FAKE_GH_COUNT_FILE="$COUNT_FILE" OSORI_CACHE_FILE="$TEST_TMP/osori-cache.json" OSORI_CACHE_TTL=0 \
  bash "$PROJECT_ROOT/scripts/project-fingerprints.sh" cache-proj >/dev/null 2>&1
count3=$(cat "$COUNT_FILE")
assert_eq "ttl 0 forces refresh calls" "4" "$count3"
teardown_test

echo ""
echo "=== test_root_key_override ==="
setup_test
export OSORI_ROOT_KEY="work"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "rooted" >/dev/null 2>&1
content=$(cat "$TEST_TMP/osori.json")
assert_contains "project root is set from env" "$content" '"root": "work"'
teardown_test

echo ""
echo "=== test_fingerprints_root_filter ==="
setup_test
# work project
export OSORI_ROOT_KEY="work"
git -C "$TEST_TMP/fake-project" remote add origin "https://github.com/example/work-proj.git"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "work-proj" >/dev/null 2>&1

# personal project
mkdir -p "$TEST_TMP/personal-project"
git -C "$TEST_TMP/personal-project" init -q 2>/dev/null
git -C "$TEST_TMP/personal-project" config user.email "test@example.com"
git -C "$TEST_TMP/personal-project" config user.name "osori-test"
echo "personal" > "$TEST_TMP/personal-project/README.md"
git -C "$TEST_TMP/personal-project" add README.md >/dev/null 2>&1
git -C "$TEST_TMP/personal-project" commit -m "init" >/dev/null 2>&1 || true
export OSORI_ROOT_KEY="personal"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/personal-project" --name "personal-proj" >/dev/null 2>&1

output=$(bash "$PROJECT_ROOT/scripts/project-fingerprints.sh" --root work 2>&1)
assert_contains "root filter headline" "$output" "[root=work]"
assert_contains "work project visible" "$output" "work-proj"
assert_not_contains "personal project hidden" "$output" "personal-proj"
teardown_test

echo ""
echo "=== test_telegram_root_filters ==="
setup_test
export OSORI_ROOT_KEY="work"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "tg-work" >/dev/null 2>&1
mkdir -p "$TEST_TMP/tg-personal"
git -C "$TEST_TMP/tg-personal" init -q 2>/dev/null
git -C "$TEST_TMP/tg-personal" config user.email "test@example.com"
git -C "$TEST_TMP/tg-personal" config user.name "osori-test"
echo "x" > "$TEST_TMP/tg-personal/README.md"
git -C "$TEST_TMP/tg-personal" add README.md >/dev/null 2>&1
git -C "$TEST_TMP/tg-personal" commit -m "init" >/dev/null 2>&1 || true
export OSORI_ROOT_KEY="personal"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/tg-personal" --name "tg-personal" >/dev/null 2>&1

list_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" list work 2>&1)
assert_contains "telegram list root header" "$list_out" "[root=work]"
assert_contains "telegram list shows work" "$list_out" "tg-work"
assert_not_contains "telegram list hides personal" "$list_out" "tg-personal"

status_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" status work 2>&1)
assert_contains "telegram status root header" "$status_out" "[root=work]"
assert_contains "telegram status total one" "$status_out" "Total: 1"
teardown_test

echo ""
echo "=== test_root_manager_commands ==="
setup_test
mkdir -p "$TEST_TMP/root-work"

list0=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" list 2>&1)
assert_contains "root-manager list shows default" "$list0" "default"

add_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" add work Work 2>&1)
assert_contains "root-manager add root" "$add_out" "Added root: work"

path_add_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" path-add work "$TEST_TMP/root-work" 2>&1)
assert_contains "root-manager add path" "$path_add_out" "Added path to root 'work'"

label_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" set-label work "Work Team" 2>&1)
assert_contains "root-manager set label" "$label_out" "Updated label for root 'work': Work Team"

list1=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" list 2>&1)
assert_contains "root-manager list shows work root" "$list1" "work"
assert_contains "root-manager list shows updated label" "$list1" "Work Team"
assert_contains "root-manager list shows root path" "$list1" "$TEST_TMP/root-work"

path_remove_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" path-remove work "$TEST_TMP/root-work" 2>&1)
assert_contains "root-manager remove path" "$path_remove_out" "Removed path from root 'work'"

list2=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" list 2>&1)
assert_not_contains "root-manager path removed from list" "$list2" "$TEST_TMP/root-work"

remove_default_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" remove default 2>&1 || true)
assert_contains "root-manager blocks default remove" "$remove_default_out" "cannot remove protected root: default"

export OSORI_ROOT_KEY="work"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "work-owned" >/dev/null 2>&1

remove_block_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" remove work 2>&1 || true)
assert_contains "root-manager blocks remove when projects exist" "$remove_block_out" "has 1 project(s)"

remove_reassign_out=$(bash "$PROJECT_ROOT/scripts/root-manager.sh" remove work --reassign default 2>&1)
assert_contains "root-manager reassign then remove" "$remove_reassign_out" "reassigned 1 project(s)"
assert_contains "root-manager removed root after reassign" "$remove_reassign_out" "removed root: work"

post_remove=$(cat "$TEST_TMP/osori.json")
assert_not_contains "root-manager removed root from registry" "$post_remove" '"key": "work"'
assert_contains "root-manager project reassigned to default" "$post_remove" '"root": "default"'
teardown_test

echo ""
echo "=== test_telegram_root_management_commands ==="
setup_test
mkdir -p "$TEST_TMP/tg-root-path"

roots_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" list-roots 2>&1)
assert_contains "telegram list-roots works" "$roots_out" "Roots"

root_add_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" root-add work Work 2>&1)
assert_contains "telegram root-add works" "$root_add_out" "Added root: work"

root_path_add_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" root-path-add work "$TEST_TMP/tg-root-path" 2>&1)
assert_contains "telegram root-path-add works" "$root_path_add_out" "Added path to root 'work'"

root_label_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" root-set-label work "Work Team" 2>&1)
assert_contains "telegram root-set-label works" "$root_label_out" "Updated label for root 'work': Work Team"

roots_after=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" list-roots 2>&1)
assert_contains "telegram list-roots shows work root" "$roots_after" "work"
assert_contains "telegram list-roots shows label" "$roots_after" "Work Team"
assert_contains "telegram list-roots shows path" "$roots_after" "$TEST_TMP/tg-root-path"

root_path_remove_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" root-path-remove work "$TEST_TMP/tg-root-path" 2>&1)
assert_contains "telegram root-path-remove works" "$root_path_remove_out" "Removed path from root 'work'"

# remove safety via telegram wrapper
export OSORI_ROOT_KEY="work"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "tg-work-owned" >/dev/null 2>&1

root_remove_block=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" root-remove work 2>&1 || true)
assert_contains "telegram root-remove blocks when projects exist" "$root_remove_block" "has 1 project(s)"

root_remove_force=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" root-remove work --force 2>&1)
assert_contains "telegram root-remove force message" "$root_remove_force" "force mode"
assert_contains "telegram root-remove force removed" "$root_remove_force" "removed root: work"

roots_final=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" list-roots 2>&1)
assert_not_contains "telegram list-roots path removed" "$roots_final" "$TEST_TMP/tg-root-path"
assert_not_contains "telegram list-roots removed root hidden" "$roots_final" "work"
teardown_test

echo ""
echo "=== test_switch_multimatch_auto_and_index ==="
setup_test

mkdir -p "$TEST_TMP/mm-demo" "$TEST_TMP/mm-demo-app"
for p in "$TEST_TMP/mm-demo" "$TEST_TMP/mm-demo-app"; do
  git -C "$p" init -q 2>/dev/null
  git -C "$p" config user.email "test@example.com"
  git -C "$p" config user.name "osori-test"
  echo "x" > "$p/README.md"
  git -C "$p" add README.md >/dev/null 2>&1
  GIT_AUTHOR_DATE="2026-02-15T10:00:00" GIT_COMMITTER_DATE="2026-02-15T10:00:00" git -C "$p" commit -m "init" >/dev/null 2>&1 || true
done

cat > "$TEST_TMP/osori.json" << JSONEOF
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [{"key": "default", "label": "Default", "paths": []}],
  "projects": [
    {"name": "demo", "path": "$TEST_TMP/mm-demo", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"},
    {"name": "demo-app", "path": "$TEST_TMP/mm-demo-app", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"},
    {"name": "demo-missing", "path": "$TEST_TMP/no-such-dir", "repo": "", "lang": "unknown", "tags": [], "description": "", "addedAt": "2026-02-16", "root": "default"}
  ]
}
JSONEOF

auto_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" switch demo 2>&1)
assert_contains "switch shows multiple candidates" "$auto_out" "Multiple matches (3)"
assert_contains "switch auto-select message" "$auto_out" "Auto-selected #1"
assert_contains "switch auto-select picks exact name" "$auto_out" "📁 *demo*"

index_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" switch demo --index 2 2>&1)
assert_contains "switch index selection message" "$index_out" "Selected candidate #2"
assert_contains "switch index picks second candidate" "$index_out" "📁 *demo-app*"

bad_index_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" switch demo --index 9 2>&1 || true)
assert_contains "switch index out-of-range" "$bad_index_out" "--index out of range"
teardown_test

echo ""
echo "=== test_alias_commands_and_resolution ==="
setup_test

# register project
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "RunnersHeart" >/dev/null 2>&1

alias_add_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" alias-add rh RunnersHeart 2>&1)
assert_contains "alias-add works" "$alias_add_out" "alias added: rh -> RunnersHeart"

aliases_out=$(bash "$PROJECT_ROOT/scripts/alias-favorite-manager.sh" aliases 2>&1)
assert_contains "aliases list includes key" "$aliases_out" "rh -> RunnersHeart"

find_alias_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" find rh 2>&1)
assert_contains "find resolves alias" "$find_alias_out" "alias resolved: rh -> RunnersHeart"
assert_contains "find alias returns project" "$find_alias_out" "RunnersHeart"

fp_alias_out=$(bash "$PROJECT_ROOT/scripts/project-fingerprints.sh" rh 2>&1)
assert_contains "fingerprints resolves alias" "$fp_alias_out" "alias resolved: rh -> RunnersHeart"

alias_remove_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" alias-remove rh 2>&1)
assert_contains "alias-remove works" "$alias_remove_out" "alias removed: rh"
teardown_test

echo ""
echo "=== test_favorite_commands ==="
setup_test

bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "FavProj" >/dev/null 2>&1

fav_add_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" favorite-add FavProj 2>&1)
assert_contains "favorite-add works" "$fav_add_out" "favorite added: FavProj"

favs_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" favorites 2>&1)
assert_contains "favorites list shows project" "$favs_out" "FavProj"

fav_remove_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" favorite-remove FavProj 2>&1)
assert_contains "favorite-remove works" "$fav_remove_out" "favorite removed: FavProj"

favs_out2=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" favorites 2>&1)
assert_contains "favorites empty message" "$favs_out2" "No favorite projects"
teardown_test

echo ""
echo "=== test_entire_manager_commands ==="
setup_test

bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "entire-proj" >/dev/null 2>&1
FAKE_BIN="$TEST_TMP/fake-bin"
mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/entire" << 'FAKEEOF'
#!/usr/bin/env bash
echo "FAKE_ENTIRE cwd=$(pwd) args=$*"
FAKEEOF
chmod +x "$FAKE_BIN/entire"

ent_status_out=$(PATH="$FAKE_BIN:$PATH" bash "$PROJECT_ROOT/scripts/telegram-commands.sh" entire-status entire-proj 2>&1)
assert_contains "entire-status uses fake cli" "$ent_status_out" "FAKE_ENTIRE"
assert_contains "entire-status runs detailed status" "$ent_status_out" "args=status --detailed"
assert_contains "entire-status runs in project path" "$ent_status_out" "cwd=$TEST_TMP/fake-project"

ent_rewind_out=$(PATH="$FAKE_BIN:$PATH" bash "$PROJECT_ROOT/scripts/telegram-commands.sh" entire-rewind-list entire-proj 2>&1)
assert_contains "entire-rewind-list runs list mode" "$ent_rewind_out" "args=rewind --list"

ent_enable_default_out=$(PATH="$FAKE_BIN:$PATH" bash "$PROJECT_ROOT/scripts/telegram-commands.sh" entire-enable entire-proj 2>&1)
assert_contains "entire-enable default command" "$ent_enable_default_out" "args=enable"
assert_contains "entire-enable defaults agent" "$ent_enable_default_out" "--agent claude-code"
assert_contains "entire-enable defaults strategy" "$ent_enable_default_out" "--strategy manual-commit"

ent_enable_custom_out=$(PATH="$FAKE_BIN:$PATH" bash "$PROJECT_ROOT/scripts/telegram-commands.sh" entire-enable entire-proj --agent gemini --strategy auto-commit --local 2>&1)
assert_contains "entire-enable custom agent forwarded" "$ent_enable_custom_out" "--agent gemini"
assert_contains "entire-enable custom strategy forwarded" "$ent_enable_custom_out" "--strategy auto-commit"
assert_contains "entire-enable custom local flag forwarded" "$ent_enable_custom_out" "--local"
teardown_test

echo ""
echo "=== test_switch_root_filter ==="
setup_test
export OSORI_ROOT_KEY="work"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "switch-work" >/dev/null 2>&1
mkdir -p "$TEST_TMP/switch-personal"
git -C "$TEST_TMP/switch-personal" init -q 2>/dev/null
git -C "$TEST_TMP/switch-personal" config user.email "test@example.com"
git -C "$TEST_TMP/switch-personal" config user.name "osori-test"
echo "p" > "$TEST_TMP/switch-personal/README.md"
git -C "$TEST_TMP/switch-personal" add README.md >/dev/null 2>&1
git -C "$TEST_TMP/switch-personal" commit -m "init" >/dev/null 2>&1 || true
export OSORI_ROOT_KEY="personal"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/switch-personal" --name "switch-personal" >/dev/null 2>&1

ok_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" switch switch-work work 2>&1)
assert_contains "switch finds project in matching root" "$ok_out" "switch-work"
assert_contains "switch output root label" "$ok_out" "root: work"

ok_out_flag=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" switch switch-work --root work 2>&1)
assert_contains "switch supports --root flag" "$ok_out_flag" "switch-work"

bad_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" switch switch-work personal 2>&1 || true)
assert_contains "switch mismatch root not found" "$bad_out" "not found in root 'personal'"
teardown_test

echo ""
echo "=== test_find_uses_registry_root_paths_priority ==="
setup_test
mkdir -p "$TEST_TMP/work-root/priority-proj"
mkdir -p "$TEST_TMP/env-root/priority-proj"

cat > "$TEST_TMP/osori.json" << JSONEOF
{
  "schema": "osori.registry",
  "version": 2,
  "updatedAt": "2026-02-16T00:00:00Z",
  "roots": [
    {"key": "default", "label": "Default", "paths": []},
    {"key": "work", "label": "Work", "paths": ["$TEST_TMP/work-root"]}
  ],
  "projects": []
}
JSONEOF

find_out=$(OSORI_SEARCH_PATHS="$TEST_TMP/env-root" bash "$PROJECT_ROOT/scripts/telegram-commands.sh" find priority-proj work 2>&1)
assert_contains "find via search output" "$find_out" "Found via search"
assert_contains "find prefers root path over env path" "$find_out" "$TEST_TMP/work-root/priority-proj"
assert_not_contains "find does not pick env path first" "$find_out" "$TEST_TMP/env-root/priority-proj"
teardown_test

echo ""
echo "=== test_telegram_scan_root_arg ==="
setup_test
mkdir -p "$TEST_TMP/scan-repos/proj1"
git -C "$TEST_TMP/scan-repos/proj1" init -q 2>/dev/null
git -C "$TEST_TMP/scan-repos/proj1" config user.email "test@example.com"
git -C "$TEST_TMP/scan-repos/proj1" config user.name "osori-test"
echo "scan" > "$TEST_TMP/scan-repos/proj1/README.md"
git -C "$TEST_TMP/scan-repos/proj1" add README.md >/dev/null 2>&1
git -C "$TEST_TMP/scan-repos/proj1" commit -m "init" >/dev/null 2>&1 || true

scan_out=$(bash "$PROJECT_ROOT/scripts/telegram-commands.sh" scan "$TEST_TMP/scan-repos" work 2>&1)
assert_contains "telegram scan prints root" "$scan_out" "root=work"
content=$(cat "$TEST_TMP/osori.json")
assert_contains "scanned project has root key" "$content" '"root": "work"'
teardown_test

echo ""
echo "=== test_injection_safe ==="
setup_test
mkdir -p "$TEST_TMP/evil-project"
git -C "$TEST_TMP/evil-project" init -q 2>/dev/null
EVIL_NAME='test"; rm -rf /; echo "'
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/evil-project" --name "$EVIL_NAME" 2>&1 || true
valid=$(python3 - << PYEOF
import json
try:
    json.load(open('$TEST_TMP/osori.json', encoding='utf-8'))
    print('valid')
except Exception:
    print('invalid')
PYEOF
)
assert_eq "registry valid after injection attempt" "valid" "$valid"
teardown_test

echo ""
echo "=== test_registry_env ==="
setup_test
CUSTOM_PATH="$TEST_TMP/custom/path/registry.json"
export OSORI_REGISTRY="$CUSTOM_PATH"
bash "$PROJECT_ROOT/scripts/add-project.sh" "$TEST_TMP/fake-project" --name "envtest" >/dev/null 2>&1
assert_file_exists "registry at custom env path" "$CUSTOM_PATH"
content=$(cat "$CUSTOM_PATH")
assert_contains "project in custom registry" "$content" '"envtest"'
teardown_test

echo ""
echo "=== test_no_hardcoded_paths ==="
skill_content=$(cat "$PROJECT_ROOT/SKILL.md")
assert_not_contains "no /Volumes/eyedisk in SKILL.md" "$skill_content" "/Volumes/eyedisk"
assert_not_contains "no ~/Developer in SKILL.md" "$skill_content" "~/Developer"
for script in "$PROJECT_ROOT/scripts/"*.sh; do
  sc=$(cat "$script")
  sname=$(basename "$script")
  assert_not_contains "no hardcoded relative registry in $sname" "$sc" '"$(dirname "$0")/../osori.json"'
done

echo ""
echo "=== test_platform_notes ==="
skill_content=$(cat "$PROJECT_ROOT/SKILL.md")
assert_contains "SKILL.md mentions mdfind is macOS only" "$skill_content" "macOS"
assert_contains "SKILL.md mentions python3 dependency" "$skill_content" "python3"
assert_contains "SKILL.md mentions entire integration" "$skill_content" "entire"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
if [[ $FAILED -gt 0 ]]; then
  echo "Failed tests:"
  for e in "${ERRORS[@]}"; do echo "  - $e"; done
  exit 1
fi
echo "All tests passed! ✓"