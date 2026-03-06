# WhatsApp Analyzer

Automatically detect appointments and urgent messages from WhatsApp → Alert via Telegram → Add to Google Calendar.

## Quick Start

```bash
chmod +x setup.sh
./setup.sh
```

That's it! Just enter your Telegram Chat ID and scan the QR code.

## Features

- 📅 **RDV Detection**: "Meeting demain 14h" → Telegram alert + Calendar option
- 🚨 **Urgent Detection**: "C'est urgent!" → Telegram alert
- 🤖 **Fully Automated**: Auto-starts on boot, no maintenance needed
- 🔒 **Private**: All data stored locally

## Requirements

- Docker
- Node.js
- OpenClaw with Telegram channel
- `gog` CLI for Google Calendar (optional)

## How It Works

```
WhatsApp → WAHA (Docker) → Webhook → messages.jsonl
                                         ↓
                              OpenClaw cron (60s)
                                         ↓
                              RDV? → Telegram "Add to calendar?"
                                         ↓
                              User: "Oui" → Google Calendar ✅
```

## License

MIT
