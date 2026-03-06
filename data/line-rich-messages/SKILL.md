---
name: line-rich-messages
description: Comprehensive guide for LINE Rich UI features (Flex Messages, buttons, quick replies, and markdown auto-conversion). Use this skill to provide a professional, low-friction experience for LINE users, prioritizing interactive elements over manual text input.
metadata:
  {
    "openclaw":
      {
        "requires": { "plugins": ["line"] },
      },
  }
---

# LINE Rich Messages

This skill transforms the agent from a text-only bot into a professional LINE assistant with native UI capabilities.

## Core Principle: Rich-UI 優先 (Low-Friction)
**Typing on mobile is slow and error-prone.** Always prioritize Rich UI elements to minimize the user's need to reply with text.

## Quick Navigation
Detailed guides for each feature:

1. **[decision-matrix.md](references/decision-matrix.md)**: Choose the best UI element for your scenario.
2. **[directives.md](references/directives.md)**: Syntax for interactive cards and bubbles.
3. **[flex-templates.md](references/flex-templates.md)**: **Raw JSON Templates** for 100% reliable UI creation.
4. **[markdown-to-flex.md](references/markdown-to-flex.md)**: Auto-美化 tables and code blocks.

<!-- file delivery removed for security -->

## Best Practices
- **No file delivery**: For security, this skill intentionally does **not** include any workflow for uploading/sharing files (e.g., Google Drive). If you need file delivery, implement it in a separate, tightly-scoped skill with explicit allowlists and safeguards.
- **Guided Choices**: If you ask a question with 2-4 fixed answers, always include `[[quick_replies: ...]]`.
- **Structured Data**: Use Markdown tables for any multi-point information (e.g., flight times, order items).
- **Destructive Actions**: Use `[[confirm: ...]]` for actions like "Delete Memory" or "Cancel Project".
- **UX Limitation (Crucial)**: Text within Flex Messages (including Markdown tables and auto-converted replies) **cannot be selected or copied** by the user. 
  - **Rule**: If the data is meant to be copied (e.g., SSH keys, IDs, URLs), **always send it as plain text** without Markdown formatting or directives that trigger Flex conversion.

## Security / Scope (Important)
- This skill is **documentation + templates** for building a better LINE UX (Flex, buttons, quick replies).
- It **does not ship credentials** and **does not automatically** make external API calls.
- Anything that touches the network or third-party services must be **explicitly requested by the user** and only after the runtime is correctly configured.

### Credentials / Setup Clarification
- **LINE**: Sending messages is handled by your OpenClaw **LINE channel/plugin setup**. This skill does **not** require you to declare or embed `LINE_CHANNEL_ACCESS_TOKEN` / `LINE_CHANNEL_SECRET`.
- **File delivery**: Intentionally **not included** (removed for safety). Do not upload/share local files from an agent runtime.

## 🏆 終極解決方案：手工 Raw Flex (The Golden Path)

若系統標籤轉換失敗，請使用 **手工構建 JSON**。這是最穩定且能 100% 呈現自定義 UI 的方式。

### 穩定發送按鈕的 JSON 模板
將此 JSON 作為純文字發送，若系統支援自動偵測則會轉換；若不支援，請改走 OpenClaw 的 LINE plugin 正規發送路徑（或由管理員在已授權的環境中操作），避免在 skill 內容中引導直接 `curl` 呼叫外部 API。

```json
{
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      { "type": "text", "text": "標題", "weight": "bold", "size": "lg" },
      { "type": "text", "text": "內文描述", "wrap": true },
      {
        "type": "button",
        "style": "primary",
        "color": "#1DB446",
        "action": {
          "type": "message",
          "label": "按鈕文字",
          "text": "回傳指令"
        }
      }
    ]
  }
}
```
