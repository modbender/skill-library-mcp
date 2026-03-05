# UI Rendering: Buttons

The Gumroad Pro skill uses interactive buttons to provide a streamlined merchant experience on supported channels (Telegram, Slack, Discord, WebChat).

### 🛡️ Reducing Chat Spam
To provide a premium experience, the skill prioritizes **Inline Editing**.

| Action | Behavior | Usage |
| :--- | :--- | :--- |
| `edit` (Default) | Replaces the current message content and buttons. | Use for navigation, detail views, and state updates. |
| `send` | Sends a brand new message to the chat. | Use only for the initial command invocation (`/gp`). |
| `alert` | Shows a temporary notification (platform dependent). | Use for quick confirmations (e.g., "Receipt Resent"). |

> [!IMPORTANT]
> **64-Character Limit**: Telegram and some other platforms limit `callback_data` to **64 characters**. Avoid embedding user input or long keys directly. Use `ctx.session` to pass complex parameters between states.

**AI Rule**: Always set `action: 'edit'` unless you are explicitly starting a new interaction thread. This keeps the user's chat history clean and focused.

## 🏗️ Button Schema
Buttons are structured as a 2D array (rows and columns) of objects:

```json
[
  [
    { "text": "Button 1", "callback_data": "gp:action_1" },
    { "text": "Button 2", "callback_data": "gp:action_2" }
  ],
  [
    { "text": "Button 3 (New Row)", "callback_data": "gp:action_3" }
  ]
]
```

## 🛠️ Implementation Protocol
All UI rendering must pass through the `renderResponse(ctx, data)` helper in `handler.js`.

### 1. Metadata Fields
- **text**: The markdown-formatted message body.
- **buttons**: The 2D array of button objects.
- **action**: (Optional) Default is `edit` for callback responses to keep the chat clean, or `send` for new messages.

### 2. Callback Data Pattern
Always use the `gp:` prefix followed by colon-separated identifiers:
`gp:<resource>:<action>:<id>`
*Example*: `gp:products:details:p123`

### 3. Progressive Disclosure & Navigation
- **Back Buttons**: Every sub-menu MUST include a `[{ text: '🔙 Back', callback_data: '...' }]` button.
- **Fallback**: For non-button channels, the skill automatically appends a numbered list (e.g., `[1] Label`) to the text.

## 📝 Example Response Structure
```javascript
return renderResponse(ctx, {
  text: "📦 **Product: Art Pack**\nPrice: $25.00",
  buttons: [
    [{ text: "📝 Edit", callback_data: "gp:prod_edit:p123" }, { text: "🗑️ Delete", callback_data: "gp:prod_del:p123" }],
    [{ text: "🔙 Back to List", callback_data: "gp:products" }]
  ],
  action: "edit"
});
```
