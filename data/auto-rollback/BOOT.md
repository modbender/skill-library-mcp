# BOOT.md

Gateway startup checklist (auto-run by OpenClaw bundled hook `boot-md`).

## Auto-cancel pending rollback

CN: 如果检测到存在待执行的回滚计划（由 auto-rollback start 创建），且现在 Gateway 已成功启动，则自动取消该回滚计划。

EN: If a rollback plan is pending (created by `auto-rollback start`), and the Gateway is up (we are running now), automatically cancel the rollback task.

Commands:

```bash
STATE="$HOME/.openclaw/state/rollback-pending.json"
LOG="$HOME/.openclaw/logs/rollback.log"

if [ -f "$STATE" ]; then
  LABEL=$(jq -r '.launchd_label // empty' "$STATE")
  PLIST="$HOME/.openclaw/${LABEL}.plist"

  echo "[$(date -Iseconds)] 🛡️ BOOT: detected rollback state file: $STATE" >> "$LOG"

  if [ -n "$LABEL" ] && [ -f "$PLIST" ]; then
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    rm -f "$HOME/.openclaw/.rollback_execute.sh"
    echo "[$(date -Iseconds)] 🛡️ BOOT: rollback cancelled (label=$LABEL)" >> "$LOG"
  else
    echo "[$(date -Iseconds)] 🛡️ BOOT: rollback state present but plist missing (label=$LABEL)" >> "$LOG"
  fi

  rm -f "$STATE"
  echo "[$(date -Iseconds)] 🛡️ BOOT: rollback state file removed" >> "$LOG"
fi
```
