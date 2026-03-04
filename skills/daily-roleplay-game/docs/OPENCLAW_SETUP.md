# OpenClaw 部署指南

本系统作为**独立 agent** 部署（不替换默认 agent），拥有独立 workspace、心跳和定时任务。`setup.sh` 会自动创建 `role-play` agent 和 workspace，不影响现有配置。

---

## 1. 安装并部署

### 方式 A：ClawHub（推荐）

```bash
clawhub install daily-roleplay-game
./skills/daily-roleplay-game/scripts/setup.sh
```

### 方式 B：Git Clone

```bash
git clone https://github.com/nannyu/openclaw-role-play-skill.git
cd openclaw-role-play-skill
./scripts/setup.sh
```

`setup.sh` 会自动：
- 检测 `openclaw` CLI，如可用则创建 `role-play` agent
- 在 `~/.openclaw/workspace-role-play/` 部署引擎文件和数据
- 引导角色设定（交互模式）或留空（非交互模式）

> 也可指定自定义 workspace 路径：`./scripts/setup.sh /path/to/workspace`

## 2. 配置 openclaw.json

将以下内容合并到 `~/.openclaw/openclaw.json`（参考 `openclaw.example.json5`）：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
        activeHours: { start: "06:00", end: "23:59" },
      },
    },
    list: [
      {
        id: "role-play",
        name: "角色扮演",
        workspace: "~/.openclaw/workspace-role-play",
        model: "anthropic/claude-sonnet-4-5",
      },
    ],
  },
}
```

**关键配置说明**：

| 字段 | 说明 |
|------|------|
| `workspace` | 需与 setup.sh 的部署路径一致（默认 `~/.openclaw/workspace-role-play`） |
| `agents.defaults.heartbeat` | 全局心跳配置，30 分钟间隔用于三级暗示系统 |
| `heartbeat.activeHours` | 限制心跳在 6:00-24:00 活跃（角色扮演时段） |
| `model` | 字符串格式，可按需更换模型 |

> **注意**：`heartbeat` 为全局配置，放在 `agents.defaults` 下，会影响所有 agent。若只需 role-play agent 使用心跳，可将 role-play 设为默认 agent，或在其他 agent 的 `HEARTBEAT.md` 中写 `HEARTBEAT_OK` 来跳过。

## 3. 编辑必填配置

部署后必须编辑以下文件：

```bash
cd ~/.openclaw/workspace-role-play
```

### MEMORY.md — 消息频道（必填）

```markdown
## 系统配置
- **消息频道**：（填写你的频道标识）
  - 格式：discord:频道ID / telegram:频道ID / feishu:xxx / last
```

ENGINE.md 和 HEARTBEAT.md 中的消息发送会读取此处的频道配置。

### IDENTITY.md — 角色基础信息

```markdown
- **Name:** （角色名称）
- **Timezone:** Asia/Shanghai
```

### USER.md — 主人信息

按提示填写称呼和偏好。

### TOOLS.md — 生图工具

配置生图后端（ComfyUI / SD WebUI / Midjourney / Nano Banana Pro），填写工具类型和接入地址。不使用生图功能可填「无」。

## 4. 配置定时任务

### 每日 6:00 — 自动初始化

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

> `--delivery none`：agent 在执行过程中已通过 message tool 发送早安消息，无需 cron 再发摘要。
> `--model opus`：初始化流程涉及多步推理和内容生成，建议使用高能力模型。

### 每日 23:30 — 自动收尾归档

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

### 验证任务

```bash
openclaw cron list
```

## 5. 频道绑定（可选）

如需将 agent 绑定到特定消息频道，在 `openclaw.json` 中使用顶层 `bindings` 数组配置消息路由，并在 `channels` 中配置账号信息。详见 [OpenClaw 多 Agent 文档](https://docs.openclaw.ai/concepts/multi-agent)。

### Discord

```json5
{
  bindings: [
    { agentId: "role-play", match: { channel: "discord", accountId: "default" } },
  ],
  channels: {
    discord: {
      groupPolicy: "allowlist",
      accounts: {
        default: {
          token: "DISCORD_BOT_TOKEN",
          guilds: {
            "GUILD_ID": {
              channels: { "CHANNEL_ID": { allow: true, requireMention: false } },
            },
          },
        },
      },
    },
  },
}
```

### Telegram

```json5
{
  bindings: [
    { agentId: "role-play", match: { channel: "telegram", accountId: "default" } },
  ],
  channels: {
    telegram: {
      accounts: {
        default: { botToken: "TELEGRAM_BOT_TOKEN", dmPolicy: "pairing" },
      },
    },
  },
}
```

### 飞书 / 其他平台

```json5
{
  bindings: [
    { agentId: "role-play", match: { channel: "feishu", accountId: "default" } },
  ],
  // channels.feishu 配置按 OpenClaw 官方文档填写
}
```

> **说明**：`bindings` 中的 `match.channel` 值对应平台名称（discord / telegram / feishu / whatsapp / slack），`accountId` 对应 `channels` 中配置的账号 key。

## 6. 首次运行检查清单

- [ ] `setup.sh` 已执行成功（自动创建 agent + workspace）
- [ ] `openclaw.json` 中已添加 role-play agent 配置（心跳、model 等）
- [ ] `MEMORY.md` 已填入消息频道标识
- [ ] `IDENTITY.md` 已填入角色名称和时区
- [ ] `USER.md` 已填写主人信息
- [ ] `TOOLS.md` 已配置生图工具（或填「无」）
- [ ] cron 任务已添加（`openclaw cron list` 可见）
- [ ] 心跳已生效（agent 每 30 分钟自动执行 HEARTBEAT.md）

## 7. 测试

手动触发一次初始化：

```bash
openclaw cron run <job-id>
```

或直接对 role-play agent 发消息，确认角色已正常进入。

---

## 架构说明

```
~/.openclaw/
├── openclaw.json              ← 全局配置（含 role-play agent）
├── cron/jobs.json             ← 定时任务持久化
├── agents/role-play/          ← agent 运行时数据（自动创建）
└── workspace-role-play/       ← 角色扮演 workspace（setup.sh 部署）
    ├── SOUL.md / ENGINE.md / AGENTS.md / HEARTBEAT.md
    ├── USER.md / MEMORY.md / TOOLS.md / IDENTITY.md
    ├── roleplay-active.md     ← 每日生成
    ├── guess-log.md           ← 当日猜测进度
    ├── data/                  ← 游戏数据库
    ├── scripts/               ← wrapup.sh 等
    └── archive/               ← 历史存档
```
