#!/bin/bash
# =============================================================================
# Plugin Integrity Hashing — clawd-zero-trust
# v1.3.0: Initial implementation
#
# Monitors OpenClaw plugin file integrity via SHA-256 hashing.
# Detects unauthorized modifications, new/removed plugins, and drift
# from the hardening.json allowlist.
#
# Subcommands:
#   --snapshot  Compute and store SHA-256 hashes for all installed plugins
#   --verify    Compare current hashes against stored snapshot
#   --drift     Check loaded plugins against hardening.json allowlist
# =============================================================================

set -u

SNAPSHOT_MODE=0
VERIFY_MODE=0
DRIFT_MODE=0

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$SKILL_DIR/.state"
HASH_FILE="$STATE_DIR/plugin-hashes.json"
HARDENING_FILE="$SKILL_DIR/hardening.json"
EXTENSIONS_DIR="$HOME/.openclaw/extensions"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

usage() {
  cat <<EOF
Usage: bash $0 [--snapshot] [--verify] [--drift]

Subcommands:
  --snapshot   Compute SHA-256 hashes for all installed plugins, store in .state/plugin-hashes.json
  --verify     Compare current plugin hashes against stored snapshot. Exit 1 on mismatch.
  --drift      Compare loaded plugins against hardening.json allowlist. Alert on new/removed.

Combine flags to run multiple checks:
  bash $0 --verify --drift
EOF
}

if [ $# -eq 0 ]; then
  usage
  exit 0
fi

for arg in "$@"; do
  case "$arg" in
    --snapshot) SNAPSHOT_MODE=1 ;;
    --verify)   VERIFY_MODE=1 ;;
    --drift)    DRIFT_MODE=1 ;;
    -h|--help)  usage; exit 0 ;;
    *) echo -e "${RED}[ERROR]${NC} Unknown arg: $arg"; usage; exit 1 ;;
  esac
done

mkdir -p "$STATE_DIR"

# ---------------------------------------------------------------------------
# find_plugin_js <plugin_dir>
# Locate the primary JS entry point for a plugin. Priority:
#   1. dist/index.js  (compiled TS plugins)
#   2. index.js       (simple plugins)
#   3. first *.js     (fallback)
# Returns the path on stdout, or empty string if none found.
# ---------------------------------------------------------------------------
find_plugin_js() {
  local pdir="$1"
  if [ -f "$pdir/dist/index.js" ]; then
    echo "$pdir/dist/index.js"
  elif [ -f "$pdir/index.js" ]; then
    echo "$pdir/index.js"
  else
    # Fallback: first .js file found (non-recursive in root)
    local first_js
    first_js="$(find "$pdir" -maxdepth 1 -name '*.js' -type f 2>/dev/null | head -1)"
    if [ -n "$first_js" ]; then
      echo "$first_js"
    fi
  fi
}

