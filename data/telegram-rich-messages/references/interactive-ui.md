# Telegram Interactive UI

## Inline Buttons (Recommended)
Inline buttons are attached directly to a message. Clicking them sends a `callback_query` back to the bot.

### How to use (Standard Method)
Always use the `message` tool with the `buttons` parameter for maximum reliability.

```json
{
  "action": "send",
  "channel": "telegram",
  "target": "telegram:2136878064",
  "message": "What would you like to do next?",
  "buttons": [
    [
      { "text": "🎨 Start Creation", "callback_data": "start_apollo" },
      { "text": "📧 Check Mail", "callback_data": "check_mail" }
    ],
    [
      { "text": "⚙️ Settings", "callback_data": "show_settings" },
      { "text": "🌐 Visit Website", "url": "https://example.com" }
    ]
  ]
}
```

### Layout Rules
- `buttons` is an array of arrays (rows of buttons).
- **One button per row**: Best for mobile clarity.
- **Two buttons per row**: Good for binary choices (Yes/No).
- **Max rows**: 10 (keep it concise).

## Quick Replies (Reply Keyboard)
This feature replaces the user's keyboard with large buttons. 

### Usage via Directive
If you must use a string tag, place it at the very end of your response:
`[[quick_replies: Option 1, Option 2, Option 3]]`

*Note*: Directives are less stable than the `message` tool. Prefer Inline Buttons for mission-critical interactions.

## Interactive Flow Strategy
1. **The Question**: Clearly state the choice.
2. **The Buttons**: Provide concise labels (1-2 words + emoji).
3. **The Feedback**: When a button is clicked, acknowledge the action immediately (e.g., "Starting creation...").
