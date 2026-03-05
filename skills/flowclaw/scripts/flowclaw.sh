#!/bin/bash
# FlowClaw — LLM Usage Monitor & Intelligent Load Balancer
# Track usage across all your LLM subscriptions in one place,
# and optionally auto-balance routing to maximize every credit.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOKEN_DIR="${TOKEN_DIR:-$HOME/.openclaw/usage-tokens}"
STATE_FILE="$SCRIPT_DIR/../config/flowclaw-state.json"
HISTORY_FILE="$SCRIPT_DIR/../config/flowclaw-history.jsonl"
CACHE_FILE="/tmp/provider-usage-cache"

# ── Banner ───────────────────────────────────────────────────────────

show_banner() {
  cat <<'BANNER'

 ███████╗██╗      ██████╗ ██╗    ██╗
 ██╔════╝██║     ██╔═══██╗██║    ██║
 █████╗  ██║     ██║   ██║██║ █╗ ██║
 ██╔══╝  ██║     ██║   ██║██║███╗██║
 ██║     ███████╗╚██████╔╝╚███╔███╔╝
 ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝
      ██████╗██╗      █████╗ ██╗    ██╗
     ██╔════╝██║     ██╔══██╗██║    ██║
     ██║     ██║     ███████║██║ █╗ ██║
     ██║     ██║     ██╔══██║██║███╗██║
     ╚██████╗███████╗██║  ██║╚███╔███╔╝
      ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝

 🦞 LLM subscription usage monitoring
 and load balancing for OpenClaw.

BANNER
}

# ── Helpers ──────────────────────────────────────────────────────────

usage_collector() {
  bash "$SCRIPT_DIR/provider-usage.sh" --json --fresh 2>/dev/null
}

scoring_engine() {
  python3 "$SCRIPT_DIR/scoring-engine.py" "$@"
}

log_history() {
  local primary="$1" action="$2" reason="${3:-}"
  mkdir -p "$(dirname "$HISTORY_FILE")"
  python3 -c "
import json, datetime
entry = {
    'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'primary': '$primary',
    'action': '$action',
    'reason': '$reason'
}
with open('$HISTORY_FILE', 'a') as f:
    f.write(json.dumps(entry) + '\n')
"
}

# ── Commands ─────────────────────────────────────────────────────────

cmd_status() {
  bash "$SCRIPT_DIR/provider-usage.sh" "$@"
}

cmd_monitor() {
  local format_flag=""
  local fresh_flag="--fresh"
  while [[ $# -gt 0 ]]; do
    case $1 in
      --json) format_flag="--json"; shift ;;
      --cached) fresh_flag=""; shift ;;
      *) shift ;;
    esac
  done

  # Collect usage data
  local usage_json
  usage_json=$(bash "$SCRIPT_DIR/provider-usage.sh" --json $fresh_flag 2>/dev/null)

  if [ -z "$usage_json" ] || [ "$usage_json" = "{}" ]; then
    echo "❌ No usage data available. Check provider configuration."
    exit 1
  fi

  if [ -n "$format_flag" ]; then
    echo "$usage_json"
    return
  fi

  # Human-readable usage report (no scoring, no routing recommendations)
  echo "📊 FlowClaw Usage Report"
  echo ""

  python3 - "$usage_json" <<'PYEOF'
import json, sys
from datetime import datetime, timezone

data = json.loads(sys.argv[1])

for provider_name, provider in data.items():
    if provider_name == "_meta":
        continue
    print(f"  ━━━ {provider.get('display_name', provider_name)} ━━━")
    print()

    accounts = provider.get("accounts", [])
    if not accounts:
        accounts = [provider]  # single-account provider

    for acct in accounts:
        name = acct.get("display_name", acct.get("email", acct.get("id", "unknown")))
        print(f"  👤 {name}")

        windows = acct.get("windows", [])
        for w in windows:
            label = w.get("label", w.get("type", "??"))
            pct = w.get("usage_pct", 0)
            remaining = w.get("remaining_str", "")

            bar_width = 10
            filled = int(pct / 100 * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)

            if pct >= 90:
                color = "🔴"
            elif pct >= 60:
                color = "🟡"
            else:
                color = "🟢"

            line = f"     {label:15s} {color} {bar} {pct:3.0f}%"
            if remaining:
                line += f"  ⏳{remaining}"
            print(line)

        extra = acct.get("extra_usage", {})
        if extra:
            spent = extra.get("spent", 0)
            limit = extra.get("limit", 0)
            if spent > 0 or limit > 0:
                print(f"     💰 Extra usage:    ${spent:.2f}/${limit:.2f}")
        print()

print(f"  📍 {datetime.now().strftime('%I:%M %p %Z')} · {datetime.now().strftime('%b %d, %Y')}")
PYEOF
}

cmd_score() {
  local format_flag=""
  if [[ "${1:-}" == "--json" ]]; then format_flag="--json"; fi

  local usage_json
  usage_json=$(usage_collector)

  if [ -z "$usage_json" ] || [ "$usage_json" = "{}" ]; then
    echo "❌ No usage data available. Check provider configuration."
    exit 1
  fi

  echo "$usage_json" | scoring_engine $format_flag
}

