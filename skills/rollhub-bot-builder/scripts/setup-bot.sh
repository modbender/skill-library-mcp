#!/bin/bash
# Quick setup helper for Agent Casino bots
# Usage: bash setup-bot.sh <platform>
# Platforms: telegram, discord, twitter

set -e
PLATFORM="${1:-telegram}"
echo "🎰 Agent Casino Bot Setup — $PLATFORM"
echo "API: https://agent.rollhub.com/api/v1"
echo ""

# Register agent
read -p "Bot name: " BOT_NAME
echo "Registering agent..."
RESPONSE=$(curl -s -X POST https://agent.rollhub.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$BOT_NAME\", \"ref\": \"ref_27fcab61\"}")
echo "Registration response: $RESPONSE"
echo ""

case "$PLATFORM" in
  telegram)
    echo "📱 Telegram Bot Setup"
    echo "1. Talk to @BotFather on Telegram"
    echo "2. Create new bot, get token"
    echo "3. Set environment variables:"
    echo "   export TELEGRAM_BOT_TOKEN=your_token"
    echo "   export AGENT_CASINO_API_KEY=your_key"
    echo "4. pip install python-telegram-bot requests"
    echo "5. Copy the bot code from references/telegram-bot.md"
    echo "6. Run: python telegram_bot.py"
    ;;
  discord)
    echo "🎮 Discord Bot Setup"
    echo "1. Go to discord.com/developers/applications"
    echo "2. Create app, add bot, get token"
    echo "3. Set environment variables:"
    echo "   export DISCORD_BOT_TOKEN=your_token"
    echo "   export AGENT_CASINO_API_KEY=your_key"
    echo "4. npm install discord.js axios"
    echo "5. Copy the bot code from references/discord-bot.md"
    echo "6. Run: node discord-casino-bot.js"
    ;;
  twitter)
    echo "🐦 Twitter Bot Setup"
    echo "1. Apply for Twitter Developer access"
    echo "2. Create app, get API keys"
    echo "3. Set environment variables:"
    echo "   export TWITTER_API_KEY=your_key"
    echo "   export TWITTER_API_SECRET=your_secret"
    echo "   export TWITTER_ACCESS_TOKEN=your_token"
    echo "   export TWITTER_ACCESS_SECRET=your_secret"
    echo "   export AGENT_CASINO_API_KEY=your_key"
    echo "4. pip install tweepy requests"
    echo "5. Copy the bot code from references/twitter-bot.md"
    echo "6. Run: python twitter_bot.py auto"
    ;;
  *)
    echo "Unknown platform: $PLATFORM"
    echo "Use: telegram, discord, or twitter"
    exit 1
    ;;
esac
echo ""
echo "✅ Done! Visit https://agent.rollhub.com for API docs."
