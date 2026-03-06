# Feishu Proactive Messenger | 飞书主动消息发送器

飞书渠道只支持被动回复——用户先发消息，agent 才能回复。当 agent 需要**主动发起对话**（如 Agent A 派任务给 Agent B，Agent B 需要在自己的飞书窗口回复用户），飞书渠道没有这个能力。本 skill 通过直接调用飞书 OpenAPI 发送文本消息，补齐主动投递能力。

The Feishu channel only supports passive replies — the user must message first. When an agent needs to **proactively initiate a conversation** (e.g. Agent A dispatches a task to Agent B, and Agent B needs to reply in its own Feishu chat window), the channel lacks this capability. This skill fills that gap by calling Feishu OpenAPI directly.

## 为什么需要这个 skill | Why this skill

OpenClaw 的飞书渠道是被动模式：用户发消息 → agent 回复。但在多 agent 场景下，Agent A 派任务给 Agent B 后，Agent B 需要通过**自己的飞书窗口**主动给用户发消息。没有本 skill，Agent B 只能在 Agent A 的窗口里回复，用户在 Agent B 的聊天窗口看不到任何消息。

OpenClaw's Feishu channel is passive: user sends → agent replies. In multi-agent setups, when Agent A dispatches a task to Agent B, Agent B needs to send a message in **its own Feishu chat window**. Without this skill, Agent B can only reply in Agent A's window — the user sees nothing in Agent B's chat.

## 功能亮点 | Features

- 📨 agent 可主动发送飞书文本消息，无需用户先发消息
- 🔑 自动从 OpenClaw 配置读取 appId/appSecret
- 🎯 自动从 `defaultTo` 读取目标用户，无需手动传 ID
- 🏷️ 自动获取飞书 bot 显示名称，输出清晰的发送结果
- 🧭 通过 `--agent` 参数或工作区匹配，对 **所有 agent** 通用
- 🧰 简洁的命令行工具

- 📨 Agents can proactively send Feishu text messages without user initiation
- 🔑 Auto-resolve appId/appSecret from OpenClaw config
- 🎯 Auto-read target user from `defaultTo` — no manual IDs needed
- 🏷️ Auto-fetch bot display name from Feishu for clean output
- 🧭 Works across **all agents** via `--agent` parameter or workspace matching
- 🧰 Simple CLI tool

## 运行要求 | Requirements

- Python 3.6+
- 已安装 `requests`
- OpenClaw 已配置飞书渠道
- 每个 account 已配置 `defaultTo`

- Python 3.6+
- `requests` installed
- OpenClaw with Feishu channel configured
- Each account has `defaultTo` configured

## 安装 | Install

```bash
python3 -m pip install requests
```

## 用法 | Usage

### 推荐用法 | Recommended usage

```bash
python3 scripts/feishu_proactive_messenger.py --agent <agent_id> --text "Mission accomplished"
```

`--agent` 指定当前 agent 的 id（如 `coder`、`data`、`life`），确保使用正确的飞书应用凭证。

### 指定目标 | Specify target

```bash
python3 scripts/feishu_proactive_messenger.py \
  --agent <agent_id> \
  --text "Mission accomplished" \
  --receive-id ou_xxx \
  --receive-id-type open_id
```

### 输出示例 | Output example

```
✅ [Wen·程序员] 消息已发送
```

## 前置配置 | Prerequisites

为每个飞书 account 配置 `defaultTo`（只需做一次）：

Set `defaultTo` for each Feishu account (one-time setup):

```bash
openclaw config set channels.feishu.accounts.main.defaultTo "user:ou_xxx"
openclaw config set channels.feishu.accounts.agent-b.defaultTo "user:ou_yyy"
# ... 其他 account
openclaw gateway restart
```

获取 open_id 的方法：给每个 bot 发一条消息，然后查日志：

How to get open_ids: send a message to each bot, then check logs:

```bash
openclaw logs --limit 300 | grep "ou_"
```

注意：飞书 open_id 是按应用隔离的，同一用户在不同 bot 下有不同的 open_id。

Note: Feishu open_id is app-scoped — same user gets different open_ids per bot.

## 工作原理 | How It Works

1. 通过 `--agent` 参数或 `cwd` 匹配确定当前 agent id。
2. 通过绑定关系从 `~/.openclaw/openclaw.json` 读取 Feishu appId/appSecret。
3. 从同一 account 的 `defaultTo` 读取默认目标（去掉 `user:` 前缀）。
4. 获取 tenant access token。
5. 通过飞书 `bot/v3/info` API 获取 bot 显示名称。
6. 调用消息发送接口（`im/v1/messages`）发送文本消息。
7. 输出 `✅ [Bot名称] 消息已发送`。

1. Determine agent id via `--agent` parameter or by matching `cwd`.
2. Read Feishu appId/appSecret from `~/.openclaw/openclaw.json` via bindings.
3. Read default target from the same account's `defaultTo` (strip `user:` prefix).
4. Obtain tenant access token.
5. Retrieve bot display name via Feishu `bot/v3/info` API.
6. Send a text message via `im/v1/messages`.
7. Output `✅ [BotName] 消息已发送`.

## 常见错误处理 | Error Handling

| 问题 | 原因 | 解决办法 |
|------|------|---------|
| `Missing receive_id` | 未传 `--receive-id` 且无 `defaultTo` | 配置 `defaultTo` 或传入 `--receive-id` |
| `No Feishu account binding` | 缺少 agent 绑定 | 确保 OpenClaw 配置中 agentId → accountId 绑定存在 |
| `Bot/User can NOT be out of the chat (230002)` | 用户未跟该 bot 发起过对话 | 先在飞书上给该 bot 发一条消息 |
| `HTTPError` | API 调用失败 | 查看响应 `log_id` 与飞书排障链接 |

| Issue | Cause | Fix |
|------|------|-----|
| `Missing receive_id` | No `--receive-id` and no `defaultTo` | Configure `defaultTo` or pass `--receive-id` |
| `No Feishu account binding` | Agent binding missing | Ensure bindings map agentId → accountId in OpenClaw config |
| `Bot/User can NOT be out of the chat (230002)` | User never chatted with bot | Send a message to the bot in Feishu first |
| `HTTPError` | API failure | Check response `log_id` and Feishu troubleshooting link |

## 安全说明 | Security

本技能从 `~/.openclaw/openclaw.json` 读取飞书凭证：

- `channels.feishu.accounts.*.appId`
- `channels.feishu.accounts.*.appSecret`

凭证仅用于获取 tenant access token 并发送消息。技能不会存储或向其他地方传输凭证。

This skill reads Feishu credentials from `~/.openclaw/openclaw.json`:

- `channels.feishu.accounts.*.appId`
- `channels.feishu.accounts.*.appSecret`

These values are used only to obtain a tenant access token and send the message.
The skill does not store or transmit credentials anywhere else.

## 更新日志 | Changelog

### 1.0.1
- 新增 `--agent` 参数，显式指定 agent 身份（解决被派发任务时 cwd 匹配不准确的问题）
- 新增通过飞书 `bot/v3/info` API 获取 bot 显示名称
- 输出简化为 `✅ [Bot名称] 消息已发送`，不再暴露敏感信息
- `resolve_agent_id` 支持 `agents.defaults.workspace` 作为 fallback

### 1.0.0
- 初始版本：主动发送飞书文本消息

## 许可证 | License

MIT
