# 🌅 Morning Briefing Cron Job - Complete System

A comprehensive, autonomous morning briefing system that delivers consolidated daily intelligence plus automated skill discovery to your Telegram every day at **10:15 AM Mountain Standard Time**.

## ✨ Features

### 🎯 Daily Consolidated Briefing
- **📺 YouTube Analytics**: Last 24h performance, top videos, subscriber changes
- **📧 Email Summary**: Unread count, important senders, key messages
- **🌤️ Weather**: Current Denver conditions + today's forecast
- **📅 Calendar**: Today's events + upcoming 48 hours
- **🔗 News Briefs**: Tech, maker, AI trending topics with links
- **📚 Research Briefs**: 
  - 3D printing (products, techniques, announcements)
  - Agentic coding (Claude, AutoGPT, reasoning patterns)
  - Clawdbot ecosystem (new features, community updates)
  - Trending Clawdbot skills (top installed, new releases)

### 🤖 Autonomous Skill Discovery (Async Sub-Agent)
- Analyzes your workspace context (MEMORY.md, daily logs, etc.)
- Searches ClawdHub for relevant skills matching your interests
- Validates skill age (≥2 days old)
- Runs security scans on all candidates
- Auto-installs SAFE skills with confirmation
- Reports CAUTION/DANGEROUS findings without installing
- Delivers summary: "X reviewed, Y installed, Z rejected"

## 📋 Quick Start

### One-Command Install

```bash
bash /Users/ericwoodard/clawd/scripts/install-morning-briefing.sh
```

That's it! Follow the interactive prompts.

### Manual Install

```bash
# 1. Add to crontab
crontab -e

# 2. Paste this line (runs at 10:15 AM daily):
15 10 * * * /bin/bash /Users/ericwoodard/clawd/morning-briefing.sh >> /Users/ericwoodard/clawd/logs/morning-briefing.log 2>&1

# 3. Verify
crontab -l
```

## 🗂️ What's Included

| File | Purpose |
|------|---------|
| `morning-briefing.sh` | Cron entry point (shell script) |
| `scripts/generate-morning-briefing.js` | Briefing generator & Telegram sender |
| `scripts/skill-discovery-agent.js` | Autonomous skill discovery sub-agent |
| `scripts/install-morning-briefing.sh` | Interactive installer |
| `config/morning-briefing.config.json` | Configuration (schedule, targets, interests) |
| `crontabs/morning-briefing.cron` | Sample crontab file |
| `MORNING-BRIEFING-SETUP.md` | Detailed setup & configuration guide |
| `MORNING-BRIEFING-QUICK-START.md` | Quick reference (2-minute read) |
| `MORNING-BRIEFING-ARCHITECTURE.md` | Technical architecture & internals |
| `logs/morning-briefing.log` | Execution logs (created on first run) |

## 🚀 How It Works

```
10:15 AM (Daily)
    ↓
morning-briefing.sh
    ↓
    ├─→ generate-morning-briefing.js (Sync)
    │   ├─ Gathers: YouTube, Email, Weather, Calendar, News
    │   ├─ Consolidates into single report
    │   └─ Sends to Telegram
    │
    └─→ skill-discovery-agent.js (Async Sub-Agent)
        ├─ Analyzes your interests
        ├─ Searches ClawdHub
        ├─ Security scans & installs
        └─ Sends summary to Telegram
```

## 📊 Example Output

### Message 1: Consolidated Briefing

```
═══════════════════════════════════════════════════════════
🌅 MORNING BRIEFING - Wednesday, January 29
═══════════════════════════════════════════════════════════

📺 YouTube Analytics:
  Last 24h: 1,234 views, 45 engagements
  Top videos: "3D Printing Timelapse", "AI Agent Deep Dive"
  Subscribers: +12 new subscribers

📧 Email Summary:
  Unread: 8 messages
  Important from: OpenAI, Printables, Clawdbot
  Key: "New Haiku model release", "Trending skill: claude-coder"

🌤️ Weather: Denver, CO
  Current: 28°F, Cloudy
  Today: High 32°F, Low 22°F, 20% chance snow
  
[... continued for Calendar, News, Research Briefs ...]

═══════════════════════════════════════════════════════════
✨ Skill Discovery Summary Incoming...
═══════════════════════════════════════════════════════════
```

### Message 2: Skill Discovery Report

