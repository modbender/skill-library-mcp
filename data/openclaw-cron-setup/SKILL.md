---
name: cron-setup
description: OpenClaw Gateway 内置定时任务调度器。用于创建一次性提醒、周期性任务、后台自动化。支持主会话系统事件和独立会话执行，可配置投递到聊天频道或 Webhook。
---

# OpenClaw Cron Jobs 配置指南

Cron 是 Gateway 内置的调度器，持久化存储任务，在指定时间唤醒 agent 执行，并可选择将结果投递到聊天频道。

## 核心概念

### 两种执行模式

| 模式 | 用途 | payload 类型 |
|------|------|--------------|
| **main** (主会话) | 系统事件，融入正常心跳流程 | `systemEvent` |
| **isolated** (独立会话) | 后台任务，不污染主会话历史 | `agentTurn` |

### 三种调度类型

| 类型 | 字段 | 示例 |
|------|------|------|
| **一次性** | `schedule.kind: "at"` | `2026-03-04T10:00:00Z` 或 `20m` (相对时间) |
| **固定间隔** | `schedule.kind: "every"` | `everyMs: 3600000` (1 小时) |
| **Cron 表达式** | `schedule.kind: "cron"` | `expr: "0 7 * * *"` (每天 7 点) |

## 快速开始

### 1. 创建一次性提醒（主会话）

```bash
openclaw cron add \
  --name "提醒事项" \
  --at "20m" \
  --session main \
  --system-event "20 分钟后检查日历" \
  --wake now \
  --delete-after-run
```

### 2. 创建周期性任务（独立会话）

```bash
openclaw cron add \
  --name "晨间简报" \
  --cron "0 7 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "总结昨晚的邮件和日历事件" \
  --announce \
  --channel telegram \
  --to "+8613800138000"
```

### 3. 创建带模型覆盖的深度任务

```bash
openclaw cron add \
  --name "周报分析" \
  --cron "0 9 * * 1" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "分析本周项目进展" \
  --model "opus" \
  --thinking high \
  --announce \
  --channel whatsapp \
  --to "+8613800138000"
```

## 常用命令

```bash
# 查看任务列表
openclaw cron list

# 手动运行任务
openclaw cron run <job-id>

# 查看运行历史
openclaw cron runs --id <job-id> --limit 10

# 编辑任务
openclaw cron edit <job-id> --message "新提示词"

# 删除任务
openclaw cron remove <job-id>
```

## JSON Schema（工具调用）

### 一次性主会话任务

```json
{
  "name": "提醒",
  "schedule": { "kind": "at", "at": "2026-03-04T10:00:00Z" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": { "kind": "systemEvent", "text": "提醒内容" },
  "deleteAfterRun": true
}
```

### 周期性独立会话任务

```json
{
  "name": "晨间简报",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Shanghai" },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": { "kind": "agentTurn", "message": "总结隔夜更新" },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "+8613800138000",
    "bestEffort": true
  }
}
```

## 投递模式（Delivery）

仅适用于 `isolated` 任务：

| 模式 | 说明 |
|------|------|
| `announce` | 投递到指定频道，并在主会话发送简短摘要 |
| `webhook` | POST 到 HTTP 端点 |
| `none` | 仅内部执行，无投递 |

**省略 `delivery` 时默认行为：** `announce` 模式

## Telegram 话题投递

支持论坛话题（topic）：

```bash
--to "-1001234567890:topic:123"  # 推荐：显式话题标记
--to "-1001234567890:123"         # 简写：数字后缀
```

## 配置示例（参考）

当前工作配置示例（`~/.openclaw/cron/jobs.json`）：

```json
{
  "name": "daily-health-summary",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "从 Bitable 查询健康数据并生成总结"
  },
  "delivery": {
    "mode": "none",
    "channel": "last"
  }
}
```

## 故障排查

### 任务不执行

1. 检查 cron 是否启用：`cron.enabled: true`（配置中）
2. 检查 Gateway 是否持续运行（cron 在 Gateway 进程内执行）
3. 确认时区设置正确（`--tz` 参数）

### 任务反复延迟

- 连续失败会触发指数退避：30s → 1m → 5m → 15m → 60m
- 成功执行后退避重置

### 查看存储位置

- 任务存储：`~/.openclaw/cron/jobs.json`
- 运行历史：`~/.openclaw/cron/runs/<jobId>.jsonl`

## 高级配置

在 `~/.openclaw/config.json` 中：

```json5
{
  cron: {
    enabled: true,
    sessionRetention: "24h",      // 独立会话保留时长
    runLog: {
      maxBytes: "2mb",            // 运行日志最大大小
      keepLines: 2000,            // 保留行数
    },
  }
}
```

## Cron vs Heartbeat

| 场景 | 推荐 |
|------|------|
| 精确时间（如"每周一 9 点"） | **cron** |
| 批量检查（邮箱 + 日历 + 天气） | **heartbeat** |
| 一次性提醒 | **cron** |
| 后台自动化（频繁/嘈杂） | **cron (isolated)** |
| 主会话上下文相关任务 | **heartbeat** |

---

**文档来源：** https://docs.openclaw.ai/automation/cron-jobs
