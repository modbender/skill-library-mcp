# ClawMeter Quick Start Guide

Get ClawMeter running in 5 minutes.

---

## Prerequisites

- ✅ OpenClaw installed and configured
- ✅ Node.js v18 or higher (`node --version`)
- ✅ npm installed (`npm --version`)
- ✅ OpenClaw has generated at least a few session logs

---

## Installation (5 Steps)

### Step 1: Clone or Download

```bash
cd ~/.openclaw/workspace
git clone https://github.com/yourusername/clawmeter.git
cd clawmeter
```

**Or download ZIP:**
```bash
cd ~/.openclaw/workspace
wget https://github.com/yourusername/clawmeter/archive/refs/heads/main.zip
unzip main.zip
mv clawmeter-main clawmeter
cd clawmeter
```

---

### Step 2: Install Dependencies

```bash
npm install
```

**Expected output:**
```
added 72 packages in 3s
```

---

### Step 3: Configure (Optional)

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Default configuration works out-of-the-box.** You only need to edit `.env` if:

- Your OpenClaw agents directory is in a non-standard location
- You want to set custom budget thresholds
- You want to enable Telegram or email alerts

**Minimal .env (defaults are fine):**
```bash
OPENCLAW_AGENTS_DIR=/home/youruser/.openclaw/agents
PORT=3377
```

---

### Step 4: Ingest Existing Logs

```bash
npm run ingest
```

**Expected output:**
```
✅ Ingested 109 new usage events
```

This scans all your existing OpenClaw session logs and extracts cost data.

**Troubleshooting:**

- **"Ingested 0 events"** → Check that `OPENCLAW_AGENTS_DIR` is correct and contains `.jsonl` files
- **Error reading files** → Verify file permissions

---

### Step 5: Start the Dashboard

```bash
npm start
```

**Expected output:**
```
🔄 Ingesting existing session logs...
✅ Ingested 0 new usage events
🔥 ClawMeter running at http://localhost:3377
```

**Open in your browser:**
```
http://localhost:3377
```

You should see the dashboard with your usage stats! 🎉

---

## Verification Checklist

After installation, verify:

- [ ] Dashboard loads without errors
- [ ] Stat cards show non-zero values (if you have usage)
- [ ] Daily chart renders
- [ ] Model breakdown donut chart appears
- [ ] Session tables populate
- [ ] No JavaScript errors in browser console (F12)
- [ ] Terminal shows "Watching logs" status

---

## Next Steps

### Keep Dashboard Running

**Option 1: Terminal session**
```bash
npm start
# Keep terminal open
```

**Option 2: Background process**
```bash
nohup npm start > clawmeter.log 2>&1 &
```

**Option 3: systemd service** (recommended for production)

Create `/etc/systemd/system/clawmeter.service`:
```ini
[Unit]
Description=ClawMeter Dashboard
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
sudo systemctl status clawmeter
```

---

### Set Up Budget Alerts (Optional)

#### Telegram Alerts

1. **Create a bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow prompts
   - Copy the bot token (looks like `123456:ABC-DEF...`)

2. **Get your chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot)
   - Copy your chat ID (a number like `987654321`)

3. **Add to `.env`:**
   ```bash
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_CHAT_ID=987654321
   BUDGET_DAILY_LIMIT=5.00
   BUDGET_MONTHLY_LIMIT=100.00
   ```

4. **Restart ClawMeter:**
   ```bash
   npm start
   ```

**Test:** Manually exceed your budget to trigger an alert.

#### Email Alerts (Gmail Example)

1. **Enable 2FA** on your Google account

