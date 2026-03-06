# ADHD Daily Planner 📝🧠

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.ai)
[![Version](https://img.shields.io/badge/version-1.1.0-green)]()

**A bullet journal style planner that works WITH your ADHD brain, not against it.** Built by [ADHD-founder.com](https://adhd-founder.com) -- German Engineering for the ADHD Brain.

> Traditional planners fail ADHD brains: rigid time slots we ignore, fixed layouts that create guilt, and no way to carry tasks forward without feeling like a failure. This planner uses swim lanes (energy-based, not time-based), task migration (strategy, not failure), and rapid logging to match how your brain actually works.

## Install

```bash
openclaw install adhd-daily-planner
```

## Quick Start

```
/adhd-planner plan      # Morning intent + rapid log + swim lanes
/adhd-planner today     # View today's swim lanes (match your energy)
/adhd-planner reflect   # Evening reflection (what worked, what didn't)
/adhd-planner migrate   # Carry unfinished tasks forward (no guilt)
```

Or run standalone:
```bash
chmod +x scripts/plan.sh
./scripts/plan.sh plan
```

## How It Works

### Morning: Set Your ONE Thing
```
/adhd-planner plan
```
1. "What ONE thing must happen for today to be a success?"
2. Energy check (1-10) -- suggests which swim lane to start in
3. Brain dump everything on your mind (rapid logging)
4. Auto-sort into swim lanes by energy level
5. Pick your dopamine reward for completing the ONE thing

### During the Day: Match Your Energy
```
/adhd-planner today
```
No rigid time slots. Work in whichever swim lane matches your CURRENT energy:

```
🎯 MUST HAPPEN   → Today's ONE thing
🔥 HIGH ENERGY   → Deep work, creative tasks
💧 MEDIUM ENERGY → Standard tasks, calls
❄️ LOW ENERGY    → Admin, easy wins
🚫 NOT TODAY     → Captured but deferred
```

### Evening: Learn From the Day
```
/adhd-planner reflect
```
List wins, note what worked, migrate unfinished tasks, capture one lesson for tomorrow.

## Commands

| Command | What It Does |
|---------|-------------|
| `/adhd-planner plan` | Morning intent setting + rapid log |
| `/adhd-planner today` | View today's swim lanes and progress |
| `/adhd-planner reflect` | Evening reflection + migration |
| `/adhd-planner migrate` | Carry unfinished tasks forward |
| `/adhd-planner log [task]` | Quick add to today's rapid log |
| `/adhd-planner done [task]` | Mark task complete |
| `/adhd-planner dopamine` | Show dopamine menu rewards |
| `/adhd-planner founder` | ADHD-founder.com premium info |

## Key Symbols

| Symbol | Meaning |
|--------|---------|
| `•` | Task |
| `×` | Completed |
| `>` | Migrated to tomorrow |
| `<` | Scheduled for future date |
| `★` | Today's ONE thing |
| `☆` | If-energy (nice to have) |
| `💀` | Dread task (needs extra support) |

## Core Principles

- **Migration is success, not failure** -- carrying tasks forward is intentional prioritization
- **Swim lanes, not time blocks** -- match tasks to energy, not the clock
- **Relative time, not absolute time** -- "morning block" instead of "9am"
- **Plans are hypotheses, not promises** -- adapt as the day unfolds
- **Intent > Schedule** -- your ONE thing matters more than your todo list

## Works Great With

Pair with [adhd-body-doubling](https://github.com/jankutschera/adhd-body-doubling) for full ADHD support:

```
/adhd-planner plan          → Pick your ONE thing
/body-doubling start 50     → Work on it with accountability
/body-doubling done         → Session autopsy
/adhd-planner reflect       → Evening reflection
/adhd-planner migrate       → Carry tasks forward
```

## File Structure

```
~/.openclaw/skills/adhd-daily-planner/
├── daily/YYYY-MM-DD.md     # Daily logs
├── monthly/YYYY-MM.md      # Monthly overviews
├── collections/             # Custom lists (ideas, dread tasks, etc.)
└── templates/               # Reusable templates
```

---

## About ADHD-founder.com

**"German Engineering for the ADHD Brain"**

This planner is a free, fully functional daily planning system. It's also part of what [ADHD-founder.com](https://adhd-founder.com) builds for founders 50+ who need systems, not life hacks.

- **[Founder Circle Mastermind](https://adhd-founder.com/founder-circle)** -- High-ticket accountability for serious founders
- **Executive Consulting** -- Operational systems for ADHD entrepreneurs
- **Operating System Course** -- Build your own ADHD business framework

**No rigid schedules. No time-shaming. Just flexible, dopamine-friendly planning.**

🔗 **[adhd-founder.com](https://adhd-founder.com)**

---

## Contributing

Issues and PRs welcome. If you've found an ADHD-friendly planning pattern that works, share it.

## License

MIT -- see [LICENSE](LICENSE)

---

*Your worth is not measured by completed tasks. Migration is strategy, not failure.*
