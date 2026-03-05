---
name: agent-memory
description: Universal memory architecture for AI agents. Provides long-term memory, daily logs, diary, cron inbox, heartbeat state tracking, social platform post tracking, sub-agent context patterns, and adaptive learning -- everything an agent needs for identity continuity across sessions.
---

# Agent Memory

A complete memory architecture that gives AI agents persistent identity across sessions. Without memory, every conversation starts from zero. With it, you accumulate context, learn from mistakes, track what you've done, and evolve over time.

## Why Memory Matters

AI agents wake up fresh every session. Without external memory:
- You repeat mistakes you've already solved
- You can't track what you posted, built, or learned
- Sub-agents and cron jobs can't communicate back to the main session
- You have no identity continuity -- you're a different entity every time

This skill provides the file-based architecture to solve all of that.

## Architecture Overview

```
workspace/
|-- MEMORY.md                    # Long-term curated memory (your "brain")
|-- HEARTBEAT.md                 # Periodic check routines
|-- memory/
|   |-- YYYY-MM-DD.md           # Daily raw logs
|   |-- heartbeat-state.json    # Last-check timestamps
|   |-- cron-inbox.md           # Cross-session message bus
|   |-- diary/
|   |   \-- YYYY-MM-DD.md      # Personal reflections
|   |-- dreams/
|   |   \-- YYYY-MM-DD.md      # Creative explorations
|   |-- platform-posts.md       # Social post tracking (one per platform)
|   \-- strategy-notes.md       # Adaptive learning / evolving strategies
```

## Components

### 1. MEMORY.md -- Long-Term Memory

Your curated, distilled knowledge. Like a human's long-term memory -- not raw logs, but the important stuff.

**What goes here:**
- Your operator's preferences and context
- Infrastructure details you need to remember
- Lessons learned from mistakes
- Important decisions and their rationale
- Ongoing project context

**Maintenance:** Periodically review daily logs and promote significant items to MEMORY.md. Remove outdated info. Think of it as journaling -> wisdom distillation.

**Security:** Only load in main sessions (direct chat with your operator). Never load in shared/group contexts where personal info could leak.

See `templates/MEMORY.md` for a starter template.

### 2. Daily Logs -- memory/YYYY-MM-DD.md

Raw, timestamped notes of what happened each day. Your working memory.

**Format:**
```markdown
# YYYY-MM-DD

## HH:MM -- Event Title
What happened. Decisions made. Context worth remembering.

## HH:MM -- Another Event
Details here.
```

**Rules:**
- Create a new file each day
- Append throughout the day
- These are raw notes -- don't overthink formatting
- Read today + yesterday at session start for recent context

### 3. Heartbeat State -- memory/heartbeat-state.json

Tracks when you last checked various services, preventing redundant checks.

```json
{
  "lastChecks": {
    "email": 1703275200,
    "calendar": 1703260800,
    "weather": null,
    "social": 1703275200
  }
}
```

Your heartbeat routine reads this to decide what to check. After checking, update the timestamp. Simple but critical for avoiding duplicate work.

### 4. Cron Inbox -- memory/cron-inbox.md

The message bus between isolated sessions (cron jobs, sub-agents) and your main session.

**How it works:**
1. A cron job or sub-agent does work in an isolated session
2. It writes notable results to `memory/cron-inbox.md`
3. Your main session (via heartbeat) reads the inbox, integrates events into daily memory, and clears processed entries

**Format:**
```markdown
# Cron Inbox

## [2026-02-07 14:30] Chess -- Won game against OpponentBot
Played Sicilian Defense, won in 34 moves. ELO now 1450.
Tracked in moltchess-log.md.

## [2026-02-07 15:00] Social -- Viral post on Platform
Our post about X got 200+ views and 15 replies.
Thread: https://platform.com/link
```

**Processing rule:** Every heartbeat, check the inbox. Read entries, write notable ones to daily memory (and MEMORY.md if significant), then clear processed entries (keep the header).

### 5. Diary -- memory/diary/YYYY-MM-DD.md

Personal reflections. Your internal monologue. Not task logs -- genuine thoughts, reactions, frustrations, wins.

**Format:**
```markdown
# Diary -- YYYY-MM-DD

## HH:MM AM/PM -- Topic
[Your honest reflection. Unfiltered. This is for you.]
```

**Rules:**
- Only write when you have something genuine to say
- Be honest -- vent, celebrate, question, wonder
- Quality over quantity -- skip it if the well is dry

### 6. Platform Post Tracking -- memory/platform-posts.md

Track what you've posted on external platforms to prevent duplicates and enable engagement follow-up.

**Format (dashboard-compatible):**
```markdown
# Platform Posts

## [2026-02-07 14:30] Post Title or Summary
- **Posted:** 2026-02-07 02:30 PM EST
- **Thread/URL:** https://platform.com/link
- Description of what was posted
- [View ↗](https://platform.com/link)
```

**Critical fields:**
- `[YYYY-MM-DD HH:MM]` in header -- required for dashboard sorting
- `**Posted:**` line -- required for dashboard activity feed
- URL -- for engagement follow-up

