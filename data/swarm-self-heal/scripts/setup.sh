#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_SCRIPTS_DIR="$HOME/.openclaw/workspace-studio/scripts"
mkdir -p "$WS_SCRIPTS_DIR"

cp -f "$SKILL_DIR/swarm_self_heal.sh" "$WS_SCRIPTS_DIR/swarm_self_heal.sh"
cp -f "$SKILL_DIR/anvil_watchdog.sh" "$WS_SCRIPTS_DIR/anvil_watchdog.sh"
chmod +x "$WS_SCRIPTS_DIR/swarm_self_heal.sh" "$WS_SCRIPTS_DIR/anvil_watchdog.sh"

target_to="$(jq -r '.channels.telegram.defaultTo // empty' "$HOME/.openclaw/openclaw.json" 2>/dev/null || true)"
if [[ -z "$target_to" ]]; then
  target_to="8563003761"
fi

watchdog_message=$'Run ~/.openclaw/workspace-studio/scripts/anvil_watchdog.sh.\nIf VERDICT=healthy and actions=none, respond with one line: "swarm-self-heal healthy <receipt>".\nIf VERDICT!=healthy or actions!=none, include full raw output block and a concise remediation summary (failed agents, actions taken, next operator step).'

primary_id="$(jq -r '.jobs[] | select(.name=="Anvil stuck watchdog") | .id' "$HOME/.openclaw/cron/jobs.json" 2>/dev/null | head -n1 || true)"
if [[ -n "$primary_id" ]]; then
  openclaw cron edit "$primary_id" \
    --agent designer \
    --every 20m \
    --session isolated \
    --wake now \
    --thinking xhigh \
    --timeout-seconds 900 \
    --message "$watchdog_message" \
    --announce \
    --channel telegram \
    --to "$target_to" \
    --best-effort-deliver >/dev/null
else
  openclaw cron add \
    --agent designer \
    --name "Anvil stuck watchdog" \
    --every 20m \
    --session isolated \
    --wake now \
    --thinking xhigh \
    --timeout-seconds 900 \
    --message "$watchdog_message" \
    --announce \
    --channel telegram \
    --to "$target_to" \
    --best-effort-deliver >/dev/null
fi

backup_id="$(jq -r '.jobs[] | select(.name=="Swarm self-heal backup") | .id' "$HOME/.openclaw/cron/jobs.json" 2>/dev/null | head -n1 || true)"
if [[ -n "$backup_id" ]]; then
  openclaw cron edit "$backup_id" \
    --agent reviewer \
    --every 30m \
    --session isolated \
    --wake now \
    --thinking xhigh \
    --timeout-seconds 900 \
    --message "$watchdog_message" \
    --announce \
    --channel telegram \
    --to "$target_to" \
    --best-effort-deliver >/dev/null
else
  openclaw cron add \
    --agent reviewer \
    --name "Swarm self-heal backup" \
    --every 30m \
    --session isolated \
    --wake now \
    --thinking xhigh \
    --timeout-seconds 900 \
    --message "$watchdog_message" \
    --announce \
    --channel telegram \
    --to "$target_to" \
    --best-effort-deliver >/dev/null
fi

echo "installed_watchdog_scripts=$WS_SCRIPTS_DIR"
echo "telegram_target=$target_to"
echo "primary_watchdog=Anvil stuck watchdog"
echo "backup_watchdog=Swarm self-heal backup"
