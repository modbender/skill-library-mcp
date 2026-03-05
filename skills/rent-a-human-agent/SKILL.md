---
name: rent
triggers: "hire a human, rent a human, delegate to human, find a freelancer, post a bounty, hire someone, human assistant, errands, rentahuman, bounty"
description: "Delegate tasks to real humans via RentAHuman.ai — search skills, post bounties, manage conversations, and run AI-scored opportunity scans."
---

# Rent-A-Human Bounty Hunter

Scans RentAHuman.ai bounties via MCP + API. Uses Grok AI to filter spam,
score opportunities by location, skills, and ease of completion, and sends
top results to Telegram.

🔍 Scan Bounties - Find and score job opportunities based on your location and skills

🧑‍💼 Browse Humans - View available humans for hire with skills and rates

💼 View Bounties - See open jobs and opportunities

📝 Post Jobs - Create new bounties directly from Telegram

🎯 Smart Scanning - AI-scored opportunity recommendations

🔒 Private - Bot only responds to your user ID

🔗 MCP + API Integration - Direct connection to official RentAHuman.ai MCP

Rent-A-Human MCP Server Integration: Full agentic access to the RentAHuman.ai platform

CLI Interface: Fully customizable /rent agent mode

AI-Powered Scoring: Uses Grok-4-1-fast-reasoning to score job opportunities on a scale of 0-100

Smart Caching: Caches results for 12 hours to avoid redundant API calls

Telegram Integration: Sends top opportunities directly to your Telegram

Drag & Drop Skills: Compatible with Claude Code and OpenClaw — drop the .claude/skills/ folder into any project

Multiple Scan Modes:

Cached mode (fast, uses existing scores)
Force fresh scoring (bypass cache)
List all open jobs
List available humans for hire

## Requirements
- `XAI_API_KEY` — from x.ai for Grok scoring
- `RENTAHUMAN_API_KEY` — from rentahuman.ai/dashboard
- `TELEGRAM_BOT_TOKEN` (optional) — for Telegram notifications
- `TELEGRAM_CHAT_ID` (optional) — for Telegram notifications

# Rent-A-Human Skill

Auto-activate when the user wants to hire a person, post a job, or delegate a task that needs a human.

## Quick Commands

```
/rent              — Browse + print command menu
/rent scan         — AI-scored bounties (Grok, 12hr cache)
/rent scan force   — Bypass cache, fresh scoring now
/rent scan new     — Only unseen bounties
/rent post <desc>  — Post a new bounty (first sentence = title)
/rent saved        — View saved bounties
/rent skills       — List available human skills
/rent status       — Connection check
```

## Hire Flow

**Direct:** `/rent search <skill>` → `/rent human <id>` → `/rent talk <id> : msg` → negotiate → book  
**Bounty:** `/rent post desc` → humans apply → `/rent applications <id>` → `/rent accept <app_id>`

## Bounty Scanner

Script: `python3 .claude/skills/rent/scripts/bounty_hunter.py`  
Cache: `logs/bounties_cache.json` (12hr TTL, Grok-3-mini-fast scoring 0–100)  
After running: read cache file and display scored results to user.

## Rate Limits

Bounties: 5/day | Conversations: 50/day | Messages: 30/hr | API keys: 3 max

## CLI Alternative

```bash
python hire_team.py "Task description"
python hire_team.py talk <human_id> "Message"
python hire_team.py bounty "Title" --description "..." --price 100 --hours 2
```

**Note:** `hire_team.py` is an optional external CLI. Primary interface is MCP via `/rent` commands.

Payment via Stripe Connect escrow on RentAHuman.ai.

→ Full command tree + MCP tool map: [`.claude/commands/rent.md`](.claude/commands/rent.md)
