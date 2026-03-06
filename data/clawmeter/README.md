# 🔥 ClawMeter — Cost Tracking Dashboard for OpenClaw

**Stop burning money blind.** ClawMeter is a self-hosted cost tracking dashboard that parses your OpenClaw session logs, calculates token usage and API costs per session/model, and provides real-time monitoring with budget alerts.

**Solves:** [GitHub Issue #12299](https://github.com/openclaw/openclaw/issues/12299) — OpenClaw users need visibility into their API spending.

![Dashboard Preview](docs/screenshot-dashboard.png)

---

## ✨ Features

- **📊 Real-time Dashboard** — Beautiful, responsive UI showing daily/weekly/monthly spend
- **💰 Accurate Cost Calculation** — Built-in pricing database for Anthropic, OpenAI, Google, DeepSeek
- **🔔 Budget Alerts** — Telegram and email notifications when you exceed daily/monthly thresholds
- **📈 Detailed Analytics** — Cost breakdown by model, session, and time period
- **🗄️ SQLite Storage** — Simple, portable, self-hosted — no cloud dependencies
- **🔄 Auto-Ingestion** — Watches your session logs and ingests new data automatically
- **📦 OpenClaw Skill** — Installs as a native skill for seamless integration
- **🎨 Modern UI** — Clean, dark-mode interface inspired by Linear and Vercel

---

## 🚀 Quick Start

### 1. Install

```bash
cd ~/.openclaw/workspace
git clone https://github.com/yourusername/clawmeter.git
cd clawmeter
npm install
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` to set your OpenClaw agents directory (defaults to `~/.openclaw/agents`):

```bash
OPENCLAW_AGENTS_DIR=/home/youruser/.openclaw/agents
CLAWMETER_DB=/home/youruser/.openclaw/workspace/clawmeter/data/clawmeter.db
PORT=3377

# Budget thresholds (optional)
BUDGET_DAILY_LIMIT=5.00
BUDGET_MONTHLY_LIMIT=100.00

# Telegram alerts (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email alerts (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=your_app_password
ALERT_EMAIL_TO=notify@yourdomain.com
```

### 3. Ingest existing logs

```bash
npm run ingest
```

This scans all your existing OpenClaw session logs and extracts usage data.

### 4. Start the dashboard

```bash
npm start
```

Dashboard is now running at **http://localhost:3377** 🎉

---

## 📖 Usage

### Dashboard

Open http://localhost:3377 in your browser to view:

- **Today's spend** with budget progress
- **Weekly and monthly totals**
- **Daily cost chart** (last 7/14/30/90 days)
- **Cost breakdown by model** (donut chart)
- **Top sessions by cost**
- **Recent activity**
- **Budget alert history**

### CLI Commands

```bash
# Ingest all session logs
npm run ingest

# Start the dashboard server (with auto-watch)
npm start

# Development mode (with file watching)
npm run dev
```

### OpenClaw Skill Installation

To install as an OpenClaw skill (adds SKILL.md to `~/.openclaw/skills/clawmeter/`):

```bash
./scripts/install-skill.sh
```

After installation, your agent can reference ClawMeter commands and API endpoints.

---

## 🏗️ Architecture

```
OpenClaw Session Logs (.jsonl)
          ↓
    Ingest Pipeline
    (parses usage from assistant messages)
          ↓
      SQLite DB
    (sessions, usage_events, daily_aggregates, alerts_log)
          ↓
     Express API
    (/api/summary, /api/daily, /api/sessions, /api/models, /api/alerts)
          ↓
   Static HTML/JS Dashboard
    (Chart.js + vanilla JS)
```

### Components

- **`src/ingest.mjs`** — Parses `.jsonl` session logs, extracts usage data
- **`src/db.mjs`** — SQLite wrapper (sql.js for portability)
- **`src/pricing.mjs`** — Model pricing database and cost calculation
- **`src/alerts.mjs`** — Budget threshold monitoring and notifications
- **`src/server.mjs`** — Express server with REST API and file watcher
- **`web/index.html`** — Single-page dashboard UI

---

## 💡 How It Works

### Session Log Parsing

ClawMeter watches your `~/.openclaw/agents/*/sessions/*.jsonl` files for changes.

When it detects new messages, it extracts:

- **Model and provider** from `session` and `model_change` events
- **Token usage** from assistant messages: `input`, `output`, `cacheRead`, `cacheWrite`
- **Timestamps** to track when usage occurred
- **Session metadata** (agent, label, started_at)

### Cost Calculation

For each usage event, ClawMeter:

1. Looks up model pricing in `src/pricing.mjs`
2. Calculates costs: `(tokens / 1M) * price_per_million`
3. Handles cache reads/writes separately (different pricing)
4. Aggregates by session, day, model, and provider

### Budget Alerts

ClawMeter checks daily and monthly spend against configured thresholds:

- Compares current totals to `BUDGET_DAILY_LIMIT` and `BUDGET_MONTHLY_LIMIT`
- Sends alerts via Telegram and/or email when exceeded
- Logs all alerts to prevent duplicate notifications

---

## 📊 API Reference

### `GET /api/summary`

Returns overall statistics:

```json
{
  "today": 2.15,
  "week": 8.42,
  "month": 32.76,
  "allTime": 127.89,
  "sessions": 234,
  "messages": 1842,
  "budgetDaily": 5.0,
  "budgetMonthly": 100.0
}
```

### `GET /api/daily?days=30`

Daily cost breakdown:

```json
[
  {
    "date": "2026-02-14",
    "cost": 2.15,
    "input_tokens": 45820,
    "output_tokens": 12340,
    "messages": 18
  }
]
```

### `GET /api/sessions?limit=50&offset=0`

List sessions:

```json
[
  {
    "id": "abc123",
    "agent": "main",
    "started_at": "2026-02-14T08:00:00Z",
    "model": "claude-sonnet-4-5",
    "provider": "anthropic",
    "total_cost": 0.842,
    "total_input_tokens": 15000,
    "total_output_tokens": 8000,
    "message_count": 12
  }
]
```

### `GET /api/models`

Cost breakdown by model:

```json
[
  {
    "model": "claude-sonnet-4-5",
    "provider": "anthropic",
    "total_cost": 45.62,
    "input_tokens": 2840000,
    "output_tokens": 890000,
    "message_count": 324
  }
]
```

### `GET /api/top-sessions?limit=10`

Most expensive sessions:

```json
[
  {
    "id": "def456",
    "agent": "main",
    "started_at": "2026-02-13T15:22:00Z",
    "model": "claude-opus-4",
    "total_cost": 12.45,
    "message_count": 28
  }
]
```

### `GET /api/alerts`

Recent budget alerts:

```json
[
  {
    "id": 1,
    "type": "daily_budget",
    "threshold": 5.0,
    "actual": 5.52,
    "message": "⚠️ Daily budget alert: $5.52 spent today (limit: $5.00)",
    "sent_at": "2026-02-14T18:30:00Z"
  }
]
```

### `POST /api/ingest`

Trigger manual re-ingest:

```json
{ "ingested": 42 }
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_AGENTS_DIR` | `~/.openclaw/agents` | Path to OpenClaw agents directory |
| `CLAWMETER_DB` | `./data/clawmeter.db` | SQLite database path |
| `PORT` | `3377` | Web server port |
| `BUDGET_DAILY_LIMIT` | `5.00` | Daily spending threshold (USD) |
| `BUDGET_MONTHLY_LIMIT` | `100.00` | Monthly spending threshold (USD) |
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token for alerts |
| `TELEGRAM_CHAT_ID` | — | Telegram chat ID for alerts |
| `SMTP_HOST` | — | SMTP server for email alerts |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USER` | — | SMTP username |
| `SMTP_PASS` | — | SMTP password |
| `ALERT_EMAIL_TO` | — | Email address for alerts |

### Model Pricing

ClawMeter maintains an up-to-date pricing database in `src/pricing.mjs`.

**Current models supported:**

- **Anthropic:** Claude Opus 4, Sonnet 4-5, Haiku 3-5, legacy models
- **OpenAI:** GPT-4o, GPT-4o-mini, o1, o3, o4-mini
- **Google:** Gemini 2.0 Flash/Pro, Gemini 1.5 Flash/Pro
- **DeepSeek:** DeepSeek Chat, DeepSeek Reasoner

**Prices are per million tokens (USD).**

To add or update pricing:

1. Edit `src/pricing.mjs`
2. Add model entries to `MODEL_PRICING` object
3. Include `input`, `output`, and optionally `cacheRead`, `cacheWrite` prices

---

## 🔔 Setting Up Alerts

### Telegram

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID (send a message to [@userinfobot](https://t.me/userinfobot))
3. Set environment variables:
   ```bash
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_CHAT_ID=987654321
   ```

### Email (SMTP)

For Gmail:

1. Enable 2FA in your Google account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Set environment variables:
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your.email@gmail.com
   SMTP_PASS=your_app_password
   ALERT_EMAIL_TO=notify@yourdomain.com
   ```

For other providers, adjust `SMTP_HOST` and `SMTP_PORT` accordingly.

---

## 🧪 Testing

### Manual Testing

1. **Run ingest:**
   ```bash
   npm run ingest
   ```
   Should output: `✅ Ingested X new usage events`

2. **Start server:**
   ```bash
   npm start
   ```
   Should show: `🔥 ClawMeter running at http://localhost:3377`

3. **Open dashboard:**
   Navigate to http://localhost:3377
   - Should display stats, charts, and tables
   - Check console for errors

4. **Test auto-watch:**
   - Keep server running
   - Have an OpenClaw session generate some messages
   - Watch terminal for `📥 X new events`
   - Refresh dashboard to see updated data

### Verification Checklist

- [ ] Ingest completes without errors
- [ ] Dashboard loads and displays data
- [ ] Charts render correctly (daily spend, model breakdown)
- [ ] Session tables populate
- [ ] Budget percentages calculate correctly
- [ ] Auto-watch detects new session logs
- [ ] Alerts trigger when thresholds exceeded (if configured)

---

## 📂 Project Structure

```
clawmeter/
├── README.md                 # This file
├── SKILL.md                  # OpenClaw skill documentation
├── LICENSE                   # MIT license
├── package.json              # NPM dependencies
├── .env.example              # Configuration template
├── scripts/
│   └── install-skill.sh      # Skill installation script
├── src/
│   ├── config.mjs            # Configuration loader
│   ├── db.mjs                # SQLite wrapper
│   ├── pricing.mjs           # Model pricing database
│   ├── ingest.mjs            # Log parsing and ingestion
│   ├── alerts.mjs            # Budget alert logic
│   └── server.mjs            # Express API + file watcher
├── web/
│   └── index.html            # Dashboard UI (single-page)
└── data/
    └── clawmeter.db          # SQLite database (created on first run)
```

---

## 🤝 Contributing

Contributions welcome! Here's how you can help:

1. **Report bugs** — Open an issue with reproduction steps
2. **Request features** — Describe your use case
3. **Add model pricing** — Submit a PR to update `src/pricing.mjs`
4. **Improve UI** — Enhance the dashboard design
5. **Write documentation** — Clarify setup or usage

### Development Workflow

```bash
# Clone the repo
git clone https://github.com/yourusername/clawmeter.git
cd clawmeter

# Install dependencies
npm install

# Make your changes
# ...

# Test locally
npm run ingest
npm start

# Submit a PR
git checkout -b feature/your-feature
git commit -m "Add: your feature"
git push origin feature/your-feature
```

---

## 🐛 Troubleshooting

### "Database not initialized" error

Make sure to run `npm run ingest` at least once before starting the server, or let the server run its initial ingest.

### Dashboard shows $0.00 everywhere

- Check that `OPENCLAW_AGENTS_DIR` points to the correct directory
- Verify that `.jsonl` session logs exist in `agents/*/sessions/`
- Run `npm run ingest` manually to force a re-scan

### Auto-watch not detecting new logs

- Ensure the server is running (`npm start`)
- Check terminal for `📥 X new events` messages
- Verify file permissions on session directories

### Budget alerts not sending

- Double-check Telegram/SMTP credentials in `.env`
- Test Telegram bot by sending a message manually
- Check server logs for alert errors

### Chart.js not loading

- Ensure you have internet connection (Chart.js loaded from CDN)
- Check browser console for JavaScript errors
- Try hard refresh (Ctrl+Shift+R)

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built for the [OpenClaw](https://github.com/openclaw/openclaw) community
- Inspired by tools like Datadog, Linear, and Vercel
- Chart.js for beautiful visualizations
- sql.js for portable SQLite in Node.js

---

## 🔗 Links

- **Documentation:** [GitHub Wiki](https://github.com/yourusername/clawmeter/wiki)
- **Issues:** [GitHub Issues](https://github.com/yourusername/clawmeter/issues)
- **ClawHub:** [Browse Skills](https://clawhub.io/)
- **OpenClaw:** [Main Repository](https://github.com/openclaw/openclaw)

---

**Made with ⚡ by the OpenClaw community**

_Track your spending. Optimize your costs. Stay in control._
