---
name: telegram-topic-rename
description: Rename Telegram forum topics and change icons via Bot API. Use when user asks to name/rename a topic, change topic title, update topic icon, or says "命名这个topic", "给话题起个名", "换个图标". Requires TELEGRAM_BOT_TOKEN environment variable.
---

# Telegram Topic Rename / Telegram 话题命名

Rename Telegram forum topics and optionally change their icons.

重命名 Telegram 论坛话题，可选更换图标。

## Setup / 配置

Set `TELEGRAM_BOT_TOKEN` in your environment or OpenClaw config:

在环境变量或 OpenClaw 配置中设置 `TELEGRAM_BOT_TOKEN`：

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
```

## Usage / 使用方法

### Get topic info / 获取话题信息

Extract from session context:
- `chat_id`: User ID (private) or group ID
- `thread_id`: From `message_thread_id` or session key

从会话上下文提取：
- `chat_id`：用户 ID（私聊）或群组 ID
- `thread_id`：从 `message_thread_id` 或 session key 获取

### Run the script / 运行脚本

```bash
# Rename only / 仅改名
scripts/rename-topic.sh <chat_id> <thread_id> "新名称"

# Rename + change icon (emoji shortcut) / 改名 + 换图标（emoji 快捷方式）
scripts/rename-topic.sh <chat_id> <thread_id> "新名称" 🤖

# Rename + change icon (full ID) / 改名 + 换图标（完整 ID）
scripts/rename-topic.sh <chat_id> <thread_id> "新名称" 5309832892262654231

# List available icons / 列出可用图标
scripts/rename-topic.sh --icons
```

### Naming rules / 命名规则

- **Length / 长度**: ≤10 characters / 字符
- **Style / 风格**: Concise, capture the core theme / 简洁，抓住核心主题
- **Auto-icon / 自动选图标**: Match icon to topic theme (see references/icons.md)

## Icon quick reference / 图标速查

| Theme / 主题 | Icon |
|-------------|------|
| AI / 机器人 | 🤖 |
| Code / 编程 | 💻 |
| Science / 科学 | 🔬 |
| Work / 工作 | 💼 |
| Notes / 笔记 | 📝 |
| Chat / 闲聊 | 💬 |
| Games / 游戏 | 🎮 |
| Music / 音乐 | 🎵 |
| Ideas / 想法 | 💡 |
| Fire / 热门 | 🔥 |

Full list: See [references/icons.md](references/icons.md)

完整列表：见 [references/icons.md](references/icons.md)
