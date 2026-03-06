#!/usr/bin/env bash
# Openclaw AI Bot — Project Setup Script
# Scaffolds a Python bot project with colored button helpers.
#
# Usage:
#   bash scripts/setup_openclaw_bot.sh [project_dir]
#
# Default project_dir: ./openclaw-bot

set -euo pipefail

PROJECT_DIR="${1:-openclaw-bot}"

echo "==> Setting up Openclaw bot project in ${PROJECT_DIR}/..."
mkdir -p "$PROJECT_DIR"

# --- .env template ---
cat > "$PROJECT_DIR/.env" << 'EOF'
# Openclaw Bot Configuration
BOT_TOKEN=your-bot-token-from-botfather
# Optional: default chat ID for testing
CHAT_ID=
EOF

# --- requirements.txt ---
cat > "$PROJECT_DIR/requirements.txt" << 'EOF'
requests>=2.28.0
python-dotenv>=1.0.0
EOF

# --- Main bot module ---
cat > "$PROJECT_DIR/bot.py" << 'PYEOF'
"""
Openclaw AI Bot — Colored Buttons Module

Sends Telegram messages with colored inline/reply keyboard buttons
using the Bot API 'style' and 'icon_custom_emoji_id' fields.

Styles:
  - (omit)        → Default accent/blue (primary action)
  - "destructive" → Red (dangerous/delete actions)
  - "secondary"   → Gray/muted (cancel, dismiss, neutral)

Usage:
    from bot import OpenclawBot

    bot = OpenclawBot("YOUR_BOT_TOKEN")
    bot.send_choice(
        chat_id="123456",
        text="Pick one:",
        choices=[
            {"text": "Yes", "data": "yes"},
            {"text": "No",  "data": "no", "style": "destructive"},
            {"text": "Skip","data": "skip", "style": "secondary"},
        ],
    )
"""

import os
import json
import requests
from typing import Optional


class OpenclawBot:
    """Telegram bot client with colored button support."""

    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("BOT_TOKEN", "")
        if not self.token:
            raise ValueError("BOT_TOKEN is required (pass to constructor or set env var)")
        self.api_url = self.API_BASE.format(token=self.token)

    def _post(self, method: str, payload: dict) -> dict:
        """Send a request to the Bot API."""
        resp = requests.post(f"{self.api_url}/{method}", json=payload)
        resp.raise_for_status()
        result = resp.json()
        if not result.get("ok"):
            raise RuntimeError(f"Bot API error: {result}")
        return result

    # ── Inline Keyboard (buttons attached to message) ──

    def send_inline_buttons(
        self,
        chat_id: str,
        text: str,
        buttons: list[list[dict]],
        parse_mode: Optional[str] = None,
    ) -> dict:
        """
        Send a message with an inline keyboard.

        buttons: list of rows, each row is a list of button dicts.
        Each button dict must have 'text' and one of:
          'callback_data', 'url', 'switch_inline_query', etc.
        Optional: 'style' ("destructive" | "secondary"), 'icon_custom_emoji_id'.
        """
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {"inline_keyboard": buttons},
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        return self._post("sendMessage", payload)

    def send_choice(
        self,
        chat_id: str,
        text: str,
        choices: list[dict],
        columns: int = 2,
        parse_mode: Optional[str] = None,
    ) -> dict:
        """
        Send a message with choice buttons, auto-arranged into rows.

        choices: list of dicts with keys:
          - text (str): button label
          - data (str): callback_data value
          - style (str, optional): "destructive" or "secondary"
          - emoji_id (str, optional): custom emoji ID
          - url (str, optional): URL instead of callback_data

        columns: max buttons per row (default 2)
        """
        rows = []
        current_row = []
        for choice in choices:
            btn = {"text": choice["text"]}
            if "url" in choice:
                btn["url"] = choice["url"]
            else:
                btn["callback_data"] = choice.get("data", choice["text"].lower())
            if "style" in choice:
                btn["style"] = choice["style"]
            if "emoji_id" in choice:
                btn["icon_custom_emoji_id"] = choice["emoji_id"]
            current_row.append(btn)
            if len(current_row) >= columns:
                rows.append(current_row)
                current_row = []
        if current_row:
            rows.append(current_row)
        return self.send_inline_buttons(chat_id, text, rows, parse_mode=parse_mode)

    # ── Reply Keyboard (buttons replace device keyboard) ──

    def send_reply_keyboard(
        self,
        chat_id: str,
        text: str,
        buttons: list[list[dict]],
        resize: bool = True,
        one_time: bool = True,
        parse_mode: Optional[str] = None,
    ) -> dict:
        """
        Send a message with a reply keyboard.

        buttons: list of rows, each row is a list of button dicts.
        Each button dict must have 'text'.
        Optional: 'style' ("destructive" | "secondary"), 'icon_custom_emoji_id'.
        """
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "keyboard": buttons,
                "resize_keyboard": resize,
                "one_time_keyboard": one_time,
            },
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        return self._post("sendMessage", payload)


# ── Quick demo when run directly ──

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    bot = OpenclawBot()
    chat_id = os.environ.get("CHAT_ID", "")
    if not chat_id:
        chat_id = input("Enter chat ID: ").strip()

    print("Sending colored inline buttons...")
    bot.send_choice(
        chat_id=chat_id,
        text="🎨 <b>Openclaw Colored Buttons</b>\n\nChoose an action:",
        choices=[
            {"text": "✅ Approve", "data": "approve"},
            {"text": "❌ Reject", "data": "reject", "style": "destructive"},
            {"text": "⏭ Skip", "data": "skip", "style": "secondary"},
            {"text": "📖 Docs", "url": "https://core.telegram.org/bots/api"},
        ],
        columns=2,
        parse_mode="HTML",
    )
    print("✅ Done! Check your Telegram chat.")
PYEOF

echo "==> Created ${PROJECT_DIR}/bot.py"
echo "==> Created ${PROJECT_DIR}/.env"
echo "==> Created ${PROJECT_DIR}/requirements.txt"
echo ""
echo "Next steps:"
echo "  1. cd ${PROJECT_DIR}"
echo "  2. Edit .env and set your BOT_TOKEN"
echo "  3. pip install -r requirements.txt"
echo "  4. python bot.py"
echo ""
echo "✅ Openclaw bot project ready!"
