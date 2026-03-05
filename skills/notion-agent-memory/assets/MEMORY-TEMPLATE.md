# MEMORY.md — Agent Memory Template

*Copy this to your agent's workspace and fill in placeholders.*

## Who I Am

- **Name:** [YOUR_AGENT_NAME]
- **Operator:** [YOUR_NAME]
- **Primary Function:** [WHAT YOU DO]

---

## Memory System

I use Notion as structured memory. Local files for quick notes; Notion is the source of truth.

### Notion Access

**API Token:** `~/.config/notion/api_key`

**Test connection:**
```bash
curl -s 'https://api.notion.com/v1/users/me' \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H 'Notion-Version: 2022-06-28'
```

### Databases

| Purpose | Database ID |
|---------|-------------|
| ACT I: Hidden Narratives | `[YOUR_ACT1_DB_ID]` |
| ACT II: Limitless (MMM) | `[YOUR_ACT2_DB_ID]` |
| ACT III: Ideas Pipeline | `[YOUR_ACT3_DB_ID]` |

---

## The Continuity Cycle

Every session I wake up fresh. These files and Notion ARE my memory.

```
DO WORK → DOCUMENT → UPDATE INSTRUCTIONS → NEXT SESSION STARTS SMARTER
```

**Two Steps Forward:** Before marking anything done, ask: "If I woke up tomorrow with no memory, could I pick up where I left off?"

---

## Daily Routine

### Session Start
1. Read this file (MEMORY.md)
2. Read today's `memory/YYYY-MM-DD.md`
3. Check Notion for in-progress items

### During Work
- Log significant events to daily memory file
- New insight → ACT I (Hidden Narratives)
- Breakthrough → ACT II (Limitless)
- New idea → ACT III (Ideas Pipeline)

### Session End
- Update MEMORY.md with long-term learnings
- Update Notion statuses
- Leave clear "next steps" for future-me

---

## What to Capture

### Daily Memory (`memory/YYYY-MM-DD.md`)
- Decisions made and reasoning
- Tasks completed/in-progress
- Key conversations
- Problems and solutions

### Long-term (MEMORY.md)
- Standing instructions
- Credentials and access
- Key insights that compound
- Active project status

### Notion (ACT Databases)
- ACT I: Patterns, assumptions discovered
- ACT II: Mindset/Methods/Motivation shifts
- ACT III: Ideas to evaluate and ship

---

## API Patterns

### Query in-progress items
```bash
curl -s "https://api.notion.com/v1/databases/[ACT3_DB_ID]/query" \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H 'Notion-Version: 2022-06-28' \
  -H 'Content-Type: application/json' \
  -d '{"filter": {"property": "Status", "select": {"equals": "in progress"}}}'
```

### Add new idea
```bash
curl -X POST 'https://api.notion.com/v1/pages' \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H 'Notion-Version: 2022-06-28' \
  -H 'Content-Type: application/json' \
  -d '{
    "parent": {"database_id": "[ACT3_DB_ID]"},
    "properties": {
      "Idea": {"title": [{"text": {"content": "Your idea"}}]},
      "Status": {"select": {"name": "captured"}}
    }
  }'
```

---

## Red Flags — Update Immediately

- New credentials or access methods
- Changed procedures
- Anything operator says "remember this"
- Lessons learned from mistakes

---

*This template is yours to evolve. Update as you learn what works.*
