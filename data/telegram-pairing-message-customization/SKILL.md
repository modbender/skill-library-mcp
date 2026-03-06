---
name: telegram-pairing-message-customization
description: Add custom messages to Telegram pairing replies for unapproved users. Insert custom text (e.g., group links, instructions) above the approval command in pairing messages. Use when unpaired Telegram users need additional guidance during the pairing process.
---

# Telegram 配对消息自定义

## request

实施本技能时, 需要用户提供一份 自定义消息

## 实施内容

### 1. 找到需要修改的文件

在你正在运行的代码中搜索下面的代码段

```javascript
fn: () => bot.api.sendMessage(chatId, [
    "OpenClaw: access not configured.",
    "",
    `Your Telegram user id: ${telegramUserId}`,
    "",
    `Pairing code: ${code}`,
    "",
    "Ask the bot owner to approve with:",
    formatCliCommand("openclaw pairing approve telegram <code>"),
].join("\n")),
```

### 2. 备份文件

修改前备份, 方便以后撤销实施

### 3. 实施修改

在数组中 "Ask the bot owner to approve with:" 项上方添加自定义消息：

修改后

```javascript
fn: () => bot.api.sendMessage(chatId, [
    "OpenClaw: access not configured.",
    "",
    `Your Telegram user id: ${telegramUserId}`,
    "",
    `Pairing code: ${code}`,
    "",
    "YOUR_CUSTOM_MESSAGE_HERE",  // <- 插入自定义消息
    "Ask the bot owner to approve with:",
    formatCliCommand("openclaw pairing approve telegram <code>"),
].join("\n")),
```

### 4. 修改完成后重启服务
```bash
openclaw gateway restart
```

## 验证

让未配对用户发送 `/start` 命令，确认收到带自定义信息的配对消息。

## 一些建议
在寻找需要修改的文件时, 建议先搜索 `Ask the bot owner to approve with:` 可以帮助你先大幅缩小处理范围, 过滤出最有可能的几个文件.

一个建议的起始目录为 /usr/lib/node_modules/openclaw/
