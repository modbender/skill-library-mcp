# Openclaw AI Bot — Colored Choice Buttons Skill

## Purpose
Every time the bot presents choices to the user, it MUST automatically color each button based on how critical, irreversible, or different the choices are. The bot never sends plain/unstyled choice buttons — color is always applied.

## Core Rule
**Whenever the bot sends 2+ choices to a user, classify each choice and assign a `style` automatically. This is not optional.**

---

## Telegram Bot API — Button Styles

Two fields on `InlineKeyboardButton` and `KeyboardButton`:

- **`style`** (String, Optional) — Button color:
  - *(omit)* — Default accent/blue. **The recommended / safe / primary action.**
  - `"destructive"` — Red. **Irreversible, dangerous, or high-stakes actions.**
  - `"secondary"` — Gray/muted. **Low-priority, dismiss, skip, or neutral actions.**

- **`icon_custom_emoji_id`** (String, Optional) — Custom emoji icon on the button.

---

## Automatic Classification Rules

When the bot builds a set of choice buttons, it MUST classify every choice into one of three tiers before sending:

### Tier 1 — Default (accent/blue): The recommended path
Apply when the choice is:
- The safest or most common action
- A positive confirmation ("Yes", "Continue", "Accept", "Start")
- The action the bot would recommend
- Moving forward in a flow

**Do:** omit the `style` field (or set to `null`).

### Tier 2 — Destructive (red): High-stakes or irreversible
Apply when the choice:
- Deletes, removes, or permanently changes something
- Cancels an in-progress operation that loses work
- Blocks, bans, or restricts a user
- Rejects, declines, or refuses something important
- Spends money, tokens, or credits
- Cannot be undone easily

**Do:** set `"style": "destructive"`.

### Tier 3 — Secondary (gray): Low-priority or escape hatch
Apply when the choice:
- Skips, dismisses, or postpones ("Maybe later", "Not now")
- Is a neutral fallback ("Back", "Cancel" when nothing is lost)
- Shows more info without committing ("Details", "Help")
- Is the least important option in the set

**Do:** set `"style": "secondary"`.

---

## How to Decide — Contrast Matters

When choices differ in criticality, the colors MUST reflect that contrast:

**High contrast** — choices have very different consequences:
```
 "Delete my account" → destructive (red)
 "Keep my account"   → default (blue)
```

**Medium contrast** — one main action, one escape:
```
 "Subscribe"   → default (blue)
 "Not now"     → secondary (gray)
```

**Low contrast** — choices are roughly equal:
```
 "Option A" → default (blue)
 "Option B" → default (blue)
 "Skip"     → secondary (gray)
```

**Multiple tiers in one set:**
```
 "Confirm purchase"  → default (blue)     — recommended
 "Change amount"     → secondary (gray)   — neutral/back
 "Cancel order"      → destructive (red)  — loses progress
```

---

## Classification Examples

Bot asks: "Approve this document?"
```json
[
  [{"text": "✅ Approve", "callback_data": "approve"},
   {"text": "❌ Reject", "callback_data": "reject", "style": "destructive"}],
  [{"text": "⏭ Review later", "callback_data": "skip", "style": "secondary"}]
]
```

Bot asks: "Pick a plan:"
```json
[
  [{"text": "Free Plan", "callback_data": "free"},
   {"text": "Pro Plan", "callback_data": "pro"}],
  [{"text": "Compare plans", "callback_data": "compare", "style": "secondary"}]
]
```
(Equal choices = both default; info link = secondary)

Bot asks: "Delete all messages in this chat?"
```json
[
  [{"text": "🗑 Delete all", "callback_data": "delete_all", "style": "destructive"}],
  [{"text": "Keep messages", "callback_data": "keep"}]
]
```
(Destructive action is red; safe action is the default blue)

Bot asks: "Transfer 500 tokens to @user?"
```json
[
  [{"text": "Send 500 tokens", "callback_data": "send", "style": "destructive"},
   {"text": "Cancel", "callback_data": "cancel", "style": "secondary"}]
]
```
(Spending = destructive since it costs something; cancel = secondary)

---

## Implementation — Python Auto-Classifier

The bot MUST use a classifier function to determine style. Here is the reference implementation:

