#!/bin/bash
# =============================================================================
# plp-config.sh — Tool Access Policy Manager for clawd-zero-trust v1.0.0
#
# Manages zero-trust-session.json: declarative pre-session tool allow-list,
# enforcement mode, and Plan-First bootstrap settings.
#
# MODES:
#   strict     — deny unlisted tools; hard block with clear error surface
#   graceful   — warn before blocking; interactive Y/N override. Never silent.
#   audit-only — log all tool access; never block (monitoring baseline)
#
# FLAGS:
#   --show                   Print current policy (default action)
#   --set-mode MODE          Set mode: strict | graceful | audit-only
#   --allow-tool TOOL        Add TOOL to the allowed list
#   --deny-tool TOOL         Add TOOL to the denied list
#   --plan-first TOOL        Require Plan-First declaration before TOOL runs
#   --no-plan-first TOOL     Remove Plan-First requirement for TOOL
#   --sync-openclaw          Push allowed list into openclaw.json tools.byProvider
#   --reset                  Reset config to safe defaults (graceful mode)
#   --apply                  Write changes to disk (default: dry-run preview)
#   --help                   Show this message
#
# State: skills/clawd-zero-trust/.state/zero-trust-session.json
# Log:   workspace/logs/plp-config.log
# =============================================================================

set -u

# --- Paths ---
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$SKILL_DIR/.state"
STATE_FILE="$STATE_DIR/zero-trust-session.json"
OC_CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
LOG_FILE="/home/claw/.openclaw/workspace/logs/plp-config.log"

# --- UI ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# --- State ---
DRY_RUN=1
ACTION="show"
MODE_ARG=""
TOOL_ARG=""
PF_TOOL_ARG=""

# --- Helpers ---
info()   { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()     { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()   { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()   { echo -e "${RED}[FAIL]${NC}  $*" >&2; }
dryrun() { echo -e "${YELLOW}[DRY-RUN]${NC} $*"; }

log_event() {
  mkdir -p "$(dirname "$LOG_FILE")"
  touch "$LOG_FILE"
  chmod 600 "$LOG_FILE"
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] [plp-config] $*" >> "$LOG_FILE"
}

# --- Usage ---
usage() {
  cat <<EOF

${BOLD}plp-config.sh${NC} — Zero Trust Tool Access Policy Manager

USAGE: bash plp-config.sh [ACTION FLAG] [--apply]

ACTION FLAGS:
  --show                     Print current policy config (default)
  --set-mode MODE            Set enforcement mode: strict | graceful | audit-only
  --allow-tool TOOL          Add TOOL to the allowed list
  --deny-tool TOOL           Add TOOL to the denied list
  --plan-first TOOL          Require Plan-First declaration before TOOL runs
  --no-plan-first TOOL       Remove Plan-First requirement for TOOL
  --sync-openclaw            Sync allowed tools into openclaw.json tools.byProvider
  --reset                    Reset to safe defaults (graceful mode)
  --apply                    Write changes (default: dry-run)
  --help                     Show this message

MODES:
  strict      Hard deny any tool not on the allowed list.
  graceful    Warn before blocking — Y/N interactive override. Never silent.
  audit-only  Log all access. Never block. Monitoring only.

EXAMPLES:
  bash plp-config.sh --show
  bash plp-config.sh --set-mode graceful --apply
  bash plp-config.sh --allow-tool browser --apply
  bash plp-config.sh --deny-tool tts --apply
  bash plp-config.sh --plan-first exec --apply
  bash plp-config.sh --sync-openclaw --apply
  bash plp-config.sh --reset --apply

EOF
}

# --- Arg Parse ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)         DRY_RUN=0 ;;
    --show)          ACTION="show" ;;
    --reset)         ACTION="reset" ;;
    --sync-openclaw) ACTION="sync" ;;
    --help|-h)       usage; exit 0 ;;
    --set-mode)
      ACTION="set-mode"
      shift
      MODE_ARG="${1:-}"
      ;;
    --allow-tool)
      ACTION="allow-tool"
      shift
      TOOL_ARG="${1:-}"
      ;;
    --deny-tool)
      ACTION="deny-tool"
      shift
      TOOL_ARG="${1:-}"
      ;;
    --plan-first)
      ACTION="plan-first"
      shift
      PF_TOOL_ARG="${1:-}"
      ;;
    --no-plan-first)
      ACTION="no-plan-first"
      shift
      PF_TOOL_ARG="${1:-}"
      ;;
    *)
      fail "Unknown flag: $1"
      usage
      exit 1
      ;;
  esac
  shift
done

