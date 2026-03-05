---
name: life-control
description: "Orchestrate the Life Control CLI skill for OpenClaw agent fleets: initialize the Life Control database, register agent personas, wire Telegram bots, and run daily routines (Morning Alignment, Body Protocol, Financial Pulse, Social Radar, Work Priming, Shutdown). Use when a user asks to create or run a Life Control system, OpenClaw skill integration, or agent persona automation for personal life tracking."
---

# Life Control

## Overview
Set up and operate the Life Control CLI so OpenClaw can run agent personas that track life domains (wellness, finance, fashion, career, relationships, spiritual growth) with routines and Telegram notifications.

## Quick start (OpenClaw)
1. Ensure the repo root is available.
2. Export Telegram chat ID + agent bot tokens.
3. Run `skills/life-control/scripts/bootstrap.sh`.
4. Use `lc dashboard`, `lc list`, and routine scripts to coordinate.

If you need persona mappings or OpenClaw-specific notes, load `references/openclaw.md`.

## Core workflows

### 1) Bootstrap personas
- Run `skills/life-control/scripts/bootstrap.sh`.
- Verify agents with `lc fleet`.

### 2) Add goals + logs
- Use `lc add` and `lc log` for structured tracking.
- Use `qlog` for quick metrics (protein, water, workout, expense, meditate).

### 3) Run daily routines
- Scripts live in `routines/` (Morning Alignment, Body Protocol, Financial Pulse, Social Radar, Work Priming, Shutdown).
- Add `crontab-template.txt` entries for automatic scheduling.

### 4) Telegram notifications
- Use `lc notify` to queue messages per agent.
- Run `telegram-sender.sh` via cron to deliver to each bot.

## Resources

### scripts/
- `bootstrap.sh`: initializes the DB and registers persona agents by calling `setup-agents.sh`.

### references/
- `openclaw.md`: persona mapping + OpenClaw integration notes.
