#!/bin/bash
# FlowClaw — Unified Provider Usage Dashboard
# Queries all configured LLM providers for real-time usage data:
#   - Anthropic Claude Max (via direct OAuth API — supports multiple accounts)
#   - Google Gemini CLI (via OpenClaw → cloudcode-pa.googleapis.com)
#   - Google Antigravity (via OpenClaw → codexbar usage API)
#   - OpenAI Codex (via OpenClaw → chatgpt.com/backend-api/wham/usage)
#   - GitHub Copilot (via OpenClaw → api.github.com/copilot_internal/user)
#   - Ollama (local models, always available)
#
# Anthropic uses FlowClaw's own token store for multi-account support.
# All other providers use OpenClaw's unified `openclaw status --usage --json`.

set -euo pipefail

FORMAT="text"
FORCE_REFRESH=0
TOKEN_DIR="${TOKEN_DIR:-$HOME/.openclaw/usage-tokens}"
CACHE_FILE="/tmp/provider-usage-cache"
CACHE_TTL=60

while [[ $# -gt 0 ]]; do
  case $1 in
    --json) FORMAT="json"; shift ;;
    --fresh|--force) FORCE_REFRESH=1; shift ;;
    --cache-ttl) CACHE_TTL="$2"; shift 2 ;;
    -h|--help)
      cat <<'EOF'
Usage: provider-usage.sh [OPTIONS]

Unified usage dashboard for all LLM providers.

Options:
  --fresh, --force       Force refresh (ignore cache)
  --json                 JSON output
  --cache-ttl SEC        Cache TTL (default: 60)
  -h, --help             Show this help
EOF
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Check cache
if [ "$FORCE_REFRESH" -eq 0 ] && [ -f "$CACHE_FILE" ]; then
  if [[ "$OSTYPE" == "darwin"* ]]; then
    age=$(($(date +%s) - $(stat -f%m "$CACHE_FILE")))
  else
    age=$(($(date +%s) - $(stat -c%Y "$CACHE_FILE")))
  fi
  if [ "$age" -lt "$CACHE_TTL" ]; then
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# ── Helpers ──────────────────────────────────────────────────────────

secs_to_human() {
  local secs=$1
  if [ "$secs" -lt 0 ]; then secs=0; fi
  local days=$((secs / 86400))
  local hours=$(((secs % 86400) / 3600))
  local mins=$(((secs % 3600) / 60))
  if [ "$days" -gt 0 ]; then echo "${days}d ${hours}h"
  elif [ "$hours" -gt 0 ]; then echo "${hours}h ${mins}m"
  else echo "${mins}m"
  fi
}

bar() {
  local pct=${1%.*}
  local filled=$((pct / 10))
  local empty=$((10 - filled))
  local b=""
  for ((i=0; i<filled; i++)); do b+="█"; done
  for ((i=0; i<empty; i++)); do b+="░"; done
  echo "$b"
}

dot() {
  local pct=${1%.*}
  if [ "$pct" -ge 80 ]; then echo "🔴"
  elif [ "$pct" -ge 50 ]; then echo "🟡"
  else echo "🟢"
  fi
}

NOW=$(date +%s)
JSON_SECTIONS=""
TEXT_OUTPUT=""

# ── Anthropic Claude Max ─────────────────────────────────────────────
# Uses FlowClaw's own token store for multi-account support

