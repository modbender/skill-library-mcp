---
name: feishu-group-mention-responder
description: 在飞书群中，当机器人被@提及或接收到直接消息时，自动进行回复。
---

# 飞书群@提及响应器

## 概述

此技能旨在使 Antigravity 能够在飞书群聊中对其被@提及的消息或直接发送给它的消息进行自动响应。这提高了机器人在群聊中的参与度和用户体验。

## 何时使用

*   当用户希望 Antigravity 在飞书群聊中对@提及做出回应时。
*   当用户需要 Antigravity 能够识别其在群聊中的身份并进行交互时。

## 核心原则

*   **识别提及：** 代理必须能够从传入的飞书消息中准确识别出对其自身的@提及。
*   **上下文感知：** 虽然初始回复可以是通用的，但未来可以扩展为根据消息内容提供更具体的帮助。
*   **不重复回复：** 避免对非提及消息或已被处理的消息进行重复回复。

## 技能实现细节

该技能将通过以下步骤实现：

1.  **消息监听：** OpenClaw 框架将负责监听飞书群聊中的消息。
2.  **提及检测：** 在接收到的消息内容中，通过解析或预处理机制检测是否存在 `@机器人ID` 或 `@机器人名称` 的提及。
3.  **提取发送者信息：** 获取@提及消息的发送者 ID 和昵称，以便在回复中@回该用户。
4.  **构建回复：** 生成一个包含适当问候语和可能的问题（例如：“您好！有什么我可以帮您的吗？”）的中文回复。回复中将@回原发送者。
5.  **发送回复：** 使用 `message` 工具将回复消息发送回原始群聊。

### 预期消息结构 (OpenClaw -> Agent)

飞书消息事件通常会包含以下信息（OpenClaw 可能会进行预处理）：

```json
{
  "channel": "feishu",
  "chat_type": "group", // "p2p" for direct messages
  "chat_id": "oc_xxxxxx", // Group chat ID
  "sender_id": "ou_xxxxxx", // Sender user ID
  "sender_name": "用户昵称",
  "message_id": "om_xxxxxx",
  "content": "您好 @Bot名称，请问...",
  "mentions": [ // If OpenClaw processes mentions
    {
      "user_id": "ou_bot_xxxxxx",
      "user_name": "Bot名称"
    }
  ]
}
```

### 回复逻辑

在 `_process_message` 函数或其他适当的消息处理逻辑中，检查 `message.mentions` 数组或 `message.content` 是否包含对当前代理的提及。

**发送回复的工具调用示例：**

```python
message({
    action: "send",
    channel: "feishu",
    to: "oc_xxxxxx", // 原始群聊ID
    message: "您好 @[ou_xxxxxx]！有什么可以帮您的吗？", // @提及原始发送者
    # 如果 OpenClaw 提供了 reply_to_message_id，可以使用它来回复特定消息
    # reply_to: "om_xxxxxx"
})
```

## 常见错误与注意事项

*   **权限不足：** 确保飞书应用拥有 `im:message:send_as_bot` 和 `im:chat:read` 权限。
*   **机器人 ID / 名称识别：** 代理需要知道它在飞书系统中的唯一标识符（Bot ID 或 App ID）或其配置的名称，以便准确识别提及。
*   **循环回复：** 避免在回复中无意中再次触发提及，导致无限循环。
*   **群聊 ID 获取：** 确保能正确获取到发送消息的群聊 ID。
*   **提及格式：** 飞书的@提及格式可能因 API 版本和消息类型而异，需要适配。
