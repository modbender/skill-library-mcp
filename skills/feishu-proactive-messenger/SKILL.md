---
name: feishu-proactive-messenger
description: 飞书主动消息发送器 — 飞书渠道只支持被动回复，agent 无法主动发起对话。本 skill 调用飞书 OpenAPI 发送文本消息，补齐主动投递能力。| Feishu Proactive Messenger — Send text messages proactively via Feishu OpenAPI, filling the channel's missing outbound messaging.
license: MIT
compatibility: openclaw
metadata:
  version: "1.0.1"
  tags: [feishu, message, proactive, outbound, openapi, messaging]
  author: wen-ai
  openclaw:
    emoji: "📨"
    requires:
      bins: [python3]
      config:
        - ~/.openclaw/openclaw.json
---

# Feishu Proactive Messenger | 飞书主动消息发送器

飞书渠道只支持被动回复——用户先发消息，agent 才能回复。当 agent 需要**主动发起对话**（如 Agent A 派任务给 Agent B，Agent B 需要在自己的飞书窗口回复用户），飞书渠道没有这个能力。本 skill 通过直接调用飞书 OpenAPI 发送文本消息，补齐主动投递能力。

The Feishu channel only supports passive replies — the user must send a message first before the agent can respond. When an agent needs to **proactively initiate a conversation** (e.g. Agent A dispatches a task to Agent B, and Agent B needs to reply in its own Feishu chat window), the channel lacks this capability. This skill fills that gap by calling Feishu OpenAPI to send text messages directly.

## 快速开始 | Quick Start

```bash
python3 scripts/feishu_proactive_messenger.py --agent <agent_id> --text "Mission accomplished"
```

`--agent` 指定当前 agent 的 id（如 `coder`、`data`、`life`），脚本会自动读取对应的飞书凭证和 `defaultTo` 目标用户。若省略 `--agent`，则通过 cwd 自动匹配。

`--agent` specifies the current agent's id (e.g. `coder`, `data`, `life`). The script reads the corresponding Feishu credentials and `defaultTo` target automatically. If `--agent` is omitted, the script resolves the agent by matching cwd.

## 使用方法 | Usage

```bash
python3 scripts/feishu_proactive_messenger.py \
  --agent <agent_id> \
  --text "要发送的消息内容" \
  --receive-id <chat_id|open_id> \
  --receive-id-type <chat_id|open_id|user_id>
```

### 参数说明 | Arguments

- `--agent`（推荐）：agent id（如 `coder`、`data`、`main`）。用于确定使用哪个飞书应用的凭证。若省略，通过 cwd 自动匹配（在被派发任务场景下可能不准确，建议显式指定）。
- `--text`（必填）：要发送的消息文本。
- `--receive-id`（可选）：目标 chat_id 或 open_id。若省略，依次从环境变量
  `OPENCLAW_CHAT_ID` / `OPENCLAW_RECEIVE_ID` / `FEISHU_CHAT_ID` 或 account 的
  `defaultTo` 配置中读取。
- `--receive-id-type`（可选）：若省略，根据前缀自动识别：
  - `oc_` → chat_id
  - `ou_` → open_id
  - `on_` → user_id

- `--agent` (recommended): Agent id (e.g. `coder`, `data`, `main`). Determines which Feishu app credentials to use. If omitted, resolves by matching cwd (may be inaccurate in dispatched-task scenarios; explicit is recommended).
- `--text` (required): The message text to send.
- `--receive-id` (optional): Target chat_id or open_id. If omitted, reads from
  env `OPENCLAW_CHAT_ID` / `OPENCLAW_RECEIVE_ID` / `FEISHU_CHAT_ID`, or from
  the account's `defaultTo` config.
- `--receive-id-type` (optional): If omitted, auto-detect by prefix:
  - `oc_` → chat_id
  - `ou_` → open_id
  - `on_` → user_id

## 工作原理 | How It Works

1. 通过 `--agent` 参数或 `cwd` 匹配确定当前 agent id。
2. 根据 agent id 从 `~/.openclaw/openclaw.json` 读取对应 account 的 appId/appSecret。
3. 从同一 account 的 `defaultTo` 读取默认目标用户（如未通过参数指定）。
4. 获取 tenant access token。
5. 通过飞书 `bot/v3/info` API 获取 bot 显示名称。
6. 调用飞书 **发送消息** API（`im/v1/messages`）发送文本消息。
7. 输出简洁结果：`✅ [Bot名称] 消息已发送`。

1. Determine agent id via `--agent` parameter or by matching `cwd`.
2. Read appId/appSecret from `~/.openclaw/openclaw.json` based on the agent id.
3. Read the default target user from the same account's `defaultTo` (if not specified via args).
4. Obtain a tenant access token.
5. Retrieve the bot's display name via Feishu `bot/v3/info` API.
6. Call Feishu **Send Message** API (`im/v1/messages`) to deliver the text message.
7. Output clean result: `✅ [BotName] 消息已发送`.

## 前置配置 | Prerequisites

每个飞书 account 需要配置 `defaultTo`，指向目标用户的 open_id：

Each Feishu account needs a `defaultTo` pointing to the target user's open_id:

```bash
openclaw config set channels.feishu.accounts.<account>.defaultTo "user:ou_xxx"
```

注意：飞书的 open_id 是按应用隔离的，同一个用户在不同 bot 下有不同的 open_id。

Note: Feishu open_id is app-scoped — the same user has different open_ids under different bots.

## 错误处理 | Error Handling

- **缺少凭证** → 确保 `channels.feishu.accounts` 存在于
  `~/.openclaw/openclaw.json`，且 bindings 映射 agentId → accountId。
- **机器人不在聊天中（230002）** → 用户需要先跟该 bot 发起过对话。
- **缺少 receive_id** → 传入 `--receive-id`，设置 `OPENCLAW_CHAT_ID`，
  或配置 `defaultTo`。
- **HTTP 错误** → 查看飞书错误返回中的 `log_id` 进行排查。

- **Missing credentials** → Ensure `channels.feishu.accounts` exists in
  `~/.openclaw/openclaw.json` and bindings map agentId → accountId.
- **Bot not in chat (code 230002)** → The user must have initiated a chat with
  the bot at least once.
- **Missing receive_id** → Pass `--receive-id`, set `OPENCLAW_CHAT_ID`,
  or configure `defaultTo`.
- **HTTP errors** → Check the returned `log_id` in Feishu error payload.

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

## 备注 | Notes

- 本技能面向 **所有 agent** 设计，通过 `--agent` 参数或工作区匹配选择正确的飞书应用凭证。
- 配合 `defaultTo` 使用时，agent 无需知道任何 ID 即可主动发消息。
- 与 `feishu-file-sender` 互补：一个发文件，一个发文本。

- Designed for **all agents**; uses `--agent` parameter or workspace matching to choose credentials.
- When used with `defaultTo`, agents can send messages without knowing any IDs.
- Complements `feishu-file-sender`: one sends files, the other sends text.

## 随附脚本 | Bundled Script

- `scripts/feishu_proactive_messenger.py`

## 更新日志 | Changelog

### 1.0.1
- 新增 `--agent` 参数，显式指定 agent 身份（解决被派发任务时 cwd 匹配不准确的问题）
- 新增通过飞书 `bot/v3/info` API 获取 bot 显示名称
- 输出简化为 `✅ [Bot名称] 消息已发送`，不再暴露 open_id 等敏感信息
- `resolve_agent_id` 支持 `agents.defaults.workspace` 作为 fallback

### 1.0.0
- 初始版本