if [ -d "$TOKEN_DIR" ]; then
  ACCT_FILES=$(ls "$TOKEN_DIR"/account-*.json 2>/dev/null || echo "")
  if [ -n "$ACCT_FILES" ]; then
    TEXT_OUTPUT+="━━━ Anthropic Claude Max ━━━━━━━━━━━━━━━━━━━━\n\n"

    for TOKEN_FILE in $ACCT_FILES; do
      LABEL=$(python3 -c "import json; d=json.load(open('$TOKEN_FILE')); print(d.get('label','?'))")
      EMAIL=$(python3 -c "import json; d=json.load(open('$TOKEN_FILE')); print(d.get('email','?'))")
      TOKEN=$(python3 -c "import json; d=json.load(open('$TOKEN_FILE')); print(d.get('accessToken',''))")

      if [ -z "$TOKEN" ]; then
        TEXT_OUTPUT+="  ⚠️  $LABEL: No token\n\n"
        continue
      fi

      RESP=$(curl -s --max-time 10 "https://api.anthropic.com/api/oauth/usage" \
        -H "Authorization: Bearer $TOKEN" \
        -H "anthropic-beta: oauth-2025-04-20" 2>/dev/null || echo "")

      if echo "$RESP" | grep -q '"error"' 2>/dev/null; then
        ERROR_MSG=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['error']['message'])" 2>/dev/null || echo "API error")
        TEXT_OUTPUT+="  ⚠️  $LABEL ($EMAIL): $ERROR_MSG\n\n"
        JSON_SECTIONS+="${JSON_SECTIONS:+,}{\"provider\":\"anthropic\",\"account\":\"$LABEL\",\"email\":\"$EMAIL\",\"error\":\"$ERROR_MSG\"}"
        continue
      fi

      PARSED=$(python3 << PYEOF
import json
d = json.loads('''$RESP''')
fh = d.get('five_hour') or {}
sd = d.get('seven_day') or {}
sn = d.get('seven_day_sonnet') or {}
op = d.get('seven_day_opus') or {}
ex = d.get('extra_usage') or {}
print(fh.get('utilization', 0))
print(fh.get('resets_at', ''))
print(sd.get('utilization', 0))
print(sd.get('resets_at', ''))
print(sn.get('utilization', 0))
print(sn.get('resets_at', ''))
print(op.get('utilization', 0))
print(op.get('resets_at', ''))
print(ex.get('is_enabled', False))
print(ex.get('utilization', 0))
print(ex.get('used_credits', 0))
print(ex.get('monthly_limit', 0))
PYEOF
      )

      SESSION_PCT=$(echo "$PARSED" | sed -n '1p')
      SESSION_RESET=$(echo "$PARSED" | sed -n '2p')
      WEEKLY_PCT=$(echo "$PARSED" | sed -n '3p')
      WEEKLY_RESET=$(echo "$PARSED" | sed -n '4p')
      SONNET_PCT=$(echo "$PARSED" | sed -n '5p')
      OPUS_PCT=$(echo "$PARSED" | sed -n '7p')
      EXTRA_ENABLED=$(echo "$PARSED" | sed -n '9p')
      EXTRA_PCT=$(echo "$PARSED" | sed -n '10p')
      EXTRA_USED=$(echo "$PARSED" | sed -n '11p')
      EXTRA_LIMIT=$(echo "$PARSED" | sed -n '12p')

      parse_reset() {
        local reset_ts="$1"
        if [ -z "$reset_ts" ] || [ "$reset_ts" = "None" ] || [ "$reset_ts" = "" ]; then
          echo "—"
          return
        fi
        local clean=$(echo "$reset_ts" | sed 's/\.[0-9]*+.*//;s/\.[0-9]*Z//')
        local epoch=0
        if [[ "$OSTYPE" == "darwin"* ]]; then
          epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$clean" +%s 2>/dev/null || echo 0)
        else
          epoch=$(date -d "$reset_ts" +%s 2>/dev/null || echo 0)
        fi
        if [ "$epoch" -gt 0 ]; then
          secs_to_human $((epoch - NOW))
        else
          echo "—"
        fi
      }

      S_LEFT=$(parse_reset "$SESSION_RESET")
      W_LEFT=$(parse_reset "$WEEKLY_RESET")

      SI=${SESSION_PCT%.*}; WI=${WEEKLY_PCT%.*}; SNI=${SONNET_PCT%.*}; OPI=${OPUS_PCT%.*}; EI=${EXTRA_PCT%.*}

      TIER_LABEL=$(python3 -c "import json; d=json.load(open('$TOKEN_FILE')); print(d.get('rateLimitTier', d.get('subscriptionType', 'Max')))" 2>/dev/null || echo "Max")
      TEXT_OUTPUT+="  👤 $LABEL ($EMAIL) — $TIER_LABEL\n"
      TEXT_OUTPUT+="     ⏱️  5h Session:  $(dot $SI) $(bar $SI) ${SI}%  ⏳${S_LEFT}\n"
      TEXT_OUTPUT+="     📅 7d Overall:   $(dot $WI) $(bar $WI) ${WI}%  ⏳${W_LEFT}\n"
      TEXT_OUTPUT+="     💎 7d Opus:      $(dot $OPI) $(bar $OPI) ${OPI}%\n"
      TEXT_OUTPUT+="     💬 7d Sonnet:    $(dot $SNI) $(bar $SNI) ${SNI}%\n"
      if [ "$EXTRA_ENABLED" = "True" ]; then
        EXTRA_USED_FMT=$(python3 -c "print(f'{${EXTRA_USED}/100:.2f}')")
        EXTRA_LIMIT_FMT=$(python3 -c "print(f'{${EXTRA_LIMIT}/100:.2f}')")
        TEXT_OUTPUT+="     💰 Extra usage:  $(dot $EI) \$${EXTRA_USED_FMT}/\$${EXTRA_LIMIT_FMT}\n"
      fi
      TEXT_OUTPUT+="\n"

      JSON_SECTIONS+="${JSON_SECTIONS:+,}{\"provider\":\"anthropic\",\"account\":\"$LABEL\",\"email\":\"$EMAIL\",\"session\":{\"utilization\":$SESSION_PCT,\"resets_in\":\"$S_LEFT\"},\"weekly\":{\"utilization\":$WEEKLY_PCT,\"resets_in\":\"$W_LEFT\"},\"opus\":{\"utilization\":$OPUS_PCT},\"sonnet\":{\"utilization\":$SONNET_PCT},\"extra\":{\"enabled\":$( [ "$EXTRA_ENABLED" = "True" ] && echo true || echo false ),\"utilization\":$EXTRA_PCT,\"used\":$EXTRA_USED,\"limit\":$EXTRA_LIMIT}}"
    done
  fi
