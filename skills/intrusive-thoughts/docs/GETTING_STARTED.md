# Getting Started with Intrusive Thoughts

## What is this?

Intrusive Thoughts gives your AI agent autonomous behavior — moods, schedules, impulses, and learning. Instead of waiting for commands, your agent *lives*: checking weather, exploring tools, building things at 3am, and drifting between curious and focused based on how the day goes.

## Requirements

- **Python 3.8+** (stdlib only — no pip dependencies)
- **OpenClaw** agent platform
- **5 minutes** of setup time

## Installation

### Option 1: One-Command Setup (Recommended)

```bash
git clone https://github.com/kittleik/intrusive-thoughts.git
cd intrusive-thoughts
./setup.sh
```

The wizard asks for your name, timezone, agent name, and preferences. For CI/automation:

```bash
./setup.sh --non-interactive
```

### Option 2: Manual Setup

```bash
git clone https://github.com/kittleik/intrusive-thoughts.git
cd intrusive-thoughts
cp config.example.json config.json
# Edit config.json with your details
mkdir -p health memory_store wal buffer evolution trust_store log journal
```

### Option 3: OpenClaw Skill

```bash
# Copy to your skills directory
cp -r intrusive-thoughts/ ~/.openclaw/skills/intrusive-thoughts/
```

## Configuration

Edit `config.json`:

```json
{
  "human": {
    "name": "Your Name",
    "timezone": "Europe/Oslo"
  },
  "agent": {
    "name": "Your Agent",
    "emoji": "🦞"
  },
  "scheduling": {
    "morning_mood_time": "07:00",
    "timezone": "Europe/Oslo"
  }
}
```

See `config.example.json` for all options.

## Setting Up Cron Jobs

The system needs OpenClaw cron jobs for autonomous behavior:

### Morning Mood Ritual (daily)
Checks weather + news → picks a mood → generates day's schedule → messages you.

### Night Workshop (nightly, 03:00-07:00)  
Deep work sessions while you sleep. Builds tools, explores, writes.

### Daytime Pop-ins
Created dynamically by the morning ritual. Random times based on mood.

Your agent can set these up automatically using the OpenClaw cron tool.

## Verifying Installation

```bash
# Check system health
./health_cli.sh status

# Test memory system
python3 memory_system.py stats

# Test trust system
python3 trust_system.py stats

# Launch dashboard
python3 dashboard.py
# Visit http://localhost:3117
```

## Architecture Overview

```
Morning Ritual → Mood Selection → Schedule Generation
                      ↓
              Daytime Pop-ins ← Working Buffer
                      ↓
              Activity Logging → WAL → Trust Scoring
                      ↓
              Night Workshop → Memory Consolidation
                      ↓
              Self-Evolution → Weight Adjustments
                      ↓
              Next Morning Ritual (repeat)
```

### Key Systems

| System | File | Purpose |
|--------|------|---------|
| Mood | `moods.json`, `set_mood.sh` | 8 moods influenced by weather/news |
| Thoughts | `thoughts.json`, `intrusive.sh` | Weighted random impulse picker |
| Memory | `memory_system.py` | Episodic/semantic/procedural with decay |
| Proactive | `proactive.py` | WAL logging + working buffer |
| Trust | `trust_system.py` | Learn when to ask vs act |
| Evolution | `self_evolution.py` | Auto-adjust from patterns |
| Health | `health_monitor.py` | Traffic light monitoring |
| Dashboard | `dashboard.py` | Web UI on port 3117 |

## Next Steps

- Read the full [README](../README.md) for detailed feature docs
- Customize `thoughts.json` with your own impulses  
- Add moods in `moods.json` if the 8 defaults don't fit
- Define achievements in `achievements.json`
- Check the dashboard at http://localhost:3117

## Troubleshooting

**Setup fails with "Python not found"**
→ Install Python 3.8+: `sudo apt install python3` (Ubuntu) or `brew install python` (macOS)

**Health monitor shows 🟡 yellow**
→ Run `./setup.sh` to initialize missing data files

**Cron jobs not firing**
→ Check OpenClaw cron status. The morning ritual creates daytime pop-ins.

**Dashboard won't start**
→ Check if port 3117 is in use: `lsof -i :3117`
