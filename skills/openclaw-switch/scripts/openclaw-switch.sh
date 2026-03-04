# ─────────────────────────────────────────────────────────────
#  openclaw-switch.sh — OpenClaw model manager & switcher
#  Pure bash + python3 stdlib. No external deps. No network.
#  Source: https://github.com/anthropics/openclaw
# ─────────────────────────────────────────────────────────────
set -euo pipefail

CFG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
[[ -f "$CFG" ]] || { echo "❌ Config not found: $CFG"; exit 1; }

# ── Helpers (python3 one-liners reading local JSON only) ──

py() { python3 -c "$1" 2>/dev/null; }

get_primary() {
  py "
import json, pathlib
d = json.loads(pathlib.Path('$CFG').read_text())
print(d.get('agents',{}).get('defaults',{}).get('model',{}).get('primary','(not set)'))
"
}

get_fallbacks() {
  py "
import json, pathlib
d = json.loads(pathlib.Path('$CFG').read_text())
for m in d.get('agents',{}).get('defaults',{}).get('model',{}).get('fallbacks',[]):
    print(m)
"
}

list_models() {
  py "
import json, pathlib
d = json.loads(pathlib.Path('$CFG').read_text())
providers = d.get('models',{}).get('providers',{})
i = 1
for pname, pcfg in providers.items():
    for m in pcfg.get('models',[]):
        mid = f\"{pname}/{m['id']}\"
        name = m.get('name', m['id'])
        print(f\"{i}|{mid}|{name}\")
        i += 1
"
}

set_primary() {
  py "
import json, pathlib
p = pathlib.Path('$CFG')
d = json.loads(p.read_text())
d['agents']['defaults']['model']['primary'] = '$1'
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
print('OK')
"
}

get_extra() {
  py "
import json, pathlib
d = json.loads(pathlib.Path('$CFG').read_text())
defs = d.get('agents',{}).get('defaults',{})
hb = defs.get('heartbeat',{})
sub = defs.get('subagents',{})
sub_m = sub.get('model','(follows primary)')
if isinstance(sub_m, dict): sub_m = sub_m.get('primary','(follows primary)')
print(f\"heartbeat|{hb.get('every','off')}|{hb.get('model','(follows primary)')}\")
print(f\"subagent||{sub_m}\")
"
}

# ── Colors ──
G='\033[0;32m' Y='\033[1;33m' B='\033[0;34m' C='\033[0;36m'
M='\033[0;35m' D='\033[2m' BD='\033[1m' N='\033[0m'

# ── Commands ──

cmd_status() {
  local cur; cur=$(get_primary)
  echo ""
  echo -e "${BD}╔══════════════════════════════════════╗${N}"
  echo -e "${BD}║  🔀 OpenClaw Switch Status            ║${N}"
  echo -e "${BD}╚══════════════════════════════════════╝${N}"
  echo -e "  ${BD}Primary:${N} ${G}${BD}${cur}${N}"
  echo ""
  echo -e "  ${C}${BD}⛓  Fallback chain:${N}"
  echo -e "    ${G}① ${cur}${N} ${D}(primary)${N}"
  local n=2
  get_fallbacks | while IFS= read -r fb; do
    [[ -z "$fb" ]] && continue
    echo -e "    ${Y}  ↓ error/429${N}"
    echo -e "    ${B}⓪ ${fb}${N} ${D}(fallback #$n)${N}"
    n=$((n + 1))
  done
  echo ""
  get_extra | while IFS='|' read -r kind interval model; do
    [[ "$kind" == "heartbeat" ]] && echo -e "  ${M}💓 Heartbeat:${N} every ${interval} → ${model}"
    [[ "$kind" == "subagent" ]]  && echo -e "  ${M}🤖 Subagents:${N} ${model}"
  done
  echo ""
}

cmd_list() {
  local cur; cur=$(get_primary)
  echo ""
  echo -e "${BD}📋 Available models:${N}"
  list_models | while IFS='|' read -r num mid name; do
    if [[ "$mid" == "$cur" ]]; then
      echo -e "  ${G}✔ [${num}] ${name}${N}  ${D}(${mid})${N}  ← current"
    else
      echo -e "    ${B}[${num}] ${name}${N}  ${D}(${mid})${N}"
    fi
  done
  echo ""
}

cmd_switch() {
  local target_n="$1"
  local target_id
  target_id=$(list_models | awk -F'|' -v n="$target_n" '$1==n {print $2}')
  [[ -z "$target_id" ]] && { echo "❌ Invalid number. Run: openclaw-switch list"; exit 1; }
  local cur; cur=$(get_primary)
  [[ "$target_id" == "$cur" ]] && { echo "⚠️  Already using ${target_id}"; exit 0; }
  echo -e "${C}🔄 Switching to: ${BD}${target_id}${N}"
  local res; res=$(set_primary "$target_id")
  [[ "$res" != "OK" ]] && { echo "❌ Failed to update config"; exit 1; }
  if command -v openclaw &>/dev/null; then
    echo -e "${C}🔄 Restarting daemon...${N}"
    openclaw daemon restart 2>/dev/null || true
  fi
  echo -e "${G}✅ Primary model → ${BD}${target_id}${N}"
}

cmd_fallback() {
  local cur; cur=$(get_primary)
  echo ""
  echo -e "${BD}⛓  Fallback chain:${N}"
  echo -e "  ${G}${cur}${N} ${D}(primary)${N}"
  get_fallbacks | while IFS= read -r fb; do
    [[ -z "$fb" ]] && continue
    echo -e "  ${Y}↓ error${N}"
    echo -e "  ${B}${fb}${N}"
  done
  echo ""
  echo -e "${D}  On error/429, OpenClaw auto-tries the next model. No manual action needed.${N}"
  echo ""
}

# ── Main ──
case "${1:-}" in
  status)             cmd_status ;;
  list)               cmd_list ;;
  switch)  [[ -z "${2:-}" ]] && { echo "Usage: openclaw-switch switch <number>"; exit 1; }
                      cmd_switch "$2" ;;
  fallback)           cmd_fallback ;;
  *)
    echo ""
    echo -e "${BD}🔀 openclaw-switch${N} — The missing model manager for OpenClaw"
    echo ""
    echo "  status     Show current model + fallback chain"
    echo "  list       List all available models"
    echo "  switch N   Switch primary model to number N"
    echo "  fallback   Show fallback chain"
    echo ""
    ;;
esac