fi

# ── All Other Providers (via OpenClaw) ────────────────────────────────
# Uses `openclaw status --usage --json` which queries source APIs:
#   - Google Gemini CLI → cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota
#   - Google Antigravity → codexbar usage API
#   - OpenAI Codex → chatgpt.com/backend-api/wham/usage
#   - GitHub Copilot → api.github.com/copilot_internal/user

if command -v openclaw >/dev/null 2>&1; then
  OPENCLAW_TMP=$(mktemp /tmp/flowclaw-oc-XXXXXX.json)
  openclaw status --usage --json > "$OPENCLAW_TMP" 2>/dev/null || echo "{}" > "$OPENCLAW_TMP"

  if python3 -c "import json; json.load(open('$OPENCLAW_TMP'))" 2>/dev/null; then
    PROVIDER_OUTPUT=$(python3 << PYEOF
import json, time

data = json.load(open("$OPENCLAW_TMP"))
usage = data.get("usage", data)
providers = usage.get("providers", [])
now = $NOW

sections = []
json_parts = []

# Provider display config
PROVIDER_CONFIG = {
    "google-gemini-cli": {"header": "Google Gemini CLI", "icon": "♊"},
    "google-antigravity": {"header": "Google Antigravity", "icon": "🌐"},
    "openai-codex": {"header": "OpenAI Codex", "icon": "🤖"},
    "github-copilot": {"header": "GitHub Copilot", "icon": "🐙"},
}

def secs_human(secs):
    if secs <= 0: return "—"
    days = secs // 86400
    hours = (secs % 86400) // 3600
    mins = (secs % 3600) // 60
    if days > 0: return f"{days}d {hours}h"
    if hours > 0: return f"{hours}h {mins}m"
    return f"{mins}m"

def bar(pct):
    pct = int(pct)
    filled = pct // 10
    empty = 10 - filled
    return "█" * filled + "░" * empty

def dot(pct):
    pct = int(pct)
    if pct >= 80: return "🔴"
    if pct >= 50: return "🟡"
    return "🟢"

for prov in providers:
    pid = prov.get("provider", "")
    if pid == "anthropic":
        continue  # handled by FlowClaw's own token store
    if pid not in PROVIDER_CONFIG:
        continue

    config = PROVIDER_CONFIG[pid]
    windows = prov.get("windows", [])
    error = prov.get("error")
    plan = prov.get("plan", "")

    header = f"━━━ {config['header']} ━━━━━━━━━━━━━━━━━━━━━━━"
    lines = [header, ""]

    if error:
        lines.append(f"  ⚠️  {error}")
        lines.append("")
        json_parts.append(f'{{"provider":"{pid}","error":"{error}"}}')
    elif not windows:
        lines.append(f"  {config['icon']} No usage data available")
        lines.append("")
        json_parts.append(f'{{"provider":"{pid}","windows":[]}}')
    else:
        # Group windows by model family for cleaner display
        json_windows = []
        for w in windows:
            label = w.get("label", "?")
            used = w.get("usedPercent", 0)
            reset_at = w.get("resetAt")
            used_int = int(used)

            reset_str = ""
            if reset_at:
                remaining = int(reset_at / 1000) - now
                if remaining > 0:
                    reset_str = f"  ⏳{secs_human(remaining)}"

            icon = config["icon"]
            if "flash" in label.lower():
                icon = "⚡"
            elif "pro" in label.lower() or "gemini" in label.lower():
                icon = "♊"
            elif "claude" in label.lower():
                icon = "🤖"
            elif "premium" in label.lower():
                icon = "💎"
            elif "chat" in label.lower():
                icon = "💬"

            lines.append(f"     {icon} {label:18s} {dot(used_int)} {bar(used_int)} {used_int}%{reset_str}")
            json_windows.append(f'{{"label":"{label}","used_pct":{used_int}}}')

        plan_str = f" ({plan})" if plan else ""
        lines.insert(2, f"  {config['icon']}{plan_str}")
        lines.append("")
        json_parts.append(f'{{"provider":"{pid}","plan":"{plan}","windows":[{",".join(json_windows)}]}}')

    for line in lines:
        print(f"TEXT:{line}")

for j in json_parts:
    print(f"JSON:{j}")
PYEOF
    )

    # Parse the output
    while IFS= read -r line; do
      if [[ "$line" == TEXT:* ]]; then
        TEXT_OUTPUT+="${line#TEXT:}\n"
      elif [[ "$line" == JSON:* ]]; then
        JSON_SECTIONS+="${JSON_SECTIONS:+,}${line#JSON:}"
      fi
    done <<< "$PROVIDER_OUTPUT"
  fi
  rm -f "$OPENCLAW_TMP"
