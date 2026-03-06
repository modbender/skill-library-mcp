---
name: feishu-multi-agent
description: Production blueprint for orchestrating multiple OpenClaw agents via Feishu with file-driven task queues, cron scheduling, and workspace sandbox workarounds.
---

# feishu-multi-agent — 飞书多 Agent 编排实战指南

> 从 0 到 1 搭建一个包工头 + N 个下属 agent 的自动化团队，通过飞书与用户交互，文件驱动任务分发，cron 驱动持续工作。

本技能总结了在生产环境中运行 7 个飞书 agent（包工头 + 游戏工厂 + 龙虾出版社 + 小秘虾妹 + 炒币哥 + 炒股姐 + Agent猎头）的全部经验，涵盖架构设计、沙箱踩坑、任务队列、cron 编排、故障排查。

## 适用场景

- 用 OpenClaw 管理多个 AI agent，每个 agent 绑定一个飞书 bot
- 需要一个"包工头"agent 自动给其他 agent 派活
- 希望 agent 持续工作（不是做一件事就停）
- 需要文件驱动的任务队列（而非纯消息驱动）

## 架构总览

```
用户 ──飞书──→ 包工头(main) ──任务文件──→ buyer / kb / gf
                  │                         ↑
                  │                    cron 触发心跳
                  └── cron 巡查 ──检查状态──┘

不受包工头管理的 agent（用户直接控制）:
  coach / travel / edu
```

### 核心概念

| 概念 | 说明 |
|------|------|
| 包工头 | 只管人不干活，通过文件派活 + `openclaw agent` 催活 |
| 任务队列 | 每个下属 workspace 下 `tasks/pending/` + `tasks/done/` |
| 持续工作 | cron 高频触发 + HEARTBEAT.md 指示"做完一件做下一件" |
| 沙箱限制 | Write 工具只能写 workspace 内，跨 workspace 必须用 bash |

---

## Step 1: 飞书应用准备

每个 agent 需要一个独立的飞书自建应用（bot）。参考 `feishu-app-setup` 技能完成：

1. 在 [open.feishu.cn](https://open.feishu.cn) 创建 N 个企业自建应用
2. 每个应用添加机器人能力 + 批量导入权限
3. 配置事件订阅（WebSocket 长连接）
4. 发布上线

**批量创建技巧**：用 `agent-browser --cdp-endpoint` 连接已登录浏览器，循环创建+配置，免重复登录。

## Step 2: OpenClaw 多账号配置

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "accounts": {
        "main":   { "appId": "cli_aaa", "appSecret": "secret_aaa", "name": "包工头" },
        "buyer":  { "appId": "cli_bbb", "appSecret": "secret_bbb", "name": "游戏工厂" },
        "kb":     { "appId": "cli_ccc", "appSecret": "secret_ccc", "name": "龙虾出版社" },
        "gf":     { "appId": "cli_ddd", "appSecret": "secret_ddd", "name": "小秘虾妹" }
      }
    }
  },
  "bindings": [
    { "agentId": "main",  "match": { "channel": "feishu", "accountId": "main" } },
    { "agentId": "buyer", "match": { "channel": "feishu", "accountId": "buyer" } },
    { "agentId": "kb",    "match": { "channel": "feishu", "accountId": "kb" } },
    { "agentId": "gf",    "match": { "channel": "feishu", "accountId": "gf" } }
  ]
}
```

### Agent 列表配置

```json
{
  "agents": {
    "list": [
      { "id": "main",  "name": "main",  "workspace": "~/.openclaw/workspace" },
      { "id": "buyer", "name": "buyer", "workspace": "~/.openclaw/workspace-buyer" },
      { "id": "kb",    "name": "kb",    "workspace": "~/.openclaw/workspace-kb" },
      { "id": "gf",    "name": "gf",    "workspace": "~/.openclaw/workspace-gf" }
    ]
  }
}
```

配置后重启 Gateway：
```bash
launchctl stop ai.openclaw.gateway && sleep 3 && launchctl start ai.openclaw.gateway
```

首次对话需配对：
```bash
openclaw pairing approve feishu <配对码>
```

## Step 3: 创建任务队列目录

```bash
# 为每个受管 agent 创建任务目录
mkdir -p ~/.openclaw/workspace-buyer/tasks/{pending,done}
mkdir -p ~/.openclaw/workspace-kb/tasks/{pending,done}
mkdir -p ~/.openclaw/workspace-gf/tasks/{pending,done}
```

### 任务文件格式

`tasks/pending/001-task-name.md`：

```markdown
# 任务标题
优先级: 高/中/低
下达时间: 2026-03-01 10:00
描述: 具体要做什么
```

完成后 agent 把文件从 `pending/` 移到 `done/`。

## Step 4: 配置包工头 SOUL.md

**文件**: `~/.openclaw/workspace/SOUL.md`

关键内容：

```markdown
# 包工头（监工/调度中心）

