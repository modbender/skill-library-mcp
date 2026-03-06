# Cron 任务配置 — 角色扮演系统

## 任务总览

| 任务 | 时间 | 说明 |
|------|------|------|
| 每日角色生成 | 06:00 | 读取 ENGINE.md 执行 Step 0-8 |
| 每日收尾归档 | 23:30 | 执行 WRAPUP.md 归档流程 |

---

## OpenClaw Cron（推荐）

### 每日 6:00 — 角色生成

```bash
openclaw cron add \
  --agent role-play \
  --name "每日角色生成" \
  --cron "0 6 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --delivery none \
  --model opus \
  --message "读取 ENGINE.md 并按步骤执行每日初始化（Step 0-8）"
```

> `--delivery none`：agent 自行通过 message tool 发送早安消息，无需 cron 发摘要。
> `--model opus`：初始化逻辑复杂（多步推理 + 内容生成），建议使用高能力模型。

### 每日 23:30 — 收尾归档

```bash
openclaw cron add \
  --agent role-play \
  --name "每日收尾归档" \
  --cron "30 23 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --delivery none \
  --message "读取 docs/WRAPUP.md 按步骤执行收尾归档，完成后回复 WRAPUP_OK"
```

> `--delivery none`：收尾归档为内部操作，无需发送执行摘要。

### 管理命令

```bash
openclaw cron list              # 查看所有任务
openclaw cron run <job-id>      # 手动触发
openclaw cron runs --id <id>    # 查看执行历史
openclaw cron remove <job-id>   # 删除任务
```

---

## 系统 Crontab（备选）

如不使用 OpenClaw cron，也可用系统 crontab 直接调用收尾脚本：

```bash
30 23 * * * <workspace-path>/scripts/wrapup.sh >> /tmp/roleplay-wrapup.log 2>&1
```

将 `<workspace-path>` 替换为实际 workspace 路径（如 `~/.openclaw/workspace-role-play`）。

**注意**：系统 crontab 只能执行 shell 脚本（收尾归档），无法触发 agent 执行初始化。每日 6:00 初始化必须通过 OpenClaw cron 或心跳手动触发。

---

## 前置条件

- 脚本已可执行：`chmod +x <workspace-path>/scripts/wrapup.sh`
- 目录权限正常
- OpenClaw Gateway 运行中（使用 OpenClaw cron 时）