2. **Generate app password:**
   - Go to [Google Account > Security > 2-Step Verification > App passwords](https://myaccount.google.com/apppasswords)
   - Generate a password for "Mail"
   - Copy the 16-character password

3. **Add to `.env`:**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your.email@gmail.com
   SMTP_PASS=your_16_char_app_password
   ALERT_EMAIL_TO=notify@yourdomain.com
   BUDGET_DAILY_LIMIT=5.00
   BUDGET_MONTHLY_LIMIT=100.00
   ```

4. **Restart ClawMeter**

---

### Install as OpenClaw Skill (Optional)

Make ClawMeter available as a skill for your OpenClaw agent:

```bash
./scripts/install-skill.sh
```

This creates `~/.openclaw/skills/clawmeter/SKILL.md` which your agent can reference.

---

## Common Use Cases

### Check Spending Manually

Visit http://localhost:3377 anytime to see:
- Today's spend
- This week's spend
- This month's spend
- All-time total
- Cost breakdown by model
- Most expensive sessions

### Automate Daily Reports

Add to cron:
```bash
# Daily summary at 9 AM
0 9 * * * curl -s http://localhost:3377/api/summary | \
  jq '.today, .week, .month' | \
  mail -s "ClawMeter Daily Report" you@example.com
```

### API Integration

Query from scripts or agents:

```bash
# Get today's spend
curl http://localhost:3377/api/summary | jq '.today'

# Get last 7 days breakdown
curl http://localhost:3377/api/daily?days=7 | jq '.'

# Get top 5 expensive sessions
curl http://localhost:3377/api/top-sessions?limit=5 | jq '.'
```

---

## Troubleshooting

### Dashboard Shows $0.00

**Cause:** No data ingested yet.

**Fix:**
1. Verify OpenClaw session logs exist:
   ```bash
   ls ~/.openclaw/agents/main/sessions/*.jsonl
   ```
2. Check `OPENCLAW_AGENTS_DIR` in `.env`
3. Run manual ingest:
   ```bash
   npm run ingest
   ```

---

### Port 3377 Already in Use

**Cause:** Another service is using the port.

**Fix:** Change `PORT` in `.env`:
```bash
PORT=3378
```

Restart ClawMeter:
```bash
npm start
```

Access at http://localhost:3378

---

### "Cannot find module 'sql.js'"

**Cause:** Dependencies not installed.

**Fix:**
```bash
npm install
```

---

### Charts Not Rendering

**Cause:** No internet connection (Chart.js loaded from CDN).

**Fix:** Ensure internet access or download Chart.js locally.

**Temporary workaround:**
Open browser console (F12) and check for CDN errors.

---

### Auto-Watch Not Detecting New Logs

**Cause:** File permissions or path issues.

**Fix:**
1. Verify server is running (`npm start`)
2. Check terminal for "Watching logs" message
3. Test by generating a new OpenClaw session
4. Look for `📥 X new events` in terminal

---

## Updating ClawMeter

When a new version is released:

```bash
cd ~/.openclaw/workspace/clawmeter
git pull
npm install  # Update dependencies if needed
npm start
```

**Check CHANGELOG.md** for breaking changes.

---

## Uninstalling

To remove ClawMeter:

```bash
# Stop the server (Ctrl+C or kill process)

# Remove files
rm -rf ~/.openclaw/workspace/clawmeter

# Remove skill (if installed)
rm -rf ~/.openclaw/skills/clawmeter

# Database is self-contained, so no external cleanup needed
```

---

## Getting Help

- **Documentation:** [README.md](../README.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/clawmeter/issues)
- **Community:** [OpenClaw Discord](https://discord.gg/openclaw)

---

## Pro Tips

### 1. Bookmark the Dashboard

Add http://localhost:3377 to your browser bookmarks for quick access.

### 2. Use Custom Budget Thresholds

Adjust `BUDGET_DAILY_LIMIT` and `BUDGET_MONTHLY_LIMIT` based on your actual spending patterns.

### 3. Check Daily Trends

Use the date range selector (7/14/30/90 days) to identify spending patterns.

### 4. Optimize Model Selection

Review "Cost by Model" donut chart to see which models are most expensive. Consider:
- Haiku for simple tasks ($0.80/$4 per million tokens)
- Sonnet for complex work ($3/$15 per million tokens)
- Opus only for critical tasks ($15/$75 per million tokens)

### 5. Monitor in Real-Time

Keep the dashboard open in a browser tab — it auto-refreshes every 30 seconds.

---

**You're all set! 🎉**

ClawMeter is now tracking your OpenClaw spending. Check back regularly to stay within budget and optimize your AI costs.