## 管辖范围
| Agent | 角色 |
|-------|------|
| buyer | 持续开发 HTML5 教育游戏 |
| kb    | 深度研究 + 写书 |
| gf    | 陪聊互动 + 内容推荐 |

不归你管的 agent：coach、travel、edu

## 巡查方式
- `openclaw sessions --agent <id> --active 60` 检查活动
- `ls ~/.openclaw/workspace-<id>/tasks/pending/` 检查任务队列

## ⚠️ 派活方式（重要）
必须用 bash 命令写任务文件，不要用 Write 工具！

    cat > ~/.openclaw/workspace-buyer/tasks/pending/003-xxx.md << 'EOF'
    # 任务标题
    优先级: 中
    描述: ...
    EOF

## 踢屁股
openclaw agent --agent <id> --message '检查 tasks/pending，有活就干'
```

## Step 5: 配置下属 HEARTBEAT.md

### 游戏工厂（buyer）

```markdown
# 工作循环
1. 检查 tasks/pending/，有任务就做第一个（按文件名排序）
2. 执行任务（cd game-factory && git pull → 开发 → commit && push）
3. 完成后移到 tasks/done/
4. 再检查 pending，有就继续
5. 没有待办时自主开发新游戏
6. 不要停，保持持续产出
```

### 龙虾出版社（kb）

```markdown
# 工作循环
1. 检查 tasks/pending/，有任务就执行
2. 新话题 → 生成大纲 → 逐章写作
3. 催进度 → 继续上次未完成的章节
4. 完成后移到 tasks/done/
5. 有进行中的项目就主动往前写
```

### 小秘虾妹（gf）

```markdown
# Heartbeat
## 先检查待办
查看 tasks/pending/，有任务优先做，完成后移到 tasks/done/

## 无待办时随机做一件事
1. 分享一首歌
2. 推荐有趣的东西
3. 分享趣闻
4. 发一张自拍
5. 随便聊聊
```

## Step 6: 配置 Cron Jobs

### 包工头巡查（每 30 分钟）

```bash
openclaw cron add \
  --name "foreman-patrol" \
  --every 30m \
  --agent main \
  --session main \
  --timeout-seconds 300 \
  --thinking low \
  --system-event "执行巡查。检查 buyer/kb/gf 状态和任务队列，为空闲的下属派新任务。"
```

**注意**：`--session main` 的 job 必须用 `--system-event`，不能用 `--message`！

### 包工头汇报（每 4 小时）

```bash
openclaw cron add \
  --name "foreman-report" \
  --every 4h \
  --agent main \
  --session main \
  --timeout-seconds 300 \
  --thinking low \
  --system-event "向老板汇报。统计 buyer/kb/gf 过去 4 小时的产出和状态。"
```

### 游戏工厂持续开发（每 20 分钟）

```bash
openclaw cron add \
  --name "game-factory-cycle" \
  --every 20m \
  --agent buyer \
  --session isolated \
  --timeout-seconds 600 \
  --thinking low \
  --message "检查 tasks/pending/ 有任务就做，没有就自主开发新游戏。做完继续做下一个。"
```

### 小秘虾妹互动（每 2 小时）

```bash
openclaw cron add \
  --name "gf-heartbeat" \
  --every 2h \
  --agent gf \
  --session isolated \
  --timeout-seconds 180 \
  --thinking low \
  --message "检查 tasks/pending/ 有任务先做。没有的话随机做一件事分享给用户。"
```

### Cron 管理

```bash
openclaw cron list                    # 查看所有 cron
openclaw cron run <job-id>            # 手动触发一次
openclaw cron update <id> --disabled  # 暂停
openclaw cron delete <id>             # 删除
```

---

## ⚠️ 关键踩坑与解决方案

### 坑 1: Write 工具受 workspace 沙箱限制

**症状**: `[tools] write failed: Path escapes workspace root: /path/outside/workspace`

**原因**: OpenClaw 的 Write/Read 工具使用 `fs.realpath()` 解析路径，严格限制在 workspace 目录内。Symlink 也无效（会被 realpath 解析为真实路径）。

**解决方案**:

| 场景 | 解决方案 |
|------|---------|
| Agent 需要写 workspace 外的目录 | 把目录移进 workspace，原位置留 symlink |
| 包工头写其他 agent 的 workspace | 用 bash `cat > file` 而非 Write 工具 |
| Agent 需要读其他 workspace | 用 bash `cat file` 或 `ls dir` |

**示例**：buyer 需要写 `~/game-factory/`：
```bash
mv ~/game-factory ~/.openclaw/workspace-buyer/game-factory
ln -s ~/.openclaw/workspace-buyer/game-factory ~/game-factory
```

### 坑 2: `--session main` 必须用 `--system-event`

**症状**: `Error: Main jobs require --system-event (systemEvent).`

**原因**: main session 的 cron job 只接受 `--system-event`，不接受 `--message`。`--message` 仅用于 `--session isolated`。

**对比**:
```bash
# ✅ main session
openclaw cron add --session main --system-event "巡查指令"