# ---------------------------------------------------------------------------
# do_snapshot: Compute SHA-256 for each plugin and store in JSON
# [NEW-3 v1.3.0-r3] Fully Python-based: bash collects plugin dirs as NUL-
# delimited list, Python does all hashing + JSON serialization. Zero bash-
# level string splitting of hash data. Handles spaces/unicode/special chars.
# ---------------------------------------------------------------------------
do_snapshot() {
  echo -e "${CYAN}[SNAPSHOT]${NC} Computing plugin integrity hashes..."

  if [ ! -d "$EXTENSIONS_DIR" ]; then
    echo -e "${YELLOW}[WARN]${NC} Extensions directory not found: $EXTENSIONS_DIR"
    echo -e "${YELLOW}[WARN]${NC} No plugins to snapshot."
    return 0
  fi

  # Collect plugin directory paths as NUL-delimited list (safe for all filenames)
  local plugin_dirs=""
  for pdir in "$EXTENSIONS_DIR"/*/; do
    [ ! -d "$pdir" ] && continue
    if [ -n "$plugin_dirs" ]; then
      plugin_dirs="${plugin_dirs}"$'\0'"${pdir}"
    else
      plugin_dirs="${pdir}"
    fi
  done

  # Python does all the work: find JS entry, hash, write JSON atomically
  python3 - "$HASH_FILE" "$HOME" <<'PYEOF' < <(printf '%s' "$plugin_dirs")
import json, sys, os, hashlib
from datetime import datetime, timezone
from pathlib import Path

hash_file = sys.argv[1]
home_dir = sys.argv[2]

# Read NUL-delimited plugin dirs from stdin
raw = sys.stdin.buffer.read()
if not raw:
    print("  No plugins found to snapshot.")
    sys.exit(0)

plugin_dirs = [d for d in raw.decode('utf-8', errors='replace').split('\0') if d.strip()]

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
plugins = {}
count = 0

for pdir in plugin_dirs:
    pdir = pdir.rstrip('/')
    pname = os.path.basename(pdir)

    # Find JS entry point: dist/index.js > index.js > first *.js
    js_path = None
    candidate = os.path.join(pdir, 'dist', 'index.js')
    if os.path.isfile(candidate):
        js_path = candidate
    else:
        candidate = os.path.join(pdir, 'index.js')
        if os.path.isfile(candidate):
            js_path = candidate
        else:
            # Fallback: first .js in root
            try:
                for f in sorted(os.listdir(pdir)):
                    if f.endswith('.js') and os.path.isfile(os.path.join(pdir, f)):
                        js_path = os.path.join(pdir, f)
                        break
            except OSError:
                pass

    if not js_path:
        print(f"  \033[1;33m⚠️\033[0m  {pname} — no JS entry point found, skipping")
        continue

    # Compute SHA-256
    sha = hashlib.sha256()
    try:
        with open(js_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha.update(chunk)
    except OSError as e:
        print(f"  \033[0;31m❌\033[0m  {pname} — read error: {e}")
        continue

    file_hash = sha.hexdigest()
    rel_path = js_path
    if js_path.startswith(home_dir + '/'):
        rel_path = js_path[len(home_dir) + 1:]

    plugins[pname] = {
        'hash': file_hash,
        'path': rel_path,
        'snapshotAt': now
    }

    basename = os.path.basename(js_path)
    print(f"  \033[0;32m✅\033[0m {pname} → {file_hash[:16]}... ({basename})")
    count += 1

# Write JSON atomically (write to tmp, rename)
os.makedirs(os.path.dirname(hash_file), exist_ok=True)
tmp_path = hash_file + '.tmp'
with open(tmp_path, 'w', encoding='utf-8') as f:
    json.dump({
        'version': '1.3.0',
        'generatedAt': now,
        'plugins': plugins
    }, f, indent=2)
    f.write('\n')
os.replace(tmp_path, hash_file)

print(f"\n\033[0;32m[DONE]\033[0m Snapshot saved: {hash_file} ({count} plugins)")
PYEOF

  local rc=$?
  [ -f "$HASH_FILE" ] && chmod 600 "$HASH_FILE"
  return "$rc"
}

# ---------------------------------------------------------------------------
# do_verify: Compare current hashes vs stored snapshot
# [NEW-3 v1.3.0-r3] Fully Python-based: reads JSON snapshot, rehashes files
# in Python, compares in Python. Zero bash-level string splitting of hash
# comparison data. Handles spaces/unicode/special chars in plugin paths.
# ---------------------------------------------------------------------------
do_verify() {
  echo -e "${CYAN}[VERIFY]${NC} Checking plugin integrity against stored hashes..."

  if [ ! -f "$HASH_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} No snapshot found at: $HASH_FILE"
    echo -e "  Run --snapshot first to establish a baseline."
    return 1
  fi

  if [ ! -d "$EXTENSIONS_DIR" ]; then
    echo -e "${YELLOW}[WARN]${NC} Extensions directory not found: $EXTENSIONS_DIR"
    return 1
  fi

  # Collect current plugin directory paths as NUL-delimited list
  local plugin_dirs=""
  for pdir in "$EXTENSIONS_DIR"/*/; do
    [ ! -d "$pdir" ] && continue
    if [ -n "$plugin_dirs" ]; then
      plugin_dirs="${plugin_dirs}"$'\0'"${pdir}"
    else
      plugin_dirs="${pdir}"
    fi
  done

  # Python does everything: load snapshot, hash current files, compare, report
  python3 - "$HASH_FILE" "$EXTENSIONS_DIR" <<'PYEOF' < <(printf '%s' "$plugin_dirs")
import json, sys, os, hashlib

hash_file = sys.argv[1]
extensions_dir = sys.argv[2]

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

# Load stored snapshot
try:
    with open(hash_file, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)
except (json.JSONDecodeError, ValueError, OSError) as e:
    print(f"  {YELLOW}[WARN]{NC} Snapshot is empty or malformed: {e}")
    sys.exit(1)

stored_plugins = snapshot.get('plugins', {})
if not stored_plugins:
    print(f"  {YELLOW}[WARN]{NC} Snapshot contains no plugins.")
    sys.exit(1)

# Read NUL-delimited current plugin dirs from stdin
raw = sys.stdin.buffer.read()
current_dirs = {}
if raw:
    for d in raw.decode('utf-8', errors='replace').split('\0'):
        d = d.rstrip('/')
        if d:
            current_dirs[os.path.basename(d)] = d

def find_plugin_js(pdir):
    """Find JS entry point: dist/index.js > index.js > first *.js"""
    candidate = os.path.join(pdir, 'dist', 'index.js')
    if os.path.isfile(candidate):
        return candidate
    candidate = os.path.join(pdir, 'index.js')
    if os.path.isfile(candidate):
        return candidate
    try:
        for f in sorted(os.listdir(pdir)):
            if f.endswith('.js') and os.path.isfile(os.path.join(pdir, f)):
                return os.path.join(pdir, f)
    except OSError:
        pass
    return None

def sha256_file(path):
    """Compute SHA-256 of a file."""
    sha = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                sha.update(chunk)
        return sha.hexdigest()
    except OSError:
        return None

mismatches = 0
checked = 0
missing = 0

# Check stored plugins against current state
for pname in sorted(stored_plugins.keys()):
    stored = stored_plugins[pname]
    stored_hash = stored.get('hash', '')
    checked += 1

    pdir = os.path.join(extensions_dir, pname)
    if not os.path.isdir(pdir):
        print(f"  {RED}⚠️  REMOVED:{NC} {pname} — plugin directory no longer exists")
        missing += 1
        continue

    js_path = find_plugin_js(pdir)
    if not js_path:
        print(f"  {RED}⚠️  CHANGED:{NC} {pname} — JS entry point no longer exists")
        mismatches += 1
        continue

    current_hash = sha256_file(js_path)
    if current_hash is None:
        print(f"  {RED}⚠️  CHANGED:{NC} {pname} — cannot read file")
        mismatches += 1
        continue

    if current_hash == stored_hash:
        print(f"  {GREEN}✅ MATCH:{NC}   {pname}")
    else:
        print(f"  {RED}⚠️  CHANGED:{NC} {pname}")
        print(f"     Stored:  {stored_hash[:16]}...")
        print(f"     Current: {current_hash[:16]}...")
        mismatches += 1

# Check for new plugins not in snapshot
stored_names = set(stored_plugins.keys())
for pname in sorted(current_dirs.keys()):
    if pname not in stored_names:
        print(f"  {YELLOW}⚠️  NEW:{NC}     {pname} — not in snapshot (run --snapshot to add)")
        mismatches += 1

print()
if mismatches > 0 or missing > 0:
    print(f"{RED}[INTEGRITY FAILURE]{NC} {mismatches} changed, {missing} removed out of {checked} checked")
    sys.exit(1)

print(f"{GREEN}[INTEGRITY OK]{NC} All {checked} plugins match stored hashes")
PYEOF

  return $?
}

