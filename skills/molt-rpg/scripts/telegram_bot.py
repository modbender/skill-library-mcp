"""
MoltRPG Telegram Bot v22
=========================
"""

import os
import json
import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Game imports
from engine import MoltRPG, pvp_system
from wallet import wallet, get_balance, create_player
from raid_oracle import RaidOracle

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GROUP_CHAT_ID = os.environ.get("MOLT_GROUP_ID", "-1003837189434")

class GameBrain:
    def recall(self, **kwargs): return []
    def remember(self, **kwargs): pass

# === Commands ===

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to MOLT RPG!\n\n"
        "Commands:\n"
        "/stats - Your player stats\n"
        "/leaderboard - Top players\n"
        "/play - Start a raid\n"
        "/challenge @player - Challenge to PVP\n\n"
        "Visit: https://molt-rpg-web.vercel.app"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    player_id = user.username or f"user_{user.id}"
    
    balance = get_balance(player_id)
    if balance == 0:
        create_player(player_id)
        balance = 10
    
    level = min(20, max(1, int(balance / 50) + 1))
    wins = random.randint(0, int(balance / 10))
    losses = random.randint(0, int(balance / 15))
    
    await update.message.reply_text(
        f"Player: {player_id}\n"
        f"Level: {level}\n"
        f"Credits: {balance}\n"
        f"Wins: {wins}\n"
        f"Losses: {losses}"
    )

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_players = list(wallet.wallets.items())
    sorted_players = sorted(all_players, key=lambda x: x[1], reverse=True)[:10]
    
    if not sorted_players:
        await update.message.reply_text("No players yet!")
        return
    
    text = "MOLT RPG Leaderboard\n" + "="*20 + "\n\n"
    for i, (name, balance) in enumerate(sorted_players, 1):
        level = min(20, max(1, int(balance / 50) + 1))
        text += f"{i}. {name} - Lv.{level} ({balance} credits)\n"
    
    await update.message.reply_text(text)

async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    player_id = user.username or f"user_{user.id}"
    
    if get_balance(player_id) == 0:
        create_player(player_id)
    
    oracle = RaidOracle()
    raids = oracle.run()
    raid = raids[0]
    
    rpg = MoltRPG(player_id, GameBrain())
    rpg._load_stats()
    
    success = rpg.fight(raid)
    
    if success:
        reward = raid['reward_usdc']
        wallet.wallets[player_id] = wallet.wallets.get(player_id, 0) + reward
        wallet.save()
        msg = f"VICTORY! You defeated {raid['name']} and earned {reward} credits!"
    else:
        msg = f"DEFEAT! {raid['name']} was too strong..."
    
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "MOLT RPG Commands:\n\n"
        "/start - Welcome\n"
        "/stats - View stats\n"
        "/leaderboard - Top players\n"
        "/play - Start a raid\n"
        "/challenge @player - PVP challenge\n"
        "/help - This help\n\n"
        "More at: https://molt-rpg-web.vercel.app"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user = update.message.from_user
    
    if any(word in text for word in ["hello", "hi", "hey"]):
        await update.message.reply_text(f"Hey {user.first_name}! Type /help for commands!")

# === Main ===

def main():
    if not BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("MOLT RPG Bot starting as @MoltRPG_Bot...")
    print("Commands: /stats, /leaderboard, /play, /challenge")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