# ✅ isolated session
openclaw cron add --session isolated --message "工作指令"

# ❌ 错误
openclaw cron add --session main --message "xxx"
```

### 坑 3: 飞书 WebSocket 静默断连

**症状**: Agent 不再收到飞书消息，但 gateway 进程仍在运行。日志中最后一条飞书消息后无新消息。

**诊断**:
```bash
# 查看最近的飞书消息
grep "feishu\[main\]" ~/.openclaw/logs/gateway.log | tail -5

# 如果最后一条 received 时间很久以前，WebSocket 可能断了
```

**解决**: 重启 gateway 重新连接：
```bash
launchctl stop ai.openclaw.gateway && sleep 3 && launchctl start ai.openclaw.gateway
```

**验证**:
```bash
grep "WebSocket client started" ~/.openclaw/logs/gateway.log | tail -10
```

### 坑 4: 飞书消息发太快导致 replies=0

**症状**: dispatch complete 显示 `queuedFinal=false, replies=0`，部分消息无回复。

**原因**: 用户在 5 秒内连续发多条消息，后面的消息被跳过（`skipping duplicate message`）或模型来不及处理。

**缓解**: 发消息后等几秒再发下一条。这是飞书 WebSocket SDK 的去重机制。

### 坑 5: Cron job 触发时 session 正忙

**症状**: `openclaw cron run` 返回 `"ran": false, "reason": "already-running"`

**原因**: 目标 session 正在处理其他请求，cron job 排队等待。

**这是正常行为**，job 会在 session 空闲后自动执行。不需要重试。

### 坑 6: Agent 上下文溢出

**症状**: Agent 回复质量下降或不回复。`openclaw sessions` 显示 context 使用率 > 70%。

**诊断**:
```bash
openclaw sessions --agent main
# 看 Tokens (ctx %) 列
```

**解决**: 让 agent 开新 session。对于 cron job，使用 `--session isolated` 每次启动新上下文。对于 main session，可能需要手动清理。

### 坑 7: `failed to obtain token` 连续报错

**症状**: gateway.err.log 中大量 `failed to obtain token` 警告。

**原因**: 某个 model provider 的 OAuth token 过期或失效。

**解决**: 检查 auth-profiles.json 中哪个 provider 有问题，重新认证：
```bash
openclaw auth login <provider>
```

---

## 运维 Checklist

### 每日检查

```bash
# 1. 所有 agent 活跃吗？
openclaw sessions --all-agents --active 60

# 2. cron 正常吗？
openclaw cron list

# 3. 飞书连接正常吗？
grep "WebSocket client started" ~/.openclaw/logs/gateway.log | tail -10

# 4. 有报错吗？
tail -20 ~/.openclaw/logs/gateway.err.log
```

### 故障快速恢复

```bash
# 飞书断连 → 重启 gateway
launchctl stop ai.openclaw.gateway && sleep 3 && launchctl start ai.openclaw.gateway

# Agent 不干活 → 手动催
openclaw agent --agent buyer --message "检查 tasks/pending，有活干活，没活自己找活"

# Cron 不触发 → 手动跑一次
openclaw cron run <job-id>

# Session 满了 → 看上下文使用率
openclaw sessions --agent <id>
```

---

## 工作流总结

```
                    ┌─────────────────────────┐
                    │     包工头 (main)         │
                    │  cron: 每30m巡查          │
                    │  cron: 每4h汇报           │
                    └───┬───────┬───────┬──────┘
                        │       │       │
              bash cat >│       │       │bash cat >
                        ▼       ▼       ▼
              ┌─────┐ ┌────┐ ┌────┐
              │buyer│ │ kb │ │ gf │
              │tasks│ │tasks│ │tasks│
              │pend/│ │pend/│ │pend/│
              │done/│ │done/│ │done/│
              └──┬──┘ └──┬─┘ └──┬─┘
                 │       │      │
            cron 20m  按需派活  cron 2h
                 │       │      │
                 ▼       ▼      ▼
            开发游戏   写书   随机互动
```

## 依赖

- OpenClaw Gateway (运行中，带飞书 WebSocket 连接)
- `feishu-app-setup` 技能（用于创建飞书应用）
- `agent-browser` 技能（可选，用于批量飞书应用配置）
- 飞书企业管理员权限

## License

MIT
