---
name: conversation-summary
description: 会话小结 - 输入对话内容，调用API返回会话摘要，支持增量更新历史摘要。
emoji: 📝
author: openclaw
version: 1.0.0
license: MIT
requires:
  bins:
    - python3
  pip:
    - requests
tools:
  - name: summarize_conversation
    description: 对对话内容进行小结，生成会话摘要
    parameters:
      type: object
      properties:
        chat_list:
          type: string
          description: "对话内容列表，JSON格式的对话记录，例如：[{\"role\":\"user\",\"content\":\"你好\"}]"
        history_summary:
          type: string
          description: "历史会话摘要（可选），用于增量更新摘要，默认为空"
      required: [chat_list]
---

# Conversation Summary - Agent Instructions

Use this skill to generate summaries for conversation content.

## Usage

When the user requests any of the following:
- "帮我总结一下这段对话"
- "生成会话小结"
- "对这些聊天记录做个摘要"
- "总结一下我们刚才聊了什么"

Use the `summarize_conversation` tool to call the summary API.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| chat_list | string | Yes | JSON formatted conversation content |
| history_summary | string | No | Previous summary for incremental update |

### chat_list Format Example

```json
[
  {"role": "user", "content": "今天天气怎么样？"},
  {"role": "assistant", "content": "今天天气晴朗，气温25度。"}
]
```

## Response

The API returns JSON with:
- `code`: Status code, 0 means success
- `message`: Status message
- `data.summary`: Generated conversation summary

## Error Handling

- If the API returns a non-zero code, report the error message to the user
- If the request fails, check network connectivity
- Ensure chat_list is valid JSON format before calling
