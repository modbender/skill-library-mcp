# Telegram Bot Setup

## Create a Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "My Trading Signals")
4. Choose a username (must end in `bot`, e.g., `my_trading_signals_bot`)
5. Copy the token: `123456789:ABCdefGHI...`

## Get Your Chat ID

1. Search for `@userinfobot` on Telegram
2. Send `/start`
3. It replies with your user ID (e.g., `6894324574`)

## For Group Chats

1. Add your bot to the group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find the `chat.id` (negative number for groups)

## Test It

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "text=Test signal 🚀" \
  -d "parse_mode=HTML"
```

## Config

Set in `config.py`:
```python
TG_BOT_TOKEN = "123456789:ABCdefGHI..."
TG_CHAT_ID = "6894324574"
```

Or via environment variables:
```bash
export TG_BOT_TOKEN="123456789:ABCdefGHI..."
export TG_CHAT_ID="6894324574"
```