# --- Python3 JSON engine ---
# All JSON mutations are handled by inline Python3 scripts for:
#   - No jq dependency risk (jq may not be installed)
#   - Richer validation and error messages
#   - Atomic read-modify-write pattern
# The config file structure is identical to what jq would produce,
# so it remains compatible with tools.byProvider jq-based mutations in harden.sh.

py_load_or_default() {
  # Emit parsed or default config JSON to stdout
  python3 - "$STATE_FILE" <<PYEOF
import json, sys, os

path = sys.argv[1]
default = {
  "version": "1.0.0",
  "mode": "graceful",
  "updatedAt": None,
  "updatedBy": "Stan",
  "tools": {
    "allowed": ["read","write","edit","exec","message","web_search","web_fetch","session_status","tts"],
    "denied": [],
    "require_plan_first": ["exec","write","edit"]
  },
  "bootstrap": {
    "auto_plan_first": True,
    "intent_required": True,
    "authorization_required": True
  }
}

if os.path.isfile(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Malformed JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)
else:
    data = default

print(json.dumps(data))
PYEOF
}

py_show() {
  local data_file="$1"
  python3 - "$data_file" <<'PYEOF'
import json, sys

with open(sys.argv[1]) as f:
    data = json.load(f)


mode = data.get("mode", "?")
updated = data.get("updatedAt") or "never"
tools = data.get("tools", {})
allowed = tools.get("allowed", [])
denied = tools.get("denied", [])
pf = tools.get("require_plan_first", [])
bootstrap = data.get("bootstrap", {})

badges = {
    "strict":     "🔴 strict     — hard deny unlisted tools",
    "graceful":   "🟡 graceful   — warn + Y/N override before blocking",
    "audit-only": "🟢 audit-only — log only, never block"
}

print()
print(f"  Mode:            {badges.get(mode, mode)}")
print(f"  Last Updated:    {updated}")
print()
print(f"  Allowed Tools:   {', '.join(allowed) if allowed else '(none)'}")
print(f"  Denied Tools:    {', '.join(denied) if denied else '(none)'}")
print(f"  Plan-First Gate: {', '.join(pf) if pf else '(none)'}")
print()
print(f"  Auto Plan-First: {'yes' if bootstrap.get('auto_plan_first') else 'no'}")
print(f"  Intent Required: {'yes' if bootstrap.get('intent_required') else 'no'}")
print(f"  Auth Required:   {'yes' if bootstrap.get('authorization_required') else 'no'}")
print()
PYEOF
}

