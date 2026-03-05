#!/bin/bash
# Gateway 健康守护脚本 v1.0
# 功能：检测 Gateway 状态，异常时自动恢复

GATEWAY_PORT=18789
LOG="$HOME/.openclaw/logs/guardian.log"
BACKUP_CONFIG="$HOME/.openclaw/openclaw.json.bak"
CONFIG="$HOME/.openclaw/openclaw.json"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG
}

# 检查 Gateway 是否运行
check_gateway() {
  curl -s --max-time 3 "http://127.0.0.1:$GATEWAY_PORT/health" > /dev/null 2>&1
  return $?
}

# 检查配置是否合法
check_config() {
  openclaw gateway --check-config > /dev/null 2>&1
  return $?
}

# 主逻辑
log "=== Guardian 健康检查 ==="

# 1. 检查 Gateway 是否运行
if check_gateway; then
  log "✅ Gateway 正常运行"
  exit 0
fi

log "⚠️ Gateway 未响应，开始诊断..."

# 2. 检查配置合法性
if ! openclaw doctor 2>&1 | grep -q "Config invalid"; then
  log "✅ 配置正常，尝试重启 Gateway..."
  openclaw gateway restart 2>/dev/null || openclaw gateway start 2>/dev/null
  sleep 5
  if check_gateway; then
    log "✅ Gateway 重启成功"
  else
    log "❌ Gateway 重启失败，通知主人"
    openclaw message send --channel telegram --to "7533987198" \
      --message "⚠️ 管家警报：Gateway 重启失败，请手动检查！运行 'openclaw gateway start'" 2>/dev/null
  fi
else
  log "❌ 配置无效！尝试恢复备份..."
  
  # 3. 配置损坏时，恢复备份
  if [ -f "$BACKUP_CONFIG" ]; then
    cp "$BACKUP_CONFIG" "$CONFIG"
    log "📦 已恢复备份配置"
    
    openclaw gateway start 2>/dev/null
    sleep 5
    
    if check_gateway; then
      log "✅ 使用备份配置恢复成功"
      openclaw message send --channel telegram --to "7533987198" \
        --message "⚠️ 管家警报：配置损坏已自动恢复！已使用备份配置重启 Gateway。" 2>/dev/null
    else
      log "❌ 备份配置也无法启动，通知主人"
      openclaw message send --channel telegram --to "7533987198" \
        --message "🚨 管家紧急警报：Gateway 无法启动！配置备份也失败。请手动运行：openclaw gateway start" 2>/dev/null
    fi
  else
    log "❌ 无备份配置，通知主人"
    openclaw message send --channel telegram --to "7533987198" \
      --message "🚨 管家紧急警报：Gateway 崩溃且无备份配置！请手动运行：openclaw gateway start" 2>/dev/null
  fi
fi

log "=== 检查完成 ==="
