# AI Bill Intelligence (v2.2.0)

Real-time AI spending dashboard for OpenClaw. Track 12+ AI providers including OpenAI, Claude, Gemini, DeepSeek, Kimi, Groq, xAI, MiniMax, Mistral, Qwen, GLM, and Llama.

![AI Bill Dashboard](https://raw.githubusercontent.com/fumabot16-max/bill-project/master/public/screenshot.png)

## 🚀 Quick Install

Run this command in your OpenClaw terminal:

```bash
openclaw skill install https://github.com/fumabot16-max/bill-project
```

## ✨ New in v2.2.0
- **Metadata Fixes:** Resolved mismatches and missing declarations for ClawHub security scans.
- **Author Sync:** Updated author name to match ClawHub profile (@fumarole16-afk).
- **12+ AI Brands Support:** Now tracks almost every major AI provider.
- **Interactive Settings:** Easily switch between **Prepaid**, **Postpaid**, **Subscribe**, and **Off** modes.
- **Smart Balance Sync:** Real-time editing of remaining credits with auto-save.
- **Zero-Password UI:** Immediate access to your billing data without tedious logins.
- **Accurate Archiving:** Solved overcounting bugs by using session-end archiving logic.

## 🛠 Setup

1. **Install the skill** using the command above.
2. **Access the dashboard** at `http://your-vps-ip:8003` (or your configured domain).
3. **Click the Gear Icon (⚙️)** in the top right corner.
4. **Enter your initial balances** and select the payment mode for each provider.
5. **Save Changes** and watch your real-time spending!

## 📊 Monitoring

The system automatically runs a background collector (`collector.js`) that:
- Scans active sessions for token usage.
- Matches models with their respective pricing in `prices.json`.
- Archives costs when sessions expire to ensure zero data loss and 100% accuracy.

## Credits
Built with 🐱 by **Tiger Jung** & **Chloe**.
Dedicated to keeping your AI costs under control.