# ---------------------------------------------------------------------------
# do_drift: Compare loaded plugins against hardening.json allowlist
# ---------------------------------------------------------------------------
do_drift() {
  echo -e "${CYAN}[DRIFT]${NC} Checking plugins against hardening.json allowlist..."

  if [ ! -f "$HARDENING_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} hardening.json not found: $HARDENING_FILE"
    return 1
  fi

  # [FINDING-9 v1.3.0-r2] Safe JSON parsing — handle missing keys, malformed JSON
  local allowed_json
  if ! allowed_json="$(python3 -c "
import json, sys
try:
    with open(sys.argv[1], 'r') as f:
        d = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    print(f'JSON_ERROR: {e}', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'READ_ERROR: {e}', file=sys.stderr)
    sys.exit(1)
allow = d.get('plugins', {}).get('allow', [])
print(json.dumps(allow))
" "$HARDENING_FILE" 2>&1)"; then
    echo -e "${RED}[ERROR]${NC} hardening.json is malformed: $allowed_json"
    return 1
  fi

  local allowed_plugins
  allowed_plugins="$(python3 -c "
import json, sys
allow = json.loads(sys.argv[1])
for p in sorted(allow):
    print(p)
" "$allowed_json" 2>/dev/null)"

  if [ -z "$allowed_plugins" ]; then
    echo -e "${YELLOW}[WARN]${NC} plugins.allow key missing or empty in hardening.json — treating as empty allowlist []"
    # Not fatal — continue with empty allowlist to still detect unauthorized plugins
  fi

  # Get currently installed plugins from filesystem (authoritative source)
  local installed_plugins=""
  if [ -d "$EXTENSIONS_DIR" ]; then
    for pdir in "$EXTENSIONS_DIR"/*/; do
      [ ! -d "$pdir" ] && continue
      local pname
      pname="$(basename "$pdir")"
      if [ -n "$installed_plugins" ]; then
        installed_plugins="${installed_plugins}"$'\n'"${pname}"
      else
        installed_plugins="${pname}"
      fi
    done
  fi

  # Deduplicate and clean
  local all_loaded
  all_loaded="$(echo "$installed_plugins" | sort -u | grep -v '^$')"

  local drift_found=0

  echo -e "\n  ${CYAN}Allowlisted plugins:${NC}"
  while IFS= read -r ap; do
    [ -z "$ap" ] && continue
    # [FINDING-11 v1.3.0-r2] Use grep -Fx for exact fixed-string line matching
    if echo "$all_loaded" | grep -Fxq "$ap" 2>/dev/null; then
      echo -e "    ${GREEN}✅${NC} $ap — present"
    else
      echo -e "    ${YELLOW}⚠️${NC}  $ap — allowlisted but NOT installed"
      drift_found=$((drift_found + 1))
    fi
  done <<< "$allowed_plugins"

  echo -e "\n  ${CYAN}Installed plugins:${NC}"
  while IFS= read -r ip; do
    [ -z "$ip" ] && continue
    # [FINDING-11 v1.3.0-r2] Use grep -Fx for exact fixed-string line matching
    if echo "$allowed_plugins" | grep -Fxq "$ip" 2>/dev/null; then
      echo -e "    ${GREEN}✅${NC} $ip — allowlisted"
    else
      echo -e "    ${RED}🚨 UNAUTHORIZED:${NC} $ip — NOT in hardening.json allowlist"
      drift_found=$((drift_found + 1))
    fi
  done <<< "$all_loaded"

  echo ""
  if [ "$drift_found" -gt 0 ]; then
    echo -e "${RED}[DRIFT DETECTED]${NC} $drift_found discrepancies between installed plugins and allowlist"
    return 1
  fi

  echo -e "${GREEN}[NO DRIFT]${NC} All installed plugins match allowlist"
  return 0
}

# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------
echo ""
echo "🔐 Plugin Integrity Check — $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "=================================================="

exit_code=0

if [ "$SNAPSHOT_MODE" -eq 1 ]; then
  do_snapshot || exit_code=1
  echo ""
fi

if [ "$VERIFY_MODE" -eq 1 ]; then
  do_verify || exit_code=1
  echo ""
fi

if [ "$DRIFT_MODE" -eq 1 ]; then
  do_drift || exit_code=1
  echo ""
fi

echo "=================================================="
exit "$exit_code"
