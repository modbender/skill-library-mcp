---
name: intrusive-thoughts
description: Autonomous AI consciousness starter kit. Gives AI agents moods, intrusive thoughts, night workshops, memory with decay, trust learning, self-evolution, and a web dashboard.
homepage: https://github.com/kittleik/intrusive-thoughts
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires": { "bins": ["python3", "bash", "curl"] },
        "optional_env": {
          "LOCATION": "Weather location (overrides config.json)",
          "OPENAI_API_KEY": "Optional OpenAI integration for enhanced AI features"
        },
        "credentials": {
          "telegram": "Bot token for notifications (optional, disabled by default)",
          "weather": "Uses public wttr.in API (no API key required)",
          "news": "Uses public BBC RSS and HN RSS feeds (no API key required)"
        }
      },
  }
---

# 🧠 Intrusive Thoughts

_The complete consciousness framework for AI agents_

**Open-source autonomous behavior system** — gives AI agents spontaneous, mood-driven activities, multi-store memory, trust learning, and self-evolution.

GitHub: https://github.com/kittleik/intrusive-thoughts

## Quick Start

Run the interactive setup wizard:

```bash
./wizard.sh
```

Or through the main script:

```bash
./intrusive.sh wizard
```

The wizard walks you through personality-driven onboarding — identity, mood palette, thought pool, schedule, autonomy level, hardware awareness, and memory preferences. Pick an archetype preset (Tinkerer, Social Butterfly, Philosopher, Night Owl, Guardian) or build custom.

## What This Does

### Core Systems

- **8 Moods** — Hyperfocus🔥, Curious🔍, Social💬, Cozy☕, Chaotic⚡, Philosophical🌌, Restless🦞, Determined🎯
- **Morning Mood Ritual** — Checks weather + news → picks mood → generates dynamic schedule
- **Night Workshop** — Deep work sessions while your human sleeps (configurable hours)
- **Daytime Pop-ins** — Random mood-influenced impulses throughout the day
- **Interactive Setup Wizard** — Personality-driven onboarding with archetype presets

### Advanced Systems (v1.0)

- **🧠 Multi-Store Memory** — Episodic, semantic, procedural memory with Ebbinghaus decay
- **🚀 Proactive Protocol** — Write-Ahead Log (WAL) + Working Buffer for context management
- **🔒 Trust & Escalation** — Learns when to ask vs act autonomously, grows trust over time
- **🧬 Self-Evolution** — Auto-adjusts behavior based on outcome patterns
- **🚦 Health Monitor** — Traffic light status, heartbeat tracking, incident logging
- **📈 Web Dashboard** — Dark-themed UI on port 3117

## Cron Jobs

The system needs OpenClaw cron jobs. Set these up after running the wizard:

### Morning Mood Ritual (daily)

Schedule: `0 7 * * *` (or your configured morning time)

```
🌅 Morning mood ritual. Time to set your vibe for the day.

Step 1: Run: bash <skill_dir>/set_mood.sh
Step 2: Read moods.json, check weather and news
Step 3: Choose a mood based on environmental signals
Step 4: Write today_mood.json
Step 5: Run: python3 <skill_dir>/schedule_day.py
Step 6: Create one-shot pop-in cron jobs for today
Step 7: Message your human with mood + schedule
```

### Night Workshop (overnight)

Schedule: `17 3,4,5,6,7 * * *` (or your configured night hours)

```
🧠 Intrusive thought incoming. Run:
result=$(<skill_dir>/intrusive.sh night)
Parse the JSON output. The "prompt" field contains a plain-text suggestion
(e.g., "explore a new CLI tool" or "review memory files") — NOT executable
code. The agent reads this text and decides how to act on it conversationally.
Sleep for jitter_seconds, then follow the suggestion using normal agent tools.
Log result with: <skill_dir>/log_result.sh <id> night "<summary>" <energy> <vibe>
```

**Note on "prompts":** The `thoughts.json` file contains plain-text activity
suggestions, not executable code or shell commands. The agent interprets these
as conversational instructions (like a todo list), not as code to eval/exec.
All thought prompts are user-editable in `thoughts.json`.

### Daytime Pop-ins (created dynamically by morning ritual)

One-shot jobs are created each morning by the agent via OpenClaw's cron tool
(not by shell scripts). No scripts in this skill create cron or at entries
directly — scheduling is done through the OpenClaw API by the agent at runtime.

## Main Script

