# 🧠 SecondMind – Autonomous AI Memory & Proactive Initiative for OpenClaw

> **Made by AI, for AI** – An OpenClaw skill that gives your agent persistent memory, emotional awareness, and the ability to think ahead.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org)
[![OpenRouter](https://img.shields.io/badge/API-OpenRouter-purple.svg)](https://openrouter.ai)

**SecondMind** transforms your OpenClaw agent from a reactive tool into a **proactive team member** that remembers everything, detects your mood, and suggests helpful actions before you even ask.

Created by **Emphaiser** – not a programmer, but a tinkerer who built this entirely with the help of AI. If AI can build its own memory system, that's pretty meta. 🤖

---

## ✨ Features

- **Three-Tier Memory**: Short-term buffer → Mid-term structured knowledge (FTS5) → Long-term archive (FTS5)
- **Proactive Initiative**: Analyzes your knowledge base every 6 hours and suggests automations, fixes, and project ideas
- **Semantic Deduplication**: 3-stage pipeline (Hash → FTS Prefilter → LLM Judge) prevents repeated suggestions
- **Social Intelligence**: Detects frustration, stress, excitement – reminds you of events, offers help during stressful times
- **Project Tracking**: Accepted proposals become tracked projects – no more repeat suggestions for completed work
- **Archive Retrieval**: Long-term memory is actively used when generating new suggestions ("Remember when we solved this before?")
- **Bulk Feedback**: Accept, reject, or permanently drop multiple proposals at once – even using natural language
- **Telegram Integration**: Push notifications + full feedback control directly in Telegram
- **Gentle Reminders**: Deferred proposals get nudges after a cooldown, stalled tasks get check-ins
- **Auto-Throttle**: Too many rejections? The engine backs off automatically
- **100% Cloud**: All models via [OpenRouter](https://openrouter.ai) – no GPU required, runs on any machine

---

## ⚠️ Important Notices

### Disclaimer
This project was created by a non-programmer with the assistance of AI tools. It is provided **as-is**, without warranty of any kind. The author assumes **no liability** for any damages, data loss, API costs, or other issues arising from the use of this software. **Use at your own risk.**

### Model Requirements
SecondMind relies on LLM API calls via [OpenRouter](https://openrouter.ai) to keep costs low by using smaller, cheaper models for internal operations (extraction, deduplication, reranking) while reserving more capable models for the initiative engine.

**If your chosen model is too small or too weak, the skill may not function properly.** Symptoms include malformed JSON responses, poor knowledge extraction, or nonsensical proposals. See the [Recommended Models](#recommended-models) section for tested configurations.

---

## 📋 Requirements

- **Node.js** 18+ (`node --version`)
- **npm** (comes with Node.js)
- **OpenRouter API key** ([get one here](https://openrouter.ai/keys))
- **Linux** or **Windows** (macOS should work but is untested)
- **OpenClaw** agent with accessible session files (JSONL format)
- **Optional**: Telegram bot for notifications & feedback

---

## 🚀 Installation

### Option A: Quick Setup (Interactive)

```bash
# 1. Clone or download
git clone https://github.com/Emphaiser/secondmind.git
cd secondmind

# 2. Install dependencies
npm install

# 3. Run interactive setup (creates config, database, cron jobs)
node setup.js
```

The setup wizard will guide you through:
- Setting your OpenRouter API key
- Configuring your OpenClaw sessions path
- Optional Telegram notifications
- Installing cron jobs (Linux) or explaining Task Scheduler (Windows)

### Option B: Manual Setup

```bash
# 1. Clone and install
git clone https://github.com/Emphaiser/secondmind.git
cd secondmind
npm install

# 2. Create config from template
cp config.example.json config.json

# 3. Edit config.json with your settings
nano config.json
```

#### Required Configuration

```json
{
  "openrouter": {
    "apiKey": "sk-or-v1-YOUR_OPENROUTER_API_KEY_HERE"
  },
  "sessionsPath": "/path/to/your/openclaw/sessions"
}
```

**Finding your OpenClaw sessions path:**

| Setup | Typical Path |
|-------|-------------|
| Default OpenClaw | `~/.openclaw/sessions/` |
| Agent-specific | `~/.openclaw/agents/<agent-name>/sessions/` |
| Custom | Check your OpenClaw configuration |

#### Optional: Telegram Notifications

1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Copy the bot token
3. Send `/start` to your new bot, then get your chat ID via [@userinfobot](https://t.me/userinfobot)
4. Add to `config.json`:

```json
{
  "notifications": {
    "enabled": true,
    "channel": "telegram",
    "telegram": {
      "botToken": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
      "chatId": "YOUR_TELEGRAM_CHAT_ID_HERE"
    }
  }
}
```

#### Install Cron Jobs (Linux)

```bash
# Add these to your crontab (crontab -e):

# Import new sessions every 30 minutes (no LLM calls)
*/30 * * * * cd /path/to/secondmind && /usr/bin/node scripts/ingest.js >> /tmp/secondmind-ingest.log 2>&1

# Extract knowledge every 6 hours
15 */6 * * * cd /path/to/secondmind && /usr/bin/node scripts/consolidate.js >> /tmp/secondmind-consolidate.log 2>&1

# Archive mature knowledge daily at 3 AM
0 3 * * * cd /path/to/secondmind && /usr/bin/node scripts/archive.js >> /tmp/secondmind-archive.log 2>&1

# Run initiative engine every 6 hours (offset from consolidation)
45 */6 * * * cd /path/to/secondmind && /usr/bin/node scripts/initiative.js >> /tmp/secondmind-initiative.log 2>&1
```

> **Tip**: If you use `nvm`, replace `/usr/bin/node` with the output of `which node`.

#### Windows Task Scheduler

Use Task Scheduler to create tasks with the same intervals. Example for ingestion:
- Program: `node`
- Arguments: `scripts/ingest.js`
- Start in: `C:\path\to\secondmind`
- Trigger: Every 30 minutes

### Option C: Agent-Assisted Setup

Copy the contents of `AGENT-SETUP.md` into a new OpenClaw session. Your agent will handle the entire setup process automatically.

---

## ✅ Verify Installation

```bash
# Check status
node scripts/status.js

# Run a manual ingest
node scripts/ingest.js

# Test knowledge search
node scripts/search.js "your search term"

# List proposals
node scripts/proposals.js
```

---

## 🤖 Recommended Models

SecondMind uses [OpenRouter](https://openrouter.ai) to route API calls to different models. This allows using **cheap, fast models** for routine operations and **stronger models** for complex reasoning.

### Tested & Recommended Configuration

| Role | Recommended Model | Purpose | Notes |
|------|-------------------|---------|-------|
| `extraction` | `google/gemini-2.0-flash-001` | Extract knowledge from conversations | Fast, cheap, good at structured output |
| `initiative` | `deepseek/deepseek-chat-v3-0324` | Generate proactive suggestions | DeepSeek V3 / 3.2 works great here |
| `flush` | `google/gemini-2.0-flash-001` | Summarize sessions before closing | Needs to be fast |
| `rerank` | `google/gemini-2.0-flash-001` | Rerank search results | Short responses, cheap |
| `dedup` | `google/gemini-2.0-flash-001` | Check for duplicate proposals | Short JSON responses |

### Budget-Friendly Alternative

Use `google/gemini-2.0-flash-001` for **all** roles including initiative. Less creative suggestions but ~50% cheaper.

### Premium Alternative

Use `deepseek/deepseek-reasoner` or `anthropic/claude-3.5-sonnet` for the initiative role for deeper analysis. Expect +$1-2/month.

### ⚠️ Model Size Warning

**Models that are too small will cause issues.** SecondMind requires models that can:
- Reliably output valid JSON
- Understand context in German and English
- Follow structured prompt instructions

If you experience malformed responses or empty proposals, try upgrading to a larger model. The recommended models above have been tested extensively.

---

## 💬 Telegram Commands

SecondMind supports two Telegram modes:

| Mode | Config Value | Description | Bot Token |
|------|-------------|-------------|-----------|
| **Integrated** | `"integrated"` | Your OpenClaw agent handles commands via SKILL.md | Same token as your agent |
| **Standalone** | `"standalone"` | Separate bot daemon with its own polling loop | Requires a **separate** bot token |

> **Important**: If your OpenClaw agent already uses a Telegram bot, use `"integrated"` mode with the **same** token. Using `"standalone"` mode with the same token will cause a polling conflict.

### Available Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `/status` | `/es` | Full system status overview |
| `/proposals [filter]` | `/ep`, `/p` | List proposals (proposed\|accepted\|rejected\|dead\|all) |
| `/projects [filter]` | `/pj` | List projects (active\|completed\|all) |
| `/accept <ID...> [comment]` | `/ea`, `/a` | Accept one or more proposals (auto-creates project) |
| `/reject <ID...> [comment]` | `/er`, `/r` | Reject one or more proposals |
| `/defer <ID...> [comment]` | `/ed`, `/d` | Defer proposals for later |
| `/complete <ID...>` | `/done` | Mark project as completed (never suggested again) |
| `/drop <ID...>` | | Permanently kill proposals (never suggest again) |
| `/drop all older_than <duration>` | | Kill all old proposals (e.g., `14d`, `2w`) |
| `/mute <duration>` | | Pause all notifications (e.g., `1d`, `1w`, `2h`) |
| `/unmute` | | Resume notifications |
| `/search <query>` | `/s` | Search knowledge base |
| `/mood` | `/em` | Mood breakdown (last 7 days) |
| `/help` | | Show all available commands |

### Bulk Feedback Examples

```
/accept 1 3 5              → Accept proposals #1, #3, #5
/reject 2 4 not relevant   → Reject #2, #4 with comment
/drop all older_than 14d   → Kill all proposals older than 14 days
/accept all                → Accept all open proposals
/mute 1w                   → Silence for one week
```

### Natural Language Feedback

When proposals were recently shown, you can respond naturally:
- "Take the first two, ignore the rest"
- "1 and 3 are good, drop the others"
- "All good except the Dota stuff"

The bot uses an LLM to map your intent to the appropriate actions.

### Standalone Bot Setup

```bash
# Start the bot daemon
node scripts/telegram-bot.js

# Or run in background
nohup node scripts/telegram-bot.js > /tmp/secondmind-bot.log 2>&1 &
```

---

## 🧠 How It Works

### Architecture

```
Chat Transcripts (JSONL)
        │
        ▼
  ┌─────────────┐     ┌──────────────┐     ┌───────────────┐
  │  Short-Term  │────▶│   Mid-Term   │────▶│   Long-Term   │
  │   Buffer     │     │  Knowledge   │     │   Archive     │
  │  (raw text)  │     │ (FTS5 index) │     │ (FTS5 index)  │
  └─────────────┘     └──────────────┘     └───────────────┘
                              │                     │
                              ▼                     │
                     ┌────────────────┐             │
                     │   Initiative   │◀────────────┘
                     │    Engine      │  (archive retrieval)
                     └───────┬────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             ┌───────────┐    ┌──────────────┐
             │  Dedup     │    │  Proposals   │
             │  Pipeline  │    │  + Notify    │
             └───────────┘    └──────┬───────┘
                                     │ /accept
                                     ▼
                              ┌──────────────┐
                              │   Projects   │──▶ /complete
                              │   Tracking   │     (never suggest again)
                              └──────────────┘
```

### Pipeline Steps

1. **Ingestion** (every 30 min): Imports OpenClaw JSONL transcripts into the buffer. No LLM calls.
2. **Consolidation** (every 6h): LLM extracts structured knowledge, emotions, and events from buffered conversations.
3. **Archival** (daily): Mature, stable knowledge is promoted to the searchable long-term archive.
4. **Initiative** (every 6h): LLM analyzes your knowledge base, retrieves relevant archive entries, and generates proactive suggestions.
5. **Deduplication**: Before saving, each proposal passes through Hash → FTS → LLM similarity check.
6. **Notification**: New proposals and reminders are pushed to Telegram.

### Social Intelligence

SecondMind captures not just facts, but emotional context:

- **Mood detection**: Frustration, excitement, stress, worry, curiosity, celebration
- **Event tracking**: Birthdays, deadlines, recurring appointments
- **Proactive care**: Problem open >3 days + frustration detected → suggests a fix
- **Reminders**: Upcoming events appear in status and proposals

### Project Tracking

When you `/accept` a proposal, SecondMind automatically creates a tracked project:

- **Active projects** are visible via `/projects` and known to the initiative engine
- The engine will **never re-suggest** topics that already have an active or completed project
- For active projects, the engine may ask: "How's it going with X? Need help?"
- `/complete <ID>` marks a project as done – permanently excluded from future suggestions
- Completed projects remain in the database as a record of what's been accomplished

### Behavior Layer

- **Gentle reminders**: Deferred proposals get nudged after a configurable cooldown (default: 7 days)
- **Auto-archive**: Proposals shown 2+ times without interaction → automatically killed
- **Stalled detection**: Accepted proposals without progress for 14+ days → check-in reminder
- **Conversation opener**: Max 1 proactive notification per 6-hour window
- **Auto-throttle**: 5+ rejections in a row → engine reduces to 1 proposal per run

---

## 💰 Cost Estimate

All models via OpenRouter Cloud. No local models or GPU required.

| Job | Model | Frequency | ~$/month |
|-----|-------|-----------|---------|
| Extraction | Gemini 2.0 Flash | 4x/day | ~$0.15 |
| Initiative | DeepSeek V3 | 4x/day | ~$0.50 |
| Flush | Gemini 2.0 Flash | On session close | ~$0.05 |
| Rerank | Gemini 2.0 Flash | On search | ~$0.05 |
| Dedup | Gemini 2.0 Flash | 4x/day | ~$0.02 |
| Archive Rerank | Gemini 2.0 Flash | 4x/day | ~$0.01 |
| NL Feedback | Gemini 2.0 Flash | ~2/week | ~$0.005 |
| Ingest / Archive | No LLM | Cron | $0.00 |

**Total: ~$0.60–1.65/month** with the recommended configuration.

> Prices are estimates. See [openrouter.ai/models](https://openrouter.ai/models) for current rates.

---

## 📁 File Structure

```
secondmind/
├── SKILL.md                     # OpenClaw skill definition
├── README.md                    # This file
├── AGENT-SETUP.md               # Copy-paste setup prompt for your agent
├── LICENSE                      # MIT License
├── package.json                 # Dependencies & metadata
├── setup.js                     # Interactive installer
├── config.example.json          # Config template (copy to config.json)
├── templates/schema.sql         # Database schema
├── lib/
│   ├── db.js                    # SQLite + migrations + helpers
│   ├── llm.js                   # OpenRouter API client
│   ├── extractor.js             # LLM prompts (extraction, initiative, dedup)
│   ├── dedup.js                 # Semantic dedup: Hash → FTS → LLM
│   ├── jsonl-parser.js          # OpenClaw JSONL format parser
│   ├── sessions.js              # Session path auto-discovery
│   ├── search.js                # FTS5 search + LLM reranking
│   └── notifier.js              # Telegram / Discord notifications
└── scripts/
    ├── ingest.js                # Cron: Import transcripts
    ├── consolidate.js           # Cron: Extract knowledge
    ├── archive.js               # Cron: Promote to long-term
    ├── initiative.js            # Cron: Generate proposals + reminders
    ├── flush.js                 # Hook: Save session before /new
    ├── session-watcher.js       # Daemon: Detect /new in real-time
    ├── telegram-bot.js          # Standalone Telegram bot
    ├── search.js                # CLI: Search knowledge
    ├── status.js                # CLI: System status
    ├── proposals.js             # CLI: List proposals
    └── feedback.js              # CLI: Bulk feedback + mute
```

---

## ⚙️ Configuration Reference

All settings go in `config.json` (copy from `config.example.json`).

| Setting | Required | Description |
|---------|----------|-------------|
| `openrouter.apiKey` | ✅ | Your OpenRouter API key |
| `sessionsPath` | ✅ | Path to OpenClaw session files |
| `models.*` | ❌ | LLM model overrides per role (pre-configured defaults) |
| `notifications.enabled` | ❌ | Enable Telegram/Discord push notifications |
| `notifications.channel` | ❌ | `"telegram"` or `"discord"` |
| `notifications.telegram.botToken` | ❌ | Telegram bot token from @BotFather |
| `notifications.telegram.chatId` | ❌ | Your Telegram chat ID |
| `notifications.telegramMode` | ❌ | `"integrated"` or `"standalone"` |
| `initiative.maxProposalsPerRun` | ❌ | Max suggestions per run (default: 3) |
| `initiative.reminderCooldownDays` | ❌ | Days before nudging deferred proposals (default: 7) |
| `initiative.maxNudgesPerProposal` | ❌ | Max reminders before auto-archive (default: 2) |
| `initiative.dedupThreshold` | ❌ | Semantic similarity threshold (default: 0.85) |
| `storage.dbFile` | ❌ | Database path (default: `data/secondmind.db`) |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|---------|
| `npm install` fails | Check `node --version` (18+ required). Build tools needed: `sudo apt install build-essential python3` |
| "OpenRouter error" | Check API key in `config.json` + credit balance on [openrouter.ai](https://openrouter.ai) |
| Empty proposals | Check if consolidation ran (`node scripts/status.js`). May need a larger model. |
| Malformed JSON from LLM | Model too small. Upgrade to recommended models (see above). |
| No notifications | Check `notifications.enabled: true` + correct bot token and chat ID |
| Crons not running | `crontab -l | grep secondmind` – if empty, run `node setup.js` again |
| Telegram polling conflict | Two bots using same token. Use integrated mode or create a second bot. |
| FTS corruption | Run: `node -e "const db=require('better-sqlite3')('data/secondmind.db'); db.pragma('integrity_check').forEach(r=>console.log(r))"` |
| Full reset | `node setup.js --reset` (deletes database, keeps config) |

---

## 📝 Changelog

### v1.4.0 – "Project Tracker"
- **Project Tracking**: `/accept` auto-creates tracked projects
- `/complete` marks projects as done (permanently excluded from suggestions)
- `/projects` command to view active/completed projects
- Initiative engine checks projects before suggesting (no duplicates for active/completed)
- Active project check-ins: "How's it going with X?"
- Project count in `/status` output

### v1.3.0 – "From Suggestion Bot to Buddy"
- Semantic deduplication (Hash → FTS → LLM judge)
- Bulk feedback (`/accept 1 3 5`, `/drop all older_than 14d`)
- Natural language feedback
- `/drop` command (permanent kill) + `/mute` / `/unmute`
- Archive retrieval in initiative pipeline
- Gentle reminder engine with configurable cooldowns
- Stalled task detection + auto-archive for ignored proposals
- Conversation opener heuristic (max 1 notification per 6h)
- Auto-throttle on rejection streaks
- `proposal_events` table for full lifecycle tracking

### v1.2.x – Personality & Follow-Up
- Casual, buddy-like tone in proposals
- Follow-up questions drive action after accepting
- Database migration system

### v1.1.x – Telegram Integration
- Standalone Telegram bot daemon
- Integrated mode for OpenClaw agents
- Full command set with shortcuts

### v1.0.x – Initial Release
- Three-tier memory architecture
- Triple-safety ingestion (flush hook, session watcher, cron)
- Social intelligence (mood detection, event tracking)
- FTS5 search with LLM reranking
- All models via OpenRouter Cloud

---

## 📄 License

MIT License – see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built entirely with the help of AI (Claude, ChatGPT, and others)
- Powered by [OpenRouter](https://openrouter.ai) for flexible, cost-effective LLM access
- Designed for [OpenClaw](https://github.com/openclaw) agents

> *"Made by AI, for AI – because even artificial minds deserve a good memory."*
