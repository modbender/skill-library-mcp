# ClawMeter — Cost Tracking Dashboard

**Track OpenClaw API usage and spending in real-time with budget alerts.**

---

## Overview

ClawMeter is a self-hosted cost tracking dashboard that monitors your OpenClaw session logs, calculates token usage and API costs, and provides real-time analytics with customizable budget alerts.

**Perfect for:**
- Users who want visibility into their AI spending
- Teams managing OpenClaw deployments with budgets
- Developers optimizing model selection based on cost
- Anyone who wants to avoid surprise API bills

---

## Installation

### Prerequisites

- OpenClaw installed and running
- Node.js v18+ (for the dashboard server)
- Session logs enabled in OpenClaw (default)

### Setup

1. **Clone or download ClawMeter:**
   ```bash
   cd ~/.openclaw/workspace
   git clone https://github.com/yourusername/clawmeter.git
   cd clawmeter
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure (optional):**
   ```bash
   cp .env.example .env
   # Edit .env to customize paths, budget limits, or alert settings
   ```

4. **Ingest existing logs:**
   ```bash
   npm run ingest
   ```

5. **Start the dashboard:**
   ```bash
   npm start
   ```

6. **Open dashboard:**
   Navigate to http://localhost:3377

---

## Commands

When this skill is installed, your OpenClaw agent can respond to:

### Spending Queries

- **"How much have I spent today?"**
  - Shows today's total spend and budget percentage

- **"What's my monthly spend?"**
  - Displays current month total and budget status

- **"Show me this week's costs"**
  - Summarizes last 7 days of spending

### Cost Analysis

- **"Which model is most expensive?"**
  - Breaks down costs by model (Claude, GPT, Gemini, etc.)

- **"Show my most expensive sessions"**
  - Lists top sessions by total cost

- **"What's my average daily spend?"**
  - Calculates mean daily cost over the last 30 days

### Dashboard & Reports

- **"Open my cost dashboard"**
  - Provides link to http://localhost:3377

- **"Generate a cost report"**
  - Exports summary data (today/week/month/all-time)

### Data Management

- **"Refresh cost data"**
  - Triggers manual re-ingest of session logs

- **"Clear old cost data"**
  - (Optional) Archive or delete data older than X days

---

## API Endpoints

ClawMeter exposes a REST API that agents can query:

### Summary Statistics

```bash
GET http://localhost:3377/api/summary
```

**Response:**
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

### Daily Breakdown

```bash
GET http://localhost:3377/api/daily?days=30
```

**Response:**
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

### Sessions

```bash
GET http://localhost:3377/api/sessions?limit=50&offset=0
```

**Response:**
```json
[
  {
    "id": "abc123",
    "agent": "main",
    "model": "claude-sonnet-4-5",
    "total_cost": 0.842,
    "message_count": 12
  }
]
```

### Model Breakdown

```bash
GET http://localhost:3377/api/models
```

**Response:**
```json
[
  {
    "model": "claude-sonnet-4-5",
    "provider": "anthropic",
    "total_cost": 45.62,
    "message_count": 324
  }
]
```

### Top Sessions

```bash
GET http://localhost:3377/api/top-sessions?limit=10
```

### Budget Alerts

```bash
GET http://localhost:3377/api/alerts
```

### Manual Ingest

```bash
POST http://localhost:3377/api/ingest
```

---

## Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# Paths
OPENCLAW_AGENTS_DIR=/home/youruser/.openclaw/agents
CLAWMETER_DB=/home/youruser/.openclaw/workspace/clawmeter/data/clawmeter.db

# Server
PORT=3377

# Budgets (USD)
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

### Budget Alerts

ClawMeter automatically checks spending against configured thresholds and sends alerts via:

- **Telegram** — Instant notifications to your phone
- **Email** — Delivered via SMTP

**Alert triggers:**
- Daily spend exceeds `BUDGET_DAILY_LIMIT`
- Monthly spend exceeds `BUDGET_MONTHLY_LIMIT`

**Alert throttling:** One alert per type per day (prevents spam).

---

## Agent Integration Examples

### Example 1: Daily Spend Check

**User:** "How much have I spent today?"

**Agent Response:**
```
Let me check your spending...

📊 Today's Spend: $2.15
Budget: $5.00 (43% used)

You have $2.85 remaining today.
```

**Implementation:**
```javascript
const res = await fetch('http://localhost:3377/api/summary');
const data = await res.json();
const pct = (data.today / data.budgetDaily * 100).toFixed(0);
return `📊 Today's Spend: $${data.today.toFixed(2)}\nBudget: $${data.budgetDaily.toFixed(2)} (${pct}% used)\n\nYou have $${(data.budgetDaily - data.today).toFixed(2)} remaining today.`;
```

### Example 2: Model Comparison

**User:** "Which model should I use to save money?"

**Agent Response:**
```
Based on your usage history:

💰 Cost per 1K messages:
• Claude Haiku 3-5: $0.12
• GPT-4o-mini: $0.18
• Claude Sonnet 4-5: $0.45
• Claude Opus 4: $1.23

Recommendation: Use Haiku for simple tasks, Sonnet for complex work.
```

### Example 3: Budget Warning

**Agent (proactive):**
```
⚠️ Budget Alert

You've spent $5.52 today, exceeding your $5.00 daily limit.

Top sessions today:
1. Code review task — $2.10
2. Research project — $1.85
3. Email drafting — $0.98

