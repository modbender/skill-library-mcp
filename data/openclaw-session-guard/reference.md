# OpenClaw Session Guard 说明

## 功能总览

### 1) 会话高水位自动治理
- 扫描所有 agent 会话 token 占用
- 达到阈值（默认 80%）触发：
  - 归档摘要（`session-archives/<agent>/...md`）
  - 生成交接提示（`.handoff.txt`）
  - 将会话键切换到新 `sessionId`
  - 预注入交接提示，降低首轮 token 成本

### 2) 防抖与并发保护
- 文件锁，防止定时任务并发执行
- 每会话冷却窗口（默认 30 分钟），避免重复轮换
- 仅处理 `agent:*:main` 主会话，默认跳过 `cron/run/group`

### 3) 运维可观测
- LaunchAgent 常驻定时执行（默认每 5 分钟）
- 轮换状态映射：
  - `~/.openclaw/state/session-rotator/active-session-map.json`

## 关键目录

- 运行脚本：`~/bin/openclaw-session-rotator.sh`
- 定时任务：`~/Library/LaunchAgents/ai.openclaw.session.rotator.plist`
- 归档目录：`~/.openclaw/knowledge/session-archives/`
- 状态目录：`~/.openclaw/state/session-rotator/`

## 可调参数

通过 LaunchAgent 环境变量或手动执行时覆盖：

- `SESSION_ROTATE_THRESHOLD_PERCENT`（默认 `80`）
- `SESSION_ROTATE_COOLDOWN_SECONDS`（默认 `1800`）
- `SESSION_ROTATE_MAX_ITEMS_PER_ROLE`（默认 `6`）
- `OPENCLAW_BIN`（默认 `openclaw`）

## 注意事项

- 会话切换是“同一会话键 -> 新 sessionId”，对上游路由透明
- 若用户要求“群聊也自动切”，需显式放开 group 过滤
- 若模型上下文已非常拥堵，首次 handoff 仍可能较慢，属正常现象