```
═══════════════════════════════════════════════════════════
🎯 SKILL DISCOVERY SUMMARY
═══════════════════════════════════════════════════════════

📊 Results:
  • Skills reviewed: 5
  • Skills installed: 2
  • Skills rejected: 3

✅ Successfully installed:
  • claude-agentic-loop
  • esp32-telemetry

❌ Rejected skills:
  • klipper-3d-monitor: Too new (<2 days)
  • openai-reasoning: CAUTION - Requires elevated permissions
  • clawdbot-hub-search: DANGEROUS - Unverified dependency

═══════════════════════════════════════════════════════════
✨ Skill discovery complete!
═══════════════════════════════════════════════════════════
```

## ⚙️ Configuration

### Change Schedule

Edit crontab: `crontab -e`

```
# Current: 10:15 AM daily
15 10 * * *

# Change to examples:
30 9  * * *    # 9:30 AM
0  8  * * *    # 8:00 AM
45 14 * * *    # 2:45 PM
0  10 * * 1-5  # 10:00 AM weekdays only
```

### Change Telegram Target

Edit `config/morning-briefing.config.json`:
```json
"telegram": {
  "targetId": "<your_telegram_user_id>",
  "targetType": "group"  // or "user"
}
```

### Customize Interests

Edit `scripts/skill-discovery-agent.js`:
```javascript
const INTEREST_KEYWORDS = {
  'MY_INTEREST': ['keyword1', 'keyword2', ...],
  // Add custom interests
};
```

### Add Briefing Topics

Edit `scripts/generate-morning-briefing.js`:
```javascript
const topics = [
  'My custom topic',
  'Another area of interest',
  // Add topics
];
```

## 🧪 Testing

### Test Manually

```bash
# Test briefing generator
node /Users/ericwoodard/clawd/scripts/generate-morning-briefing.js

# Test skill discovery
node /Users/ericwoodard/clawd/scripts/skill-discovery-agent.js
```

### Monitor Logs

```bash
# Follow logs in real-time
tail -f /Users/ericwoodard/clawd/logs/morning-briefing.log

# Check for errors
grep ERROR /Users/ericwoodard/clawd/logs/morning-briefing.log
```

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Cron not running | Check timezone: `date` (should be America/Denver) |
| Cron not running | Check crontab: `crontab -l` (should show the job) |
| No Telegram messages | Verify Clawdbot is running: `clawdbot gateway status` |
| Skills not available | Install them: `clawdbot skills install youtube-analytics` |
| Check logs | `tail -f /Users/ericwoodard/clawd/logs/morning-briefing.log` |

## 📚 Documentation

- **MORNING-BRIEFING-QUICK-START.md** - 2-minute TL;DR
- **MORNING-BRIEFING-SETUP.md** - Full setup & configuration guide
- **MORNING-BRIEFING-ARCHITECTURE.md** - Technical deep dive & internals

## 🎯 Key Design Decisions

1. **Consolidated Message**: Single report (not scattered notifications)
2. **Async Sub-Agent**: Skill discovery doesn't block briefing delivery
3. **Security First**: All skills vetted before installation
4. **Age Requirement**: ≥2 days old skills only (community review period)
5. **Graceful Degradation**: Missing skills don't break the briefing
6. **Local Context Analysis**: Interests detected from your workspace files
7. **Extensible**: Easy to add new briefing components or discovery interests

## 🚀 Next Steps

1. **Install**: `bash scripts/install-morning-briefing.sh`
2. **Verify**: `crontab -l` (confirm job is there)
3. **Test**: `node scripts/generate-morning-briefing.js`
4. **Monitor**: `tail -f logs/morning-briefing.log`
5. **Wait**: First briefing arrives at 10:15 AM tomorrow!

## ❓ FAQ

**Q: What timezone does the cron job use?**  
A: System timezone (should be America/Denver). Verify with `date`.

**Q: What if a skill isn't installed?**  
A: The briefing continues with a note saying that component is unavailable.

**Q: Can I change what time it runs?**  
A: Yes! Edit crontab: `crontab -e` and change `15 10` to your preferred time.

**Q: What if I don't want skill discovery?**  
A: Edit the script and remove the `spawnSkillDiscoveryAgent()` call.

**Q: How long does it take to run?**  
A: Briefing: ~10-15 seconds. Skill discovery: ~5-10 minutes (async, doesn't block).

**Q: Where are the logs?**  
A: `/Users/ericwoodard/clawd/logs/morning-briefing.log`

**Q: How do I remove the cron job?**  
A: `crontab -e` and delete the morning-briefing line.

## 📧 Support

Check the logs: `tail -f /Users/ericwoodard/clawd/logs/morning-briefing.log`

For detailed help, see the documentation files above.

---

**Created**: January 2025  
**Version**: 1.0  
**Status**: Ready for deployment  
**License**: Personal use

Enjoy your daily AI-powered briefings! 🌅
