---
name: session-wrap-up
description: Wrap up a conversation session before starting a new one. Use when the user says "wrap up", "wrap up this conversation", "session wrap up", or uses /session_wrap_up command. Flushes context to memory files, updates PARA notes, commits changes, and provides a summary.
---

# Session Wrap Up

End-of-session protocol to preserve context and ensure continuity between sessions.

## When Triggered

Run this protocol when the user indicates they want to wrap up the current session before starting a new one.

## Protocol Steps

Execute these steps in order:

### 1. Flush to Daily Log

Write to `memory/YYYY-MM-DD.md` (create if doesn't exist):
- Key topics discussed in this session
- Decisions made
- Commands, configs, or code that worked
- Problems solved and how they were solved
- Any gotchas or lessons learned

### 2. Update Long-Term Memory

If significant learnings occurred, update `MEMORY.md`:
- New user preferences discovered
- Important lessons learned
- Long-term decisions made
- Workflow changes

### 3. Update PARA Notes

Check and update the PARA structure in `notes/` (or `memory/notes/`):
- **Open loops** (`notes/areas/open-loops.md`): Add new unfinished items, mark completed items with ✅
- **Projects** (`notes/projects/`): Update progress on active projects
- **Areas** (`notes/areas/`): Add new ongoing responsibilities
- **Resources** (`notes/resources/`): Add new reference material, how-tos

### 4. Commit Changes

```bash
cd <workspace>
git add -A
git status
git commit -m "wrap-up: YYYY-MM-DD session summary"
git push
```

Notes:
- The wrap-up `git push` is **automatic** (no confirmation prompt).
- If `git push` fails, report the error and leave the commit locally.

### 5. Report Summary

Provide a brief summary to the user:
- What was captured
- Files updated
- Any items that need follow-up next session
- Confirmation that changes were committed (and pushed, if successful)

## Example Output

```
## Session Wrap-Up Complete ✅

**Captured to daily log:**
- Configured PARA second brain
- Fixed vector indexing for notes
- Set up weekly memory review cron

**Updated:**
- MEMORY.md: Added memory system learnings
- notes/areas/open-loops.md: Marked .gitignore task complete

**Committed:** `wrap-up: 2026-01-30 session summary`

**Follow-up next session:**
- Check LanceDB autoCapture setting
- Consider morning briefing cron

Ready for new session! ⚡
```

## Notes

- Always create the daily log file if it doesn't exist
- Use the current date for filenames and commit messages
- Keep summaries concise but complete
- Include the ⚡ emoji at the end (GigaBot signature)
