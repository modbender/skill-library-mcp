# Telegram Casino Bot Template

Full Python bot using `python-telegram-bot` that connects to Agent Casino API.

## Requirements

```
pip install python-telegram-bot requests
```

## Environment Variables

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AGENT_CASINO_API_KEY=your_api_key
AGENT_CASINO_AGENT_ID=your_agent_id
```

## Full Bot Code

```python
#!/usr/bin/env python3
"""Telegram Casino Bot - Agent Casino API Integration"""

import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

API_BASE = "https://agent.rollhub.com/api/v1"
API_KEY = os.environ["AGENT_CASINO_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# --- Registration (run once) ---
def register_agent(name: str) -> dict:
    resp = requests.post(f"{API_BASE}/register", json={"name": name, "ref": "ref_27fcab61"})
    return resp.json()

# --- API Helpers ---
def place_bet(game: str, amount: float, **kwargs) -> dict:
    payload = {"game": game, "amount": amount, **kwargs}
    resp = requests.post(f"{API_BASE}/bet", headers=HEADERS, json=payload)
    return resp.json()

def get_balance() -> dict:
    resp = requests.get(f"{API_BASE}/balance", headers=HEADERS)
    return resp.json()

def get_history(limit: int = 10) -> dict:
    resp = requests.get(f"{API_BASE}/history?limit={limit}", headers=HEADERS)
    return resp.json()

def verify_bet(bet_id: str) -> dict:
    resp = requests.get(f"{API_BASE}/verify/{bet_id}", headers=HEADERS)
    return resp.json()

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🪙 Coinflip 100", callback_data="coinflip_100"),
         InlineKeyboardButton("🪙 Coinflip 500", callback_data="coinflip_500")],
        [InlineKeyboardButton("🎲 Dice 100", callback_data="dice_100"),
         InlineKeyboardButton("🎲 Dice 500", callback_data="dice_500")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("📜 History", callback_data="history")]
    ]
    await update.message.reply_text(
        "🎰 *Agent Casino Bot*\n\nChoose a game or use commands:\n"
        "/bet <amount> <game>\n/coinflip <amount>\n/dice <amount>\n"
        "/balance\n/history\n/autoplay <game> <amount> <rounds>",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def cmd_coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = float(context.args[0]) if context.args else 100
    result = place_bet("coinflip", amount, choice="heads")
    won = result.get("won", False)
    payout = result.get("payout", 0)
    emoji = "✅" if won else "❌"
    await update.message.reply_text(
        f"{emoji} Coinflip: {'WON' if won else 'LOST'}\n"
        f"Bet: {amount} | Payout: {payout}\n"
        f"Verify: /verify_{result.get('bet_id', 'unknown')}"
    )

async def cmd_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = float(context.args[0]) if context.args else 100
    result = place_bet("dice", amount, target=50, over=True)
    won = result.get("won", False)
    roll = result.get("result", 0)
    payout = result.get("payout", 0)
    emoji = "✅" if won else "❌"
    await update.message.reply_text(
        f"{emoji} Dice Roll: {roll}\n"
        f"Bet: {amount} (over 50) | Payout: {payout}\n"
        f"Verify: /verify_{result.get('bet_id', 'unknown')}"
    )

async def cmd_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /bet <amount> <game> [choice]")
        return
    amount = float(context.args[0])
    game = context.args[1]
    kwargs = {}
    if game == "coinflip":
        kwargs["choice"] = context.args[2] if len(context.args) > 2 else "heads"
    elif game == "dice":
        kwargs["target"] = int(context.args[2]) if len(context.args) > 2 else 50
        kwargs["over"] = True
    result = place_bet(game, amount, **kwargs)
    won = result.get("won", False)
    await update.message.reply_text(
        f"{'✅ WON' if won else '❌ LOST'} | Game: {game} | Amount: {amount} | Payout: {result.get('payout', 0)}"
    )

async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = get_balance()
    await update.message.reply_text(f"💰 Balance: {bal.get('balance', 'unknown')}")

async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hist = get_history()
    bets = hist.get("bets", [])
    if not bets:
        await update.message.reply_text("No bet history.")
        return
    lines = []
    for b in bets[:10]:
        emoji = "✅" if b.get("won") else "❌"
        lines.append(f"{emoji} {b.get('game')} | {b.get('amount')} → {b.get('payout', 0)}")
    await update.message.reply_text("📜 Recent Bets:\n" + "\n".join(lines))

async def cmd_autoplay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /autoplay <game> <amount> <rounds>")
        return
    game, amount, rounds = context.args[0], float(context.args[1]), int(context.args[2])
    await update.message.reply_text(f"🤖 Auto-playing {rounds} rounds of {game} at {amount} each...")
    wins, losses, total_payout = 0, 0, 0
    for i in range(rounds):
        kwargs = {"choice": "heads"} if game == "coinflip" else {"target": 50, "over": True}
        result = place_bet(game, amount, **kwargs)
        if result.get("won"):
            wins += 1
            total_payout += result.get("payout", 0)
        else:
            losses += 1
    await update.message.reply_text(
        f"🏁 Auto-play complete!\n"
        f"Rounds: {rounds} | Wins: {wins} | Losses: {losses}\n"
        f"Total wagered: {amount * rounds} | Total payout: {total_payout}\n"
        f"Net: {total_payout - (amount * rounds)}"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "balance":
        bal = get_balance()
        await query.edit_message_text(f"💰 Balance: {bal.get('balance', 'unknown')}")
    elif data == "history":
        hist = get_history()
        bets = hist.get("bets", [])
        text = "No history." if not bets else "\n".join(
            f"{'✅' if b.get('won') else '❌'} {b.get('game')} | {b.get('amount')}" for b in bets[:5]
        )
        await query.edit_message_text(f"📜 {text}")
    elif data.startswith("coinflip_"):
        amount = float(data.split("_")[1])
        result = place_bet("coinflip", amount, choice="heads")
        won = result.get("won", False)
        await query.edit_message_text(f"{'✅ WON' if won else '❌ LOST'} Coinflip {amount} | Payout: {result.get('payout', 0)}")
    elif data.startswith("dice_"):
        amount = float(data.split("_")[1])
        result = place_bet("dice", amount, target=50, over=True)
        await query.edit_message_text(f"{'✅ WON' if won else '❌ LOST'} Dice {amount} | Roll: {result.get('result', '?')} | Payout: {result.get('payout', 0)}")

def main():
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coinflip", cmd_coinflip))
    app.add_handler(CommandHandler("dice", cmd_dice))
    app.add_handler(CommandHandler("bet", cmd_bet))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("autoplay", cmd_autoplay))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
```

## Deployment

1. Create bot via @BotFather on Telegram
2. Set environment variables
3. Run: `python telegram_bot.py`
4. For production: use systemd, Docker, or a cloud function