cmd_optimize() {
  local dry_run=0
  local verbose=0
  while [[ $# -gt 0 ]]; do
    case $1 in
      --dry-run) dry_run=1; shift ;;
      --verbose|-v) verbose=1; shift ;;
      *) shift ;;
    esac
  done

  # Collect and score
  local usage_json
  usage_json=$(usage_collector)
  local scored_json
  scored_json=$(echo "$usage_json" | scoring_engine --json)

  # Extract recommendations — FAMILY-AWARE routing
  # Only recommend switching to a model in the same capability family as current primary
  local recommended_primary
  local anthropic_order
  read -r recommended_primary anthropic_order < <(echo "$scored_json" | python3 -c "
import json, sys, subprocess

d = json.load(sys.stdin)

# Get current primary model from openclaw config
try:
    import pathlib, os
    cfg_path = pathlib.Path(os.path.expanduser('~/.openclaw/openclaw.json'))
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        current_primary = cfg.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', '')
    else:
        current_primary = ''
except:
    current_primary = ''

# Determine current model family
def get_family(model):
    m = model.lower()
    if 'opus' in m: return 'opus'
    if 'sonnet' in m: return 'sonnet'
    if 'gemini-3-pro' in m or 'gemini-pro' in m: return 'gemini-pro'
    if 'gemini-3-flash' in m or 'gemini-flash' in m: return 'gemini-flash'
    return 'other'

current_family = get_family(current_primary) if current_primary else 'opus'

# Find best available model in the SAME family
ranked = d.get('ranked', [])
best_same_family = None
for r in ranked:
    if r['available'] and get_family(r['model']) == current_family:
        best_same_family = r['model']
        break

# Fallback: if no same-family available, use overall best
if not best_same_family:
    best_same_family = d.get('recommended_primary', '')

# Anthropic order (unchanged)
order = d.get('recommended_anthropic_order', [])

print(f\"{best_same_family or ''} {' '.join(order)}\")
")

  # Get ranked summary for display
  local ranked_summary
  ranked_summary=$(echo "$scored_json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for r in d.get('ranked', []):
    status = '✅' if r['available'] else '🚫'
    print(f\"  #{r['rank']}  {status} {r['account']:15s}  score={r['score']:.4f}  {r['reason']}\")
")

  echo "🧠 FlowClaw Optimization"
  echo ""
  echo "$ranked_summary"
  echo ""

  if [ -z "$recommended_primary" ]; then
    echo "⚠️  All accounts exhausted — no routing change needed."
    log_history "none" "skip" "all_exhausted"
    return
  fi

  echo "  🎯 Recommended primary: $recommended_primary"
  echo "  📋 Anthropic profile order: $anthropic_order"
  echo ""

  # ── Info: switching to Google provider ──
  if [[ "$recommended_primary" == google-gemini-cli/* ]]; then
    echo "  ℹ️  Routing to Google (Gemini CLI) — free tier credits available"
    echo ""
  fi

  if [ "$dry_run" -eq 1 ]; then
    echo "  🔍 DRY RUN — no changes applied."
    echo ""
    echo "  Would run:"
    echo "    openclaw models auth order set --provider anthropic $anthropic_order"
    echo "    Set primary model → $recommended_primary"
    echo "    Reorganize fallbacks accordingly"
    return
  fi

  # Apply changes
  echo "  ⚙️  Applying..."

  # 1. Reorder Anthropic profiles
  if [ -n "$anthropic_order" ]; then
    openclaw models auth order set --provider anthropic $anthropic_order 2>/dev/null && \
      echo "  ✅ Anthropic profile order updated" || \
      echo "  ⚠️  Failed to update Anthropic profile order"
  fi

  # 2. Swap primary + fallbacks in openclaw.json
  # We need to edit the JSON directly because `openclaw config set` only sets
  # the primary but doesn't reorganize fallbacks
  python3 << PYEOF
import json

config_path = "$HOME/.openclaw/openclaw.json"
recommended = "$recommended_primary"

with open(config_path) as f:
    cfg = json.load(f)

model_cfg = cfg.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})
current_primary = model_cfg.get("primary", "")
current_fallbacks = model_cfg.get("fallbacks", [])

# Build consolidated model list: recommended first, then all others
all_models = [current_primary] + current_fallbacks
# Remove duplicates while preserving order
seen = set()
unique_models = []
for m in all_models:
    if m and m not in seen:
        seen.add(m)
        unique_models.append(m)

# Move recommended to primary, everything else to fallbacks
if recommended in unique_models:
    unique_models.remove(recommended)

model_cfg["primary"] = recommended
model_cfg["fallbacks"] = unique_models

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=4)

print(f"  ✅ Primary model set to {recommended}")
print(f"  ✅ Fallbacks: {', '.join(unique_models)}")
PYEOF

  # Log to history
  log_history "$recommended_primary" "optimize" "scored_switch"

  # Restart gateway to pick up config changes
  echo ""
  echo "  🔄 Restarting gateway..."
  if openclaw gateway restart 2>/dev/null; then
    echo "  ✅ Gateway restarted — new routing active"
  else
    echo "  ⚠️  Gateway restart failed — run 'openclaw gateway restart' manually"
  fi

  # Save state
  python3 -c "
import json
state = {
    'last_run': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'action': 'optimize',
    'primary': '$recommended_primary',
    'anthropic_order': '$anthropic_order'.split(),
}
json.dump(state, open('$STATE_FILE', 'w'), indent=2)
"

  echo ""
  echo "  ✅ FlowClaw optimized!"
  rm -f "$CACHE_FILE"
}

cmd_auto() {
  cmd_optimize "$@" 2>&1 | tee -a /tmp/flowclaw-auto.log
}

cmd_test() {
  scoring_engine --test
}

cmd_history() {
  local num_entries="${1:-20}"

  if [ ! -f "$HISTORY_FILE" ]; then
    echo "📊 No routing history yet. Run 'flowclaw optimize' first."
    return
  fi

  echo "📊 FlowClaw Routing History"
  echo ""

  python3 - "$HISTORY_FILE" "$num_entries" << 'PYEOF'
import json, sys
from datetime import datetime

history_file = sys.argv[1]
num = int(sys.argv[2])

entries = []
with open(history_file) as f:
    for line in f:
        line = line.strip()
        if line:
            entries.append(json.loads(line))

if not entries:
    print("  No entries.")
    sys.exit(0)

entries = entries[-num:]

# Assign symbols to providers
provider_map = {}
symbols = ["🔵", "🟢", "🟠", "🔴", "🟣", "⚪"]
sym_idx = 0

# Timeline
print("  ┌─── Routing Timeline ───────────────────────────────────────")
prev_primary = None
for e in entries:
    ts = e.get("timestamp", "?")
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        time_str = dt.strftime("%b %d %I:%M%p")
    except:
        time_str = ts[:16]

    primary = e.get("primary", "none")
    action = e.get("action", "?")

    if primary not in provider_map:
        provider_map[primary] = symbols[sym_idx % len(symbols)]
        sym_idx += 1
    sym = provider_map[primary]

    # Switchover marker
    if prev_primary and prev_primary != primary:
        print(f"  │  ⚡ SWITCH: {prev_primary}")
        print(f"  │         → {primary}")

    print(f"  │ {time_str:>14s}  {sym} {primary}")
    prev_primary = primary

print("  └──────────────────────────────────────────────────────────")
print()

# Distribution chart
print("  Provider Distribution:")
counts = {}
for e in entries:
    p = e.get("primary", "none")
    counts[p] = counts.get(p, 0) + 1
total = len(entries)
bar_width = 30

for provider, count in sorted(counts.items(), key=lambda x: -x[1]):
    pct = count / total * 100
    filled = int(pct / 100 * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    sym = provider_map.get(provider, "⚪")
    short = provider.split("/")[-1] if "/" in provider else provider
    if len(short) > 25:
        short = short[:22] + "..."
    print(f"    {sym} {short:25s} {bar} {pct:5.1f}% ({count})")

print()
print(f"  Total routing decisions: {total}")

# Switchover count
switches = 0
prev = None
for e in entries:
    p = e.get("primary", "none")
    if prev and prev != p:
        switches += 1
    prev = p
print(f"  Total switchovers: {switches}")
PYEOF
}

# ── Main ─────────────────────────────────────────────────────────────

case "${1:-help}" in
  status)   shift; cmd_status "$@" ;;
  monitor)  shift; cmd_monitor "$@" ;;
  score)    shift; cmd_score "$@" ;;
  optimize) shift; cmd_optimize "$@" ;;
  auto)     shift; cmd_auto "$@" ;;
  test)     shift; cmd_test "$@" ;;
  history)  shift; cmd_history "$@" ;;
  -h|--help|help)
    show_banner
    echo ""
    cat <<'EOF'
Usage: flowclaw <command> [options]

📊 Usage Monitoring:
  status [--fresh] [--json]        Raw usage dashboard from all providers
  monitor [--json] [--cached]      Clean usage report (no scoring/routing)

🧠 Load Balancing:
  score [--json]                   Scored ranking of all accounts
  optimize [--dry-run] [--verbose] Reorder OpenClaw routing for optimal usage
  auto                             Run optimize silently (for cron jobs)
  history [N]                      Routing history & switchover graph

🛠  Utilities:
  test                             Run scoring engine unit tests
  help                             Show this help message

Options:
  --fresh          Bypass cache, query APIs directly
  --json           Output as JSON (for piping/scripting)
  --cached         Use cached data (monitor only)
  --dry-run        Show proposed changes without applying

Examples:
  flowclaw monitor                 # Quick usage check across all providers
  flowclaw monitor --json          # Usage data as JSON for scripting
  flowclaw status --fresh          # Full provider dashboard
  flowclaw score                   # See which account FlowClaw recommends
  flowclaw optimize --dry-run      # Preview routing changes
  flowclaw optimize                # Apply optimal routing
  flowclaw history 50              # Last 50 routing decisions
EOF
    ;;
  *)
    echo "Unknown command: $1. Run 'flowclaw help' for usage."
    exit 1
    ;;
esac
