# Windowed Autonomy

**Time-windowed autonomous work queue with predictable schedule.**

---

## Overview

The agent works autonomously **only during defined time windows**:

- ☀️ **Daytime** (8 AM - 8 PM UTC): Autonomy ON, work from queue
- 🌙 **Overnight** (8 PM - 8 AM UTC): Autonomy OFF, HEARTBEAT_OK only

**Clear separation:** Day = work, Night = cron maintenance

---

## When to Use

- You want **predictable work schedule**
- You want autonomy to work during **specific hours**
- Tasks are **not time-sensitive** (can wait for window)
- You want the "slowly evolve" approach - start small, expand over time
- You want **clear temporal separation** between autonomy and maintenance

---

## Quick Start

1. Copy `templates/QUEUE.md` to `tasks/QUEUE.md`
2. Adjust window times in queue file (default: 8 AM - 8 PM UTC)
3. Autonomy works only during active window
4. Overnight: no autonomy, only cron jobs

---

## Slowly Evolve Approach

**Week 1-2:** Conservative, 4 sessions/day, limited window
**Week 3-4:** Expand, 6 sessions/day, full day window
**Month 2+:** Optimize, tailor window to RA's schedule

---

## Files

- `SKILL.md` - Full documentation and usage guide
- `templates/QUEUE.md` - Queue template with window configuration
- `templates/HEARTBEAT.md` - Heartbeat template for time-windowed work

---

## Usage

1. Copy `templates/QUEUE.md` to `tasks/QUEUE.md`
2. Copy `templates/HEARTBEAT.md` to `HEARTBEAT.md` (or integrate into existing)
3. Adjust window times in queue file (default: 8 AM - 8 PM UTC)
4. Autonomy works only during active window
5. Overnight: standby mode (HEARTBEAT_OK only, no work)

---

*See `autonomy-type-based` sister skill for type-based autonomy*
