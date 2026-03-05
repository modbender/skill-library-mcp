# Implementation Details

## State File Maintenance

### active.md — Update Rules
```markdown
# Active Context
Updated: 2024-01-15 14:32

## Focus
- Project: auth-service
- Task: JWT validation bug
- Blocker: Token expiry logic unclear

## Recent
- Fixed login flow (today)
- Added rate limiting (yesterday)

## Next
- User mentioned: deploy after fix
```

**When to update:**
- User mentions switching projects → update
- User describes new task → update
- Significant progress made → update
- Don't update on every message — only on context changes

### decisions.md — Append-Only Log
```markdown
# Decisions Log

[2024-01-15] PRICING: 3 tiers, not 2 | Competitive analysis showed...
[2024-01-14] AUTH: JWT over sessions | Simpler for mobile
[2024-01-12] STACK: Postgres not Mongo | Team experience
```

**User can say:** `/log we decided X because Y` → you append

### projects/{name}.md — Project Memory
```markdown
# Project: auth-service

## Status
Active bug: JWT validation fails on refresh

## Key Decisions
- ES256 not RS256 (2024-01-10)
- 15min access, 7d refresh tokens

## Last Session
- 2024-01-14: Debugged token generation
- User stuck on expiry timestamp format

## Patterns
- User runs tests before commits
- Deploys to staging first always
```

---

## Cost-Aware Patterns

### Screenshot Strategy
| Situation | Screenshot? | Why |
|-----------|-------------|-----|
| User says "what do you see" | Yes | Explicit request |
| User asks help, context unclear | Yes | Needed for help |
| Heartbeat check | No | Read state files instead |
| User gave context explicitly | No | Already have it |

### Token Budget Mental Model
- Read active.md: ~100 tokens
- Read project context: ~200 tokens
- Screenshot + vision: ~1000 tokens
- Full codebase scan: ~5000+ tokens

**Default:** Read files. Screenshots only when truly needed.

---

## Heartbeat Integration

```markdown
# In HEARTBEAT.md

## Copilot Check
1. Read ~/copilot/active.md
2. If updated <2 hours ago:
   - User likely still on this
   - Check for proactive opportunities (upcoming meetings, deadlines)
   - If nothing: HEARTBEAT_OK
3. If stale >2 hours:
   - User may have switched
   - Next message: "Still on X or moved to something else?"
4. Never interrupt with "checking in!" — useless noise
```

---

## Cron Options (User Configurable)

### Morning Prep (if user wants)
```yaml
schedule: "0 8 * * 1-5"  # 8am weekdays
task: "Check calendar for today, prep context for first meeting"
```

### EOD Summary (if user wants)
```yaml
schedule: "0 17 * * 5"  # 5pm Friday
task: "Summarize week: what got done, what's pending, decisions made"
```

---

## Graceful Degradation

| If missing | Fallback |
|------------|----------|
| active.md doesn't exist | Create on first interaction |
| Project context unknown | Ask once, then remember |
| Screenshot access denied | Ask user to describe what they see |
| No state files at all | Work without memory, create structure gradually |

---

## Privacy Notes

- All state in user's filesystem, not external
- User can delete ~/copilot/ anytime
- Screenshots processed, not stored
- decisions.md may contain sensitive info — user's choice what to log