Consider switching to a cheaper model or pausing non-urgent tasks.
```

---

## Dashboard Features

### Overview Screen

- **Today's spend** with budget progress bar
- **Weekly and monthly totals**
- **All-time spending** and message count
- **Budget status** (green/yellow/red indicators)

### Analytics

- **Daily cost chart** (bar chart, 7/14/30/90 day views)
- **Model breakdown** (donut chart with percentages)
- **Top sessions** by cost
- **Recent activity** feed

### Alerts History

- View all triggered budget alerts
- See when and why alerts fired
- Track spending patterns over time

---

## Use Cases

### 1. Personal Budget Management

**Scenario:** You want to keep OpenClaw costs under $100/month.

**Setup:**
- Set `BUDGET_MONTHLY_LIMIT=100.00`
- Enable Telegram alerts
- Check dashboard weekly

**Result:** Get notified before you exceed budget, adjust usage accordingly.

### 2. Team Cost Allocation

**Scenario:** Multiple team members use shared OpenClaw instance.

**Setup:**
- ClawMeter tracks costs by agent/session
- Export data via API for reporting
- Analyze which agents/projects cost most

**Result:** Fair cost distribution, identify optimization opportunities.

### 3. Model Selection Optimization

**Scenario:** You're unsure which model to use for different tasks.

**Setup:**
- Run experiments with different models
- Compare costs in ClawMeter dashboard
- Analyze cost-per-message and cost-per-token

**Result:** Data-driven model selection, optimize for cost/quality balance.

### 4. Production Monitoring

**Scenario:** OpenClaw running in production, need cost visibility.

**Setup:**
- ClawMeter auto-ingests logs in real-time
- Set aggressive budget alerts
- Monitor dashboard for anomalies

**Result:** Catch cost spikes immediately, prevent runaway spending.

---

## Troubleshooting

### Dashboard shows $0.00

**Cause:** Session logs not found or not yet ingested.

**Fix:**
1. Verify `OPENCLAW_AGENTS_DIR` points to correct path
2. Run `npm run ingest` manually
3. Check that `.jsonl` files exist in `agents/*/sessions/`

### Auto-watch not working

**Cause:** File watcher not detecting changes.

**Fix:**
1. Ensure server is running (`npm start`)
2. Check terminal for `📥 X new events` messages
3. Verify file permissions on session directories

### Budget alerts not sending

**Cause:** Missing or incorrect credentials.

**Fix:**
1. Double-check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
2. For email, verify SMTP settings
3. Check server logs for error messages

### Database errors

**Cause:** Corrupted or locked database file.

**Fix:**
1. Stop the server
2. Backup `data/clawmeter.db`
3. Delete database and re-run `npm run ingest`

---

## Advanced Configuration

### Custom Model Pricing

If you use custom models or pricing changes:

1. Edit `src/pricing.mjs`
2. Add entry to `MODEL_PRICING` object:
   ```javascript
   'your-custom-model': {
     input: 2.50,    // per million tokens
     output: 10.00,  // per million tokens
     cacheRead: 0.25,   // optional
     cacheWrite: 3.75   // optional
   }
   ```
3. Restart server

### Scheduled Reports

Use cron to schedule daily/weekly reports:

```bash
# Daily summary at 9 AM
0 9 * * * curl -s http://localhost:3377/api/summary | mail -s "Daily Cost Report" you@example.com
```

### Data Export

Export raw data for external analysis:

```bash
# Export all sessions to CSV
sqlite3 data/clawmeter.db "SELECT * FROM sessions" -csv > sessions.csv
```

### Running as a Service

Create systemd service for persistent operation:

```ini
# /etc/systemd/system/clawmeter.service
[Unit]
Description=ClawMeter Cost Tracking Dashboard
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/.openclaw/workspace/clawmeter
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable clawmeter
sudo systemctl start clawmeter
```

---

## Security Considerations

### Local Access Only

By default, ClawMeter binds to `localhost:3377` and is **not exposed to the internet**.

To access remotely, use SSH tunneling:
```bash
ssh -L 3377:localhost:3377 your-server
```

### Sensitive Data

Session logs may contain conversation data. ClawMeter:
- Stores only usage metadata (tokens, costs, timestamps)
- Does **not** store message content or prompts
- Database is local SQLite (no cloud sync)

### API Authentication

ClawMeter currently has **no authentication**. For production:

1. Run behind a reverse proxy (nginx/caddy) with auth
2. Use firewall rules to restrict access
3. Deploy on a private network

---

## Performance

### Resource Usage

- **CPU:** Minimal (event-driven ingestion)
- **RAM:** ~50-100 MB
- **Disk:** Database grows ~1 KB per message (SQLite is very efficient)
- **Network:** None (all local)

### Scalability

ClawMeter handles:
- **100K+ messages** easily
- **Years of historical data** without performance degradation
- **Multiple agents** (separated by directory structure)

For massive deployments (millions of messages), consider:
- Periodic database archiving
- PostgreSQL backend (requires code changes)

---

## Roadmap

Planned features:

- [ ] Multi-user authentication
- [ ] PostgreSQL support for large deployments
- [ ] Export to CSV/JSON
- [ ] Cost forecasting (predict monthly spend)
- [ ] Slack/Discord webhook support
- [ ] Token usage heatmaps
- [ ] Model performance tracking (latency, quality)
- [ ] Budget recommendations based on usage patterns

---

## Support

- **Documentation:** [GitHub README](https://github.com/yourusername/clawmeter)
- **Issues:** [GitHub Issues](https://github.com/yourusername/clawmeter/issues)
- **Community:** [OpenClaw Discord](https://discord.gg/openclaw)

---

## License

MIT — Free and open source forever.

---

**Made with ⚡ by the OpenClaw community**

_Track your spending. Optimize your costs. Stay in control._
