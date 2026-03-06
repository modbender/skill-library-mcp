---
name: message-injector
description: "OpenClaw plugin that prepends custom text to every user message before it reaches the agent. Use for: enforcing memory_search before replies, injecting system-level instructions, adding persistent reminders to every conversation turn. Install as a workspace extension — works on all channels including WebChat, Telegram, Slack, etc."
---

# Message Injector

A lightweight OpenClaw workspace extension that uses the `before_agent_start` hook to inject custom text into every user message via `prependContext`.

## Installation

### 1. Create the extension directory

```bash
mkdir -p ~/.openclaw/workspace/.openclaw/extensions/message-injector
```

### 2. Copy the plugin files

Copy `scripts/index.ts` and `scripts/openclaw.plugin.json` to the extension directory:

```bash
cp scripts/index.ts ~/.openclaw/workspace/.openclaw/extensions/message-injector/
cp scripts/openclaw.plugin.json ~/.openclaw/workspace/.openclaw/extensions/message-injector/
```

### 3. Add configuration

Add the following to `~/.openclaw/openclaw.json` under `plugins.entries`:

```json
"message-injector": {
  "enabled": true,
  "config": {
    "enabled": true,
    "prependText": "Your custom text here"
  }
}
```

### 4. Restart Gateway

```bash
openclaw gateway restart
```

## Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable or disable the injector |
| `prependText` | string | `""` | Text to prepend before every user message |

## Example Use Cases

**Force memory search:**
```json
"prependText": "[⚠️ 回答前必须先 memory_search 检索相关记忆，禁止凭印象回答]"
```

**Add persistent context:**
```json
"prependText": "[当前项目：my-app | 技术栈：React + Node.js | 部署环境：AWS]"
```

**Inject safety rules:**
```json
"prependText": "[RULE: Always verify file paths before deletion. Never run rm -rf without confirmation.]"
```

## How It Works

The plugin registers a `before_agent_start` hook. When triggered, it returns `{ prependContext: prependText }` which OpenClaw prepends to the user's message before the agent processes it. This is a hard injection at the Gateway level — the agent cannot skip or ignore it.

## Source Code

GitHub: https://github.com/Harukaon/openclaw-message-injector
