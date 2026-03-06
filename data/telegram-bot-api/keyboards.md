# Keyboards & Buttons — Telegram Bot API

## Keyboard Types

| Type | Position | Persists | Use Case |
|------|----------|----------|----------|
| InlineKeyboardMarkup | In message | With message | Actions, navigation, menus |
| ReplyKeyboardMarkup | Below input | Until removed | Frequent options |
| ReplyKeyboardRemove | — | — | Remove reply keyboard |
| ForceReply | — | — | Force user to reply |

---

## Inline Keyboards

### Basic Inline Keyboard

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Choose an option:",
    "reply_markup": {
      "inline_keyboard": [
        [
          {"text": "Option 1", "callback_data": "opt1"},
          {"text": "Option 2", "callback_data": "opt2"}
        ],
        [
          {"text": "Option 3", "callback_data": "opt3"}
        ]
      ]
    }
  }'
```

### Button Types

```json
// Callback button (bot receives callback_query)
{"text": "Click me", "callback_data": "action_id"}

// URL button (opens link)
{"text": "Visit Site", "url": "https://example.com"}

// Web App button
{"text": "Open App", "web_app": {"url": "https://webapp.example.com"}}

// Login button (for websites with Telegram Login)
{"text": "Login", "login_url": {"url": "https://example.com/auth"}}

// Switch inline query (opens inline mode)
{"text": "Share", "switch_inline_query": "preset query"}

// Switch inline in current chat
{"text": "Search here", "switch_inline_query_current_chat": ""}

// Pay button (for payments)
{"text": "Pay $10", "pay": true}
```

### Handling Callback Queries

When user clicks inline button:

```json
{
  "update_id": 123456789,
  "callback_query": {
    "id": "query_id",
    "from": {"id": 123456789, "first_name": "User"},
    "message": {
      "message_id": 100,
      "chat": {"id": 123456789}
    },
    "data": "opt1"
  }
}
```

**Always answer the callback:**

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/answerCallbackQuery" \
  -d "callback_query_id=query_id" \
  -d "text=Option 1 selected"
```

### Edit Message After Button Press

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/editMessageText" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "message_id": 100,
    "text": "You selected Option 1!",
    "reply_markup": {
      "inline_keyboard": [
        [{"text": "← Back", "callback_data": "back"}]
      ]
    }
  }'
```

---

## Reply Keyboards

### Basic Reply Keyboard

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Choose an option:",
    "reply_markup": {
      "keyboard": [
        [{"text": "Option 1"}, {"text": "Option 2"}],
        [{"text": "Option 3"}]
      ],
      "resize_keyboard": true,
      "one_time_keyboard": true
    }
  }'
```

### Keyboard Options

| Option | Default | Description |
|--------|---------|-------------|
| `resize_keyboard` | false | Fit keyboard to buttons |
| `one_time_keyboard` | false | Hide after button press |
| `input_field_placeholder` | — | Placeholder in input field |
| `selective` | false | Show only to specific users |
| `is_persistent` | false | Always show keyboard |

### Special Button Types

```json
// Request phone number
{"text": "Share Phone", "request_contact": true}

// Request location
{"text": "Share Location", "request_location": true}

// Request poll
{"text": "Create Poll", "request_poll": {"type": "quiz"}}

// Request users
{"text": "Select User", "request_users": {"request_id": 1}}

// Request chat
{"text": "Select Chat", "request_chat": {"request_id": 2, "chat_is_channel": false}}
```

### Remove Reply Keyboard

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Keyboard removed.",
    "reply_markup": {"remove_keyboard": true}
  }'
```

---

## Common Patterns

### Pagination

```json
{
  "inline_keyboard": [
    [
      {"text": "Item 1", "callback_data": "item_1"},
      {"text": "Item 2", "callback_data": "item_2"}
    ],
    [
      {"text": "Item 3", "callback_data": "item_3"},
      {"text": "Item 4", "callback_data": "item_4"}
    ],
    [
      {"text": "« Prev", "callback_data": "page_0"},
      {"text": "1/5", "callback_data": "noop"},
      {"text": "Next »", "callback_data": "page_2"}
    ]
  ]
}
```

### Confirmation Dialog

```json
{
  "inline_keyboard": [
    [
      {"text": "✅ Confirm", "callback_data": "confirm_delete"},
      {"text": "❌ Cancel", "callback_data": "cancel"}
    ]
  ]
}
```

### Menu Navigation

```json
{
  "inline_keyboard": [
    [{"text": "📊 Statistics", "callback_data": "menu_stats"}],
    [{"text": "⚙️ Settings", "callback_data": "menu_settings"}],
    [{"text": "❓ Help", "callback_data": "menu_help"}]
  ]
}
```

### Toggle Button

```json
// State: ON
{"text": "🔔 Notifications: ON", "callback_data": "toggle_notif"}

// State: OFF (after toggle)
{"text": "🔕 Notifications: OFF", "callback_data": "toggle_notif"}
```

---

## Limits & Constraints

| Limit | Value |
|-------|-------|
| Max buttons per row | 8 |
| Max buttons total | 100 |
| callback_data max length | 64 bytes |
| Button text max length | 64 chars (display may truncate) |

---

## Tips

1. **Use emojis** — Make buttons visually clear: ✅ ❌ ⬅️ ➡️
2. **Keep callback_data short** — Max 64 bytes, use IDs not full text
3. **Always answer callbacks** — User sees loading indicator until you respond
4. **Update message on action** — Show feedback by editing the message
5. **Use resize_keyboard** — Reply keyboards look better when resized