```python
import re

# Keywords that signal each tier (case-insensitive, matched against button text + callback_data)
DESTRUCTIVE_SIGNALS = [
    r"\bdelete\b", r"\bremove\b", r"\bban\b", r"\bblock\b",
    r"\breject\b", r"\bdecline\b", r"\brevoke\b", r"\bterminate\b",
    r"\bcancel order\b", r"\bcancel subscription\b",
    r"\bunsubscribe\b", r"\bdestroy\b", r"\bpurge\b",
    r"\bspend\b", r"\btransfer\b", r"\bpay\b", r"\bsend.*tokens?\b",
    r"\breset\b", r"\bclear all\b", r"\bwipe\b",
    r"\bleave\b", r"\bquit\b", r"\bdisconnect\b",
]

SECONDARY_SIGNALS = [
    r"\bskip\b", r"\bnot now\b", r"\bmaybe later\b", r"\blater\b",
    r"\bback\b", r"\bdismiss\b", r"\bclose\b",
    r"\bdetails\b", r"\bmore info\b", r"\bhelp\b", r"\babout\b",
    r"\bno thanks\b", r"\bnevermind\b",
    r"\bcancel$",  # plain "cancel" (no lost work) = secondary, not destructive
]


def classify_button_style(text: str, callback_data: str = "", context_hint: str = "") -> str | None:
    """
    Automatically determine the button style based on its text and context.

    Returns:
        "destructive" — red button (irreversible / high-stakes)
        "secondary"   — gray button (low-priority / dismiss)
        None          — default blue button (primary / recommended)

    context_hint: optional extra context like "this action costs money"
    """
    combined = f"{text} {callback_data} {context_hint}".lower()

    # Check destructive first (higher priority)
    for pattern in DESTRUCTIVE_SIGNALS:
        if re.search(pattern, combined):
            return "destructive"

    # Then secondary
    for pattern in SECONDARY_SIGNALS:
        if re.search(pattern, combined):
            return "secondary"

    # Default = primary (blue)
    return None


def build_choice_buttons(choices: list[dict]) -> list[list[dict]]:
    """
    Takes a list of raw choices and returns Bot API inline_keyboard rows
    with styles automatically assigned.

    Each choice dict:
        text (str):          Button label (required)
        data (str):          callback_data (required unless url is set)
        url (str):           URL button (optional, mutually exclusive with data)
        style (str|None):    Override style — if set, skip auto-classification
        context (str):       Extra hint for classifier (e.g. "costs money")
        emoji_id (str):      Custom emoji ID (optional)
        row (int):           Force button into a specific row (optional)

    Returns list of rows suitable for inline_keyboard.
    """
    # Group by row
    row_map: dict[int, list[dict]] = {}
    auto_row = 0
    for i, choice in enumerate(choices):
        btn: dict = {"text": choice["text"]}

        # Action
        if "url" in choice:
            btn["url"] = choice["url"]
        else:
            btn["callback_data"] = choice.get("data", choice["text"].lower().replace(" ", "_"))

        # Style — use override if provided, else auto-classify
        if "style" in choice and choice["style"] is not None:
            btn["style"] = choice["style"]
        else:
            auto_style = classify_button_style(
                choice["text"],
                choice.get("data", ""),
                choice.get("context", ""),
            )
            if auto_style:
                btn["style"] = auto_style

        # Custom emoji
        if "emoji_id" in choice:
            btn["icon_custom_emoji_id"] = choice["emoji_id"]

        # Row assignment
        target_row = choice.get("row", auto_row)
        row_map.setdefault(target_row, []).append(btn)

        # Auto-advance row every 2 buttons
        if len(row_map.get(auto_row, [])) >= 2:
            auto_row += 1

    return [row_map[k] for k in sorted(row_map.keys())]
```

### Using the classifier in the bot:

```python
import requests

def send_choices(bot_token, chat_id, text, choices, parse_mode="HTML"):
    """Send a message with auto-colored choice buttons."""
    keyboard = build_choice_buttons(choices)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "reply_markup": {"inline_keyboard": keyboard},
    }
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()

# The bot just passes raw choices — colors are assigned automatically:
send_choices(TOKEN, chat_id, "Approve this document?", [
    {"text": "✅ Approve", "data": "approve"},
    {"text": "❌ Reject", "data": "reject"},          # auto → destructive (red)
    {"text": "⏭ Review later", "data": "later"},       # auto → secondary (gray)
])
```

---

## Usage with python-telegram-bot library

> If the library version does not yet expose `style`, pass it via `api_kwargs`.

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def auto_button(text, callback_data, context=""):
    style = classify_button_style(text, callback_data, context)
    kwargs = {"style": style} if style else {}
    return InlineKeyboardButton(text, callback_data=callback_data, api_kwargs=kwargs)

keyboard = InlineKeyboardMarkup([
    [auto_button("Approve", "approve"),
     auto_button("Reject", "reject")],
    [auto_button("Skip", "skip")],
])
await update.message.reply_text("Pick an option:", reply_markup=keyboard)
```

---

## Reply Keyboard — Same Rules Apply

```json
{
  "chat_id": "<CHAT_ID>",
  "text": "Delete your data?",
  "reply_markup": {
    "keyboard": [
      [
        {"text": "Keep my data"},
        {"text": "Delete everything", "style": "destructive"}
      ]
    ],
    "resize_keyboard": true,
    "one_time_keyboard": true
  }
}
```

---

## Custom Emoji on Buttons

Can be combined with `style` on the same button:

```json
{"text": "Boost", "callback_data": "boost", "style": "destructive", "icon_custom_emoji_id": "5368324170671202286"}
```

---

## Shell Helper

Quick test with colored buttons:

```bash
./SKILL.sh <BOT_TOKEN> <CHAT_ID>
```

## References
- Telegram Bot API: https://core.telegram.org/bots/api
- Bot API Changelog: https://core.telegram.org/bots/api-changelog
- Telegram Blog Announcement: https://telegram.org/blog/crafting-android-design-and-more
