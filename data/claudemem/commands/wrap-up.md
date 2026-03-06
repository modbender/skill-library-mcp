---
description: End-of-session save — captures all important knowledge + session summary in one step
argument-hint: Optional session title
---

Wrap up this conversation by saving everything important to persistent memory.

## What This Command Does

This is the **all-in-one end-of-session** command. It does three things:

### Step 1: Extract and Save New Knowledge (Notes)

Review the ENTIRE conversation and identify important knowledge fragments that should persist:
- API specs, endpoints, rate limits discovered
- Technical decisions made (and why)
- Bugs resolved and their root causes
- Configuration quirks or gotchas found
- User preferences learned

**For each knowledge fragment:**
1. Search first: `claudemem note search "<key phrase>" --format json`
2. If already saved → **skip** (or append if there's genuinely new info: `claudemem note append <id> "new detail"`)
3. If not saved → create: `claudemem note add <category> --title "..." --content "..." --tags "..."`

Track what you saved, skipped, and updated.

### Step 2: Generate and Save Session Summary

Generate a structured session summary covering:
- **Summary**: What was accomplished (1-2 paragraphs)
- **Key Decisions**: Choices made with rationale
- **What Changed**: Files modified (if any coding was done)
- **Problems & Solutions**: Issues and resolutions
- **Questions Raised**: Open items for future sessions
- **Next Steps**: Follow-up tasks

Save it:
```bash
printf '<session markdown>' | claudemem session save \
  --title "<title>" \
  --branch "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')" \
  --project "$(pwd)" \
  --session-id "$(date +%Y%m%d-%H%M%S)" \
  --tags "<tags>"
```

### Step 3: Show Summary Report

Display a clean summary of everything that was saved:

```
📦 Wrap-up complete!

📝 Notes:
  ✅ Saved: "TikTok Rate Limits" → api-specs
  ✅ Saved: "CORS Docker Quirk" → quirks
  ⏭️ Skipped: "Alembic Steps" (already stored)
  📎 Updated: "FastAPI Conventions" (appended new info)

📋 Session:
  ✅ "Implement TikTok Search API" (feat/tiktok, 2026-02-21)

📊 Memory: 15 notes, 5 sessions total
```

## Important Rules

- **Never save duplicates**: Always search before saving. When in doubt, skip rather than duplicate.
- **Be selective**: Only save information with lasting value. Skip temporary debugging or transient state.
- **Categorize well**: Use existing categories when possible (`claudemem note categories` to check).
- **Keep it concise**: Each note should be a focused, fact-dense fragment — not a brain dump of the entire conversation.