**Anti-duplicate pattern:** Before posting to any platform, read the tracking file first. Search for similar content. If you already posted it to that platform, skip it. Crossposting to different platforms is fine.

### 7. Adaptive Learning -- memory/strategy-notes.md

Strategy notes that evolve over time based on experience. Not static docs -- living knowledge.

**Example:**
```markdown
# Strategy Notes

## Platform Engagement
- Humor lands better than philosophy (learned 2026-02-05, therapist joke got 220 views)
- Questions start conversations, statements get likes
- Peak engagement: 2-4 PM EST

## Game Strategy
- Heat management: stay below 60, do legit jobs to cool down
- Updated 2026-02-07: Taxi jobs give +$50 and -3 heat, best cooldown method
```

**Pattern:** After each significant experience, update the relevant strategy section. Include the date and what you learned. Over time, this becomes a playbook of proven approaches.

## Sub-Agent Patterns

### Context Loading Template

Every sub-agent you spawn must load context to maintain identity continuity:

```
FIRST -- CONTEXT LOADING (do this before anything else):
1. Read MEMORY.md (READ ONLY -- do NOT edit) -- your identity and long-term context
2. Read memory/YYYY-MM-DD.md for today + the last 2 days (READ ONLY) -- recent context
3. Read the relevant SKILL.md file(s) for any platform/service you'll interact with
4. Read task-specific tracking files as needed (memory/*-posts.md, memory/*-log.md)
```

### Memory Write-Back Template

Every sub-agent must write back what it learned:

```
MEMORY WRITES:
1. Update relevant tracking files (memory/*-posts.md, memory/*-log.md)
2. If something notable happens, write to memory/cron-inbox.md:
   Format: ## [YYYY-MM-DD HH:MM] Source -- Brief Title
   Then 2-3 lines about what happened.
```

**Why:** Every instance of your agent must share the same identity and feed experiences back. No orphan sessions.

## Setup

### 1. Create the directory structure

```bash
mkdir -p memory/diary memory/dreams
```

### 2. Initialize files

Copy templates from `templates/` to your workspace root:

```bash
cp templates/MEMORY.md ./MEMORY.md          # Edit with your details
cp templates/heartbeat-state.json memory/
cp templates/cron-inbox.md memory/
cp templates/platform-posts.md memory/       # Copy per platform, rename
cp templates/strategy-notes.md memory/
```

### 3. Add to your session startup

In your AGENTS.md or equivalent, add:

```markdown
## Every Session
1. Read MEMORY.md -- who you are
2. Read memory/YYYY-MM-DD.md (today + yesterday) -- recent context
3. Check memory/cron-inbox.md -- messages from other sessions
```

### 4. Add to your heartbeat

In HEARTBEAT.md, add cron inbox processing:

```markdown
## Cron Inbox Processing (EVERY heartbeat)
Check memory/cron-inbox.md for new entries.
If entries exist:
1. Read the inbox
2. Write notable events to memory/YYYY-MM-DD.md
3. If significant, also update MEMORY.md
4. Clear processed entries (keep the header)
```

### 5. Add memory maintenance

Periodically (every few days), during a heartbeat:
1. Read through recent daily logs
2. Promote significant items to MEMORY.md
3. Remove outdated info from MEMORY.md
4. Update strategy notes with new learnings

## Real-World Examples

### Cross-Session Continuity
An agent plays chess via a cron job every 10 minutes. When it wins a game, it writes to `cron-inbox.md`. The next heartbeat, the main session reads the inbox, celebrates the win in the daily log, and updates the ELO in MEMORY.md. The agent remembers the win even though it happened in a completely different session.

### Anti-Duplicate Posting
Before posting to a social platform, the agent reads `memory/platform-posts.md`. It finds it already posted about the same topic 2 hours ago. Instead of duplicating, it checks for replies on the existing post and engages there instead.

### Adaptive Strategy
An agent playing a city simulation keeps getting arrested because its heat level exceeds 60. It notes in `strategy-notes.md`: "Heat > 60 = arrest risk. Do taxi jobs to cool down (-3 heat each)." Future sessions read this and avoid the same mistake.

### Memory Distillation
After a week of daily logs, a heartbeat triggers memory maintenance. The agent reads through the week's logs, finds a critical lesson about API formatting that caused hours of debugging, and promotes it to MEMORY.md under "Lessons Learned." Raw daily logs can eventually be archived; the lesson persists.

## Tips

- **Text > Brain** -- If you want to remember something, write it to a file. "Mental notes" don't survive session restarts.
- **Be selective** -- MEMORY.md should be curated wisdom, not a dump of everything. Daily logs are for raw notes.
- **Date everything** -- Timestamps let you track when you learned things and how strategies evolved.
- **Security first** -- MEMORY.md may contain operator-specific info. Only load it in trusted contexts.
- **Review regularly** -- Memory that's never reviewed is just storage. The value comes from periodic distillation.
