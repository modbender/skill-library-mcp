# Type-Based Autonomy

**Task-type-filtered autonomous work queue.**

---

## Overview

The agent pulls from `tasks/QUEUE.md` but **only works on specific task types**:

- ✅ **Research** (`@type:research`) - Information gathering, investigation
- ✅ **Writing** (`@type:writing`) - Content creation, documentation
- ✅ **Analysis** (`@type:analysis`) - Data review, metrics, patterns

- ❌ **Maintenance** (`@type:maintenance`) - Cron handles cleanup, backup
- ❌ **Backup** (`@type:backup`) - Scheduled by cron
- ❌ **Security** (`@type:security`) - Monthly audit by cron

---

## When to Use

- You want **focused autonomous work** on value-add tasks (research/writing/analysis)
- You want **maximum token efficiency**
- Tasks can be **clearly categorized by type**
- You want to **expand task types later** (add coding, testing, etc.)

---

## Quick Start

1. Copy `templates/QUEUE.md` to `tasks/QUEUE.md`
2. Add tasks with `@type:` labels
3. Autonomy works by filtering queue types
4. Cron handles maintenance separately

---

## Files

- `SKILL.md` - Full documentation and usage guide
- `templates/QUEUE.md` - Queue template with type labels
- `templates/HEARTBEAT.md` - Heartbeat template for proactive queue pulling

---

## Usage

1. Copy `templates/QUEUE.md` to `tasks/QUEUE.md`
2. Copy `templates/HEARTBEAT.md` to `HEARTBEAT.md` (or integrate into existing)
3. Add tasks with `@type:` labels (research, writing, analysis)
4. Autonomy works by filtering queue types on each heartbeat
5. Cron handles maintenance separately

---

*See `autonomy-windowed` sister skill for time-based autonomy*