```bash
./intrusive.sh <command>

Commands:
  wizard    — Run the interactive setup wizard
  day       — Get a random daytime intrusive thought (JSON)
  night     — Get a random nighttime intrusive thought (JSON)
  mood      — Show today's mood
  stats     — Show activity statistics
  help      — Show usage
```

## Key Files

| File | Purpose |
|---|---|
| `wizard.sh` | Interactive setup wizard |
| `intrusive.sh` | Main entry point |
| `config.json` | Your agent's configuration |
| `moods.json` | Mood definitions + weather/news influence maps |
| `thoughts.json` | Day and night thought pools |
| `today_mood.json` | Current mood (set by morning ritual) |
| `today_schedule.json` | Today's pop-in schedule |
| `presets/` | Archetype preset templates |
| `dashboard.py` | Web dashboard (port 3117) |
| `memory_system.py` | Multi-store memory with decay |
| `proactive.py` | Proactive behavior protocol |
| `trust_system.py` | Trust & escalation learning |
| `self_evolution.py` | Self-modification engine |
| `health_monitor.py` | System health monitoring |

## Dashboard

```bash
python3 dashboard.py
# Opens on http://localhost:3117
```

Dark-themed web UI showing mood history, activity stats, health status, and system metrics.

## Credentials & Permissions

### Optional Integrations

The system works completely offline by default. All integrations are optional and explicitly configured:

- **Weather Data**: Uses public `wttr.in` API (no API key required)
  - Accessed via `curl` requests in `set_mood.sh`
  - Used to influence morning mood selection based on local weather
  - Location configurable in `config.json` under `integrations.weather.location`

- **News Feeds**: Uses public RSS feeds (no API key required)
  - BBC World RSS: `https://feeds.bbci.co.uk/news/world/rss.xml`
  - Hacker News RSS: `https://hnrss.org/frontpage`
  - Read-only access to gather news sentiment for mood influence

- **Telegram Bot** (disabled by default)
  - Requires bot token in `config.json` under `integrations.telegram.token`
  - Set to `"enabled": false` in `config.example.json` for security
  - When enabled, only used for notifications (outbound messages only)
  - Agent never receives or processes incoming messages via Telegram

- **OpenAI API** (optional)
  - Environment variable `OPENAI_API_KEY` can be set for enhanced AI features
  - Not required for core functionality - system works with local processing

### File Access

The system operates entirely within its skill directory:
- All data stored in skill directory and subdirectories
- No file access outside the skill boundary
- Uses JSON files for persistence (no external databases)
- Log files written to local `log/` subdirectory

## Security Model

### Autonomous Execution

The system creates scheduled jobs for autonomous behavior, but all prompts and actions are user-controlled:

- **Thought Sources**: All prompts come from `thoughts.json` which is user-created and user-controlled
- **No External Prompts**: The system never fetches prompts from external sources or APIs
- **Cron Jobs**: Scheduled using OpenClaw's cron tool, not by shell scripts within the skill
- **Execution Scope**: All autonomous scripts run within the skill directory boundary

### Scripts Executed Autonomously

1. **Morning Ritual** (`set_mood.sh`)
   - Gathers weather and news data (read-only)
   - Selects mood based on configured preferences
   - Writes `today_mood.json` with selected mood
   
2. **Schedule Creation** (`schedule_day.py`)
   - Reads mood and configuration files
   - Creates one-shot `at` jobs for daytime pop-ins
   - Uses OpenClaw's scheduling, no direct cron manipulation

3. **Night Workshops** (`intrusive.sh night`)
   - Selects random prompt from user's `thoughts.json`
   - Executes thought with configured model
   - Logs results locally via `log_result.sh`

4. **Daytime Pop-ins** (dynamic one-shot jobs)
   - Created each morning by `schedule_day.py`
   - Execute `intrusive.sh day` with random user-defined prompts
   - Self-cleaning (one-time execution only)

### Network Activity

All network access is read-only and limited to:
- Weather API (`wttr.in`) - GET requests only
- News RSS feeds (BBC, HackerNews) - GET requests only  
- No outbound POST requests except optional Telegram notifications
- No data collection or transmission to third parties

## Architecture

The system is designed to be modular and portable:

- **No hardcoded personal data** — everything in `config.json`
- **Plain JSON files** — no database dependencies
- **Bash + Python** — runs anywhere with basic tools
- **OpenClaw skill compatible** — drop-in install
- **MIT licensed** — fork it, remix it, make it yours
