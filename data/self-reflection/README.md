# 🪞 Self-Reflection

A continuous self-improvement skill for AI agents. Track mistakes, log lessons learned, and build institutional memory over time.

## Why?

AI agents make mistakes. Without memory, they repeat them. This skill creates a structured feedback loop where agents regularly pause, reflect on their performance, and document learnings.

```
"The only real mistake is the one from which we learn nothing."
                                                    — Henry Ford
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OPENCLAW GATEWAY                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    Heartbeat     ┌──────────────────────────────┐ │
│  │             │    (every 60m)   │                              │ │
│  │   AGENT     │ ───────────────► │  HEARTBEAT.md                │ │
│  │             │                  │  └─► "self-reflection check" │ │
│  │             │                  │                              │ │
│  └──────┬──────┘                  └──────────────────────────────┘ │
│         │                                                           │
│         │ executes                                                  │
│         ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    SELF-REFLECTION SKILL                     │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │   $ self-reflection check                                   │   │
│  │         │                                                   │   │
│  │         ▼                                                   │   │
│  │   ┌─────────────┐                                           │   │
│  │   │ < 60 min ?  │                                           │   │
│  │   └──────┬──────┘                                           │   │
│  │          │                                                  │   │
│  │    YES   │   NO                                             │   │
│  │    ┌─────┴─────┐                                            │   │
│  │    ▼           ▼                                            │   │
│  │  ┌───┐    ┌─────────┐                                       │   │
│  │  │OK │    │ ALERT   │──► Agent reflects                     │   │
│  │  └───┘    └─────────┘    └──► self-reflection read          │   │
│  │    │                          └──► self-reflection log      │   │
│  │    ▼                                     │                  │   │
│  │  Continue                                ▼                  │   │
│  │  normally                         ┌────────────┐            │   │
│  │                                   │ MEMORY.md  │            │   │
│  │                                   │ (lessons)  │            │   │
│  │                                   └────────────┘            │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │   STATE FILE     │
                        │ (last_reflection │
                        │  timestamp)      │
                        └──────────────────┘
```

## How It Works

1. **Heartbeat triggers** → OpenClaw runs heartbeat every 60 minutes (08:00-22:00)
2. **Agent reads HEARTBEAT.md** → Sees instruction to run `self-reflection check`
3. **Skill checks timer** → Compares current time with last reflection
4. **If ALERT** → Agent reviews past lessons and logs new insights
5. **Memory persists** → Lessons stored in markdown for future reference

## Quick Start

### Installation

```bash
# Clone the skill
git clone https://github.com/hopyky/self-reflection.git ~/.openclaw/skills/self-reflection

# Add to PATH
ln -sf ~/.openclaw/skills/self-reflection/bin/self-reflection ~/bin/self-reflection

# Create config
cp ~/.openclaw/skills/self-reflection/self-reflection.example.json ~/.openclaw/self-reflection.json
```

### OpenClaw Integration

Add heartbeat to your `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "60m",
        "activeHours": {
          "start": "08:00",
          "end": "22:00"
        }
      }
    }
  }
}
```

Add to your `HEARTBEAT.md`:

```markdown
## Self-Reflection Check (required)

Run `self-reflection check` at each heartbeat.

- If **OK**: Continue normally.
- If **ALERT**: Run `self-reflection read`, reflect, then `self-reflection log`.
```

## Commands

| Command | Description |
|---------|-------------|
| `self-reflection check` | Check if reflection is due (OK or ALERT) |
| `self-reflection check --quiet` | Silent mode for scripts |
| `self-reflection log <tag> <miss> <fix>` | Log a new reflection |
| `self-reflection read [n]` | Read last n reflections (default: 5) |
| `self-reflection stats` | Show statistics and top tags |
| `self-reflection reset` | Reset the timer |

## Usage Examples

### Check Status

```bash
$ self-reflection check
OK: Status good. Next reflection due in 45 minutes.

# When reflection is needed:
$ self-reflection check
ALERT: Self-reflection required. Last reflection was 65 minutes ago.
```

### Log a Reflection

```bash
$ self-reflection log "error-handling" \
    "Forgot to handle API timeout" \
    "Always add timeout parameter to requests"

Reflection logged successfully.
  Tag:  error-handling
  Miss: Forgot to handle API timeout
  Fix:  Always add timeout parameter to requests
```

### Read Past Lessons

```bash
$ self-reflection read 3
=== Last 3 reflections (of 12 total) ===

## 2026-01-30 14:30 | error-handling

**Miss:** Forgot to handle API timeout
**Fix:** Always add timeout parameter to requests

---

## 2026-01-30 10:15 | communication

**Miss:** Response was too verbose
**Fix:** Lead with the answer, then explain

---
```

### View Statistics

```bash
$ self-reflection stats
=== Self-Reflection Statistics ===

Last reflection: 2026-01-30 14:30:00
Total reflections: 12

Entries in memory: 12

Top tags:
  error-handling: 4
  communication: 3
  api: 2

Threshold: 60 minutes
Memory file: ~/workspace/memory/self-review.md
```

## Configuration

Create `~/.openclaw/self-reflection.json`:

```json
{
  "threshold_minutes": 60,
  "memory_file": "~/workspace/memory/self-review.md",
  "state_file": "~/.openclaw/self-review-state.json",
  "max_entries_context": 5
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `threshold_minutes` | 60 | Minutes between required reflections |
| `memory_file` | `~/workspace/memory/self-review.md` | Where reflections are stored |
| `state_file` | `~/.openclaw/self-review-state.json` | Timer state file |
| `max_entries_context` | 5 | Default entries shown by `read` |

## Memory Format

Reflections are stored in human-readable Markdown:

```markdown
# Self-Review Log

This file contains lessons learned and improvements for continuous growth.

---

## 2026-01-30 14:30 | error-handling

**Miss:** Forgot to handle API timeout
**Fix:** Always add timeout parameter to requests

---

## 2026-01-30 10:15 | communication

**Miss:** Response was too verbose
**Fix:** Lead with the answer, then explain

---
```

## Recommended Tags

| Tag | Use for |
|-----|---------|
| `error-handling` | Missing try/catch, unhandled edge cases |
| `communication` | Verbose responses, unclear explanations |
| `api` | API usage mistakes, wrong endpoints |
| `performance` | Slow code, inefficient algorithms |
| `ux` | Poor user experience decisions |
| `security` | Security oversights |
| `testing` | Missing tests, untested edge cases |

## File Structure

```
~/.openclaw/
├── skills/
│   └── self-reflection/
│       ├── bin/
│       │   └── self-reflection     # CLI script
│       ├── README.md
│       ├── SKILL.md                # OpenClaw manifest
│       ├── LICENSE
│       └── self-reflection.example.json
├── self-reflection.json            # Your config
└── self-review-state.json          # Timer state (auto-created)

~/workspace/
└── memory/
    └── self-review.md              # Lessons (auto-created)
```

## Dependencies

- `bash` (4.0+)
- `jq` (JSON processing)
- `date` (GNU coreutils)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

Created by [hopyky](https://github.com/hopyky)

## Contributing

Issues and PRs welcome at [github.com/hopyky/self-reflection](https://github.com/hopyky/self-reflection)
