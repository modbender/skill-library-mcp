# Agent Setup Prompt

Copy this prompt into a new OpenClaw session to set up SecondMind automatically:

---

```
I have the SecondMind skill installed (an autonomous memory and initiative system).
Please set it up step by step:

## Step 1: Run setup
cd /path/to/secondmind && node setup.js

## Step 2: Configure
Open the generated config.json and set:
- openrouter.apiKey: my OpenRouter API key (ask me for it)
- Check which OpenClaw agents exist: ls ~/.openclaw/agents/
- Set sessionsPath to the correct session path
- Optional: Set telegramMode to "integrated" or "standalone"
- Optional: Set notifications.enabled = true + Telegram bot token and chat ID

## Step 3: Test
Run these one by one and show me each output:
1. node scripts/ingest.js
2. node scripts/status.js
3. node scripts/consolidate.js
4. node scripts/status.js
5. node scripts/initiative.js
6. node scripts/status.js

## Step 4: Verify cron jobs
crontab -l | grep secondmind
Should show 4 jobs. If not, run node setup.js again.

## Step 5: Telegram (optional)
If telegramMode is "standalone" and notifications are enabled:
  nohup node scripts/telegram-bot.js >> /tmp/secondmind-bot.log 2>&1 &
If telegramMode is "integrated":
  No extra steps – I handle commands directly via this agent.

## Important:
- ALL LLM calls go through OpenRouter Cloud
- No local models needed (no Ollama, no GPU)
- Cost: ~$0.60-1.65/month
- Models in config.json are pre-optimized for minimal cost
- Logs: /tmp/secondmind-ingest.log, /tmp/secondmind-consolidate.log etc.
- Full reset: node setup.js --reset

Show me the final output of: node scripts/status.js
```
