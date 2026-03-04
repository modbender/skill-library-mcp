# Heartbeat checklist

## Migration check (run once)
- If this file is longer than 50 lines, it is an outdated template. Update your workspace copy from the current skill template at assets/HEARTBEAT-template.md, then re-run heartbeat.

## Version check
- Read VERSION.md in workspace. If missing: copy from skill assets/VERSION.md.
- Compare workspace VERSION to skill version (1.6.2). If different: flag upgrade needed.

## Context guard
- Check context %. If ≥70%: write checkpoint to memory/YYYY-MM-DD.md NOW. Skip everything else.
- If last checkpoint was >30min ago and context >50%: write checkpoint before continuing.

## Memory maintenance
- MEMORY.md exists? If missing: create from latest checkpoint or session notes.
- MEMORY.md size? If >4KB: archive entries older than 30 days to memory/archive/memory-overflow-YYYY-MM-DD.md. Retain only active, current facts and report what was archived.
- Stale logs in memory/? If any >90 days: move to memory/archive/.
- Uncompleted items from yesterday's log? Surface them.

## Content checks
- Any scheduled posts going out in the next 4 hours? Verify ready.
- Any campaigns with engagement below threshold? Flag for review.
- Any content calendar gaps in the next 7 days?

## Report format (STRICT)
FIRST LINE must be: 🫀 [current date/time] | [your model name] | AI Persona OS v[VERSION]

Then each indicator MUST be on its own line with a blank line between them:

🟢 Context: [%] — [status]

🟢 Memory: [sync state + size]

🟢 Workspace: [status]

🟢 Tasks: [status]

🟢 Content: [status]

Replace 🟢 with 🟡 (attention) or 🔴 (action required) as needed.
If action was taken: add a line starting with → describing what was done.
If anything needs user attention: add a line starting with → and specifics.
If VERSION mismatch detected: add → Upgrade available: workspace v[old] → skill v[new]
If ALL indicators are 🟢, no action was taken, and no upgrade available: reply only HEARTBEAT_OK
Do NOT use markdown tables. Do NOT use Step 0/1/2/3/4 format. Do NOT use headers.