fi

# ── Ollama (Local Models) ────────────────────────────────────────────

if command -v ollama >/dev/null 2>&1; then
  OLLAMA_RUNNING=$(curl -s --max-time 2 http://localhost:11434/api/tags 2>/dev/null || echo "")
  if [ -n "$OLLAMA_RUNNING" ] && echo "$OLLAMA_RUNNING" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    OLLAMA_MODELS=$(echo "$OLLAMA_RUNNING" | python3 -c "
import json, sys
d = json.load(sys.stdin)
models = d.get('models', [])
for m in models:
    name = m.get('name', '?')
    size_gb = m.get('size', 0) / (1024**3)
    print(f'{name}|{size_gb:.1f}GB')
")
    if [ -n "$OLLAMA_MODELS" ]; then
      TEXT_OUTPUT+="━━━ Ollama (Local) ━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
      while IFS='|' read -r OL_NAME OL_SIZE; do
        TEXT_OUTPUT+="  🖥️  $OL_NAME ($OL_SIZE)  🟢 Always available\n"
        JSON_SECTIONS+="${JSON_SECTIONS:+,}{\"provider\":\"ollama\",\"model\":\"$OL_NAME\",\"size\":\"$OL_SIZE\",\"available\":true}"
      done <<< "$OLLAMA_MODELS"
      TEXT_OUTPUT+="\n"
    fi
  fi
fi

# ── Output ───────────────────────────────────────────────────────────

if [ -z "$TEXT_OUTPUT" ]; then
  TEXT_OUTPUT="❌ No providers configured.\n"
  TEXT_OUTPUT+="   Run 'flowclaw setup' to add your first provider.\n"
fi

if [ "$FORMAT" = "json" ]; then
  OUTPUT="{\"providers\":[$JSON_SECTIONS],\"checked_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
else
  OUTPUT="🦞 FlowClaw — LLM Provider Dashboard\n\n${TEXT_OUTPUT}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📍 $(date '+%I:%M %p %Z') · $(date '+%b %d, %Y')"
fi

echo -e "$OUTPUT" > "$CACHE_FILE"
echo -e "$OUTPUT"