py_mutate() {
  # py_mutate <op> <arg>
  # ops: set-mode, allow-tool, deny-tool, plan-first, no-plan-first, reset
  local op="$1"
  local arg="$2"
  python3 - "$op" "$arg" <<PYEOF
import json, sys, datetime

op = sys.argv[1]
arg = sys.argv[2]

raw = sys.stdin.read()
data = json.loads(raw)

VALID_MODES = {"strict", "graceful", "audit-only"}

if op == "set-mode":
    if arg not in VALID_MODES:
        print(f"ERROR: Invalid mode '{arg}'. Valid values: strict | graceful | audit-only", file=sys.stderr)
        sys.exit(1)
    data["mode"] = arg

elif op == "allow-tool":
    if not arg:
        print("ERROR: tool name required for --allow-tool", file=sys.stderr)
        sys.exit(1)
    if arg not in data["tools"]["allowed"]:
        data["tools"]["allowed"].append(arg)
    # ensure not in denied
    data["tools"]["denied"] = [t for t in data["tools"]["denied"] if t != arg]

elif op == "deny-tool":
    if not arg:
        print("ERROR: tool name required for --deny-tool", file=sys.stderr)
        sys.exit(1)
    if arg not in data["tools"]["denied"]:
        data["tools"]["denied"].append(arg)
    # remove from allowed
    data["tools"]["allowed"] = [t for t in data["tools"]["allowed"] if t != arg]

elif op == "plan-first":
    if not arg:
        print("ERROR: tool name required for --plan-first", file=sys.stderr)
        sys.exit(1)
    if arg not in data["tools"]["require_plan_first"]:
        data["tools"]["require_plan_first"].append(arg)

elif op == "no-plan-first":
    if not arg:
        print("ERROR: tool name required for --no-plan-first", file=sys.stderr)
        sys.exit(1)
    data["tools"]["require_plan_first"] = [t for t in data["tools"]["require_plan_first"] if t != arg]

elif op == "reset":
    data = {
      "version": "1.0.0",
      "mode": "graceful",
      "updatedAt": None,
      "updatedBy": "Stan",
      "tools": {
        "allowed": ["read","write","edit","exec","message","web_search","web_fetch","session_status","tts"],
        "denied": [],
        "require_plan_first": ["exec","write","edit"]
      },
      "bootstrap": {
        "auto_plan_first": True,
        "intent_required": True,
        "authorization_required": True
      }
    }

data["updatedAt"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
print(json.dumps(data, indent=2))
PYEOF
}

py_sync_openclaw() {
  # Emit updated openclaw.json JSON to stdout
  python3 - "$STATE_FILE" "$OC_CONFIG" <<PYEOF
import json, sys, datetime

state_path = sys.argv[1]
oc_path = sys.argv[2]

with open(state_path) as f:
    state = json.load(f)
with open(oc_path) as f:
    oc = json.load(f)

allowed = state.get("tools", {}).get("allowed", [])
denied = state.get("tools", {}).get("denied", [])
mode = state.get("mode", "graceful")
synced_at = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# Model tiers: flash-class models get PLP restriction
# Anthropic/Claude models are trusted (no restriction pushed here)
FLASH_MODEL = "google-antigravity/gemini-3-flash"

if "tools" not in oc:
    oc["tools"] = {}
if "byProvider" not in oc["tools"]:
    oc["tools"]["byProvider"] = {}

existing = oc["tools"]["byProvider"].get(FLASH_MODEL, {})

if mode in ("strict", "graceful"):
    # Merge: existing openclaw allow list UNION plp-config allowed list
    existing_allow = existing.get("allow", [])
    merged = sorted(set(existing_allow) | set(allowed) - set(denied))
    oc["tools"]["byProvider"][FLASH_MODEL] = {
        "profile": existing.get("profile", "coding"),
        "allow": merged,
        "_plp_mode": mode,
        "_plp_synced_at": synced_at
    }
elif mode == "audit-only":
    # audit-only: preserve existing config, just tag it
    oc["tools"]["byProvider"][FLASH_MODEL] = {
        **existing,
        "_plp_mode": "audit-only",
        "_plp_synced_at": synced_at
    }

print(json.dumps(oc, indent=2))
PYEOF
}

# --- State helpers ---
ensure_state_dir() {
  mkdir -p "$STATE_DIR"
  chmod 700 "$STATE_DIR"
}

write_state() {
  local new_json="$1"
  local context="$2"
  if [ "$DRY_RUN" -eq 1 ]; then
    dryrun "$context (dry-run — pass --apply to write)"
    echo "$new_json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"  mode: {d['mode']} | allowed: {len(d['tools']['allowed'])} | denied: {len(d['tools']['denied'])}\")
"
  else
    ensure_state_dir
    local tmp
    tmp=$(mktemp "$STATE_DIR/.tmp.XXXXXX")
    echo "$new_json" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    chmod 600 "$STATE_FILE"
    ok "$context"
    log_event "$context"
  fi
}

# --- Actions ---

action_show() {
  ensure_state_dir
  echo ""
  echo -e "${BOLD}🔐 Zero Trust Tool Access Policy${NC}"
  echo "   State: $STATE_FILE"
  echo "=================================================="

  local data
  if ! data=$(py_load_or_default); then
    fail "Failed to load config"
    exit 1
  fi

  if [ ! -f "$STATE_FILE" ]; then
    warn "Config not yet initialized — showing defaults."
    warn "Run: bash plp-config.sh --reset --apply  to write defaults to disk."
  fi

  local tmpf
  tmpf=$(mktemp /tmp/plp-show.XXXXXX)
  echo "$data" > "$tmpf"
  py_show "$tmpf"
  rm -f "$tmpf"
}

action_set_mode() {
  if [ -z "$MODE_ARG" ]; then
    fail "--set-mode requires a value: strict | graceful | audit-only"
    exit 1
  fi

  ensure_state_dir
  local current new_json
  current=$(py_load_or_default) || exit 1
  new_json=$(echo "$current" | py_mutate "set-mode" "$MODE_ARG") || exit 1

  write_state "$new_json" "Mode set to: $MODE_ARG"
}

action_allow_tool() {
  if [ -z "$TOOL_ARG" ]; then
    fail "--allow-tool requires a tool name"
    exit 1
  fi

  ensure_state_dir
  local current new_json
  current=$(py_load_or_default) || exit 1
  new_json=$(echo "$current" | py_mutate "allow-tool" "$TOOL_ARG") || exit 1

  write_state "$new_json" "Allowed tool: $TOOL_ARG"
}

action_deny_tool() {
  if [ -z "$TOOL_ARG" ]; then
    fail "--deny-tool requires a tool name"
    exit 1
  fi

  ensure_state_dir
  local current new_json
  current=$(py_load_or_default) || exit 1
  new_json=$(echo "$current" | py_mutate "deny-tool" "$TOOL_ARG") || exit 1

  write_state "$new_json" "Denied tool: $TOOL_ARG"
}

action_plan_first() {
  local op="$1"
  if [ -z "$PF_TOOL_ARG" ]; then
    fail "--plan-first / --no-plan-first requires a tool name"
    exit 1
  fi

  ensure_state_dir
  local current new_json
  current=$(py_load_or_default) || exit 1
  new_json=$(echo "$current" | py_mutate "$op" "$PF_TOOL_ARG") || exit 1

  write_state "$new_json" "$op applied: $PF_TOOL_ARG"
}

action_reset() {
  ensure_state_dir

  local dummy new_json
  dummy='{}'
  new_json=$(echo "$dummy" | py_mutate "reset" "") || exit 1

  if [ "$DRY_RUN" -eq 1 ]; then
    dryrun "Would reset $STATE_FILE to safe defaults:"
    echo "$new_json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"  mode: {d['mode']}\")
print(f\"  allowed: {', '.join(d['tools']['allowed'])}\")
print(f\"  denied: {', '.join(d['tools']['denied']) or '(none)'}\")
print(f\"  plan-first: {', '.join(d['tools']['require_plan_first'])}\")
"
    dryrun "Pass --apply to write."
  else
    if [ -f "$STATE_FILE" ]; then
      local bak
      bak="$STATE_FILE.bak.$(date -u +%Y%m%d%H%M%S)"
      cp "$STATE_FILE" "$bak"
      info "Backup: $bak"
    fi
    local tmp
    tmp=$(mktemp "$STATE_DIR/.tmp.XXXXXX")
    echo "$new_json" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    chmod 600 "$STATE_FILE"
    ok "Config reset to defaults (graceful mode)"
    log_event "config reset to defaults"
  fi
}

action_sync_openclaw() {
  if [ ! -f "$STATE_FILE" ]; then
    fail "No config at $STATE_FILE — run: bash plp-config.sh --reset --apply"
    exit 1
  fi
  if [ ! -f "$OC_CONFIG" ]; then
    fail "openclaw.json not found: $OC_CONFIG"
    exit 1
  fi

  info "Computing PLP sync into tools.byProvider..."

  local new_oc
  if ! new_oc=$(py_sync_openclaw); then
    fail "Sync computation failed — aborting. openclaw.json untouched."
    exit 1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    dryrun "Would write tools.byProvider to $OC_CONFIG:"
    echo "$new_oc" | python3 -c "
import json, sys
d = json.load(sys.stdin)
bp = d.get('tools', {}).get('byProvider', {})
print(json.dumps(bp, indent=4))
"
    dryrun "Pass --apply to write."
  else
    local bak
    bak="$OC_CONFIG.bak.plp.$(date -u +%Y%m%d%H%M%S)"
    cp "$OC_CONFIG" "$bak"
    info "Backed up openclaw.json → $bak"
    local tmp
    tmp=$(mktemp /tmp/oc-plp.XXXXXX)
    echo "$new_oc" > "$tmp"
    mv "$tmp" "$OC_CONFIG"
    ok "Synced PLP policy into openclaw.json (tools.byProvider)"
    log_event "synced policy to openclaw.json backup=$bak"
    warn "OpenClaw restart may be required for changes to take effect."
  fi
}

# --- Pre-flight ---
echo ""
echo -e "${BOLD}🔐 plp-config.sh${NC} — Zero Trust Tool Access Policy  [clawd-zero-trust v1.0.0]"
echo "=========================================================================="
if [ "$DRY_RUN" -eq 1 ]; then
  echo -e "${YELLOW}  Mode: DRY-RUN (default). Pass --apply to commit changes.${NC}"
else
  echo -e "${RED}  Mode: APPLY — changes will be written to disk.${NC}"
fi
echo ""

if ! command -v python3 &>/dev/null; then
  fail "python3 is required but not found. Install: sudo apt install python3"
  exit 1
fi

# Verify Python3 json module is available
if ! python3 -c "import json" 2>/dev/null; then
  fail "python3 json module is required but not available"
  exit 1
fi

# --- Dispatch ---
case "$ACTION" in
  show)          action_show ;;
  set-mode)      action_set_mode ;;
  allow-tool)    action_allow_tool ;;
  deny-tool)     action_deny_tool ;;
  plan-first)    action_plan_first "plan-first" ;;
  no-plan-first) action_plan_first "no-plan-first" ;;
  reset)         action_reset ;;
  sync)          action_sync_openclaw ;;
  *)
    fail "Unknown action: $ACTION"
    usage
    exit 1
    ;;
esac
