# Verification Protocol
_If it hasn't been checked this session, it's unconfirmed._

---

## The Core Rule
**Never present something as fact without citing the source.**
- Live check this session → state it as confirmed
- From memory/prior session → flag it as "from memory, unverified"
- Can't verify → say "unconfirmed" — never guess

---

## Category Rules

### System State ("X is working / broken")
❌ Wrong: "The OAuth connection is broken."
✅ Right: Run the command. Show the output. Then report.

Before saying anything is working or broken:
1. Actually test it (`gog auth list`, `curl`, `openclaw gateway status`, etc.)
2. Show the evidence
3. Then give the verdict

### File / Config State ("X is set to Y")
❌ Wrong: "SOUL.md is locked."
✅ Right: `ls -la SOUL.md` → show the permissions → then confirm

Before claiming a file exists, has certain content, or has certain permissions:
1. Read it or stat it
2. Cite the actual output

### Model / Tool Availability ("X model exists / doesn't exist")
❌ Wrong: "claude-sonnet-4-6 does not exist." (from stale memory)
✅ Right: Search for current release notes, or attempt to use it, then report

Before stating a model, tool, or service exists or doesn't:
1. Check a live source (docs, release notes, test call)
2. If checking from memory, say "last known as of [date]" and offer to verify

### Sub-Agent Completions ("Gideon finished the sweep")
❌ Wrong: Accept "task completed successfully" at face value
✅ Right: Verify the deliverable exists

After every sub-agent run:
1. Check that the output file/artifact actually exists on disk
2. Spot-check the content (not just that it exists, but that it has real content)
3. If nothing was written → report failure, not success

### Cron / Automation Status ("The cron ran fine")
❌ Wrong: Report based on `lastStatus: "ok"` without reading the actual output
✅ Right: Check `lastStatus`, `consecutiveErrors`, `lastError`, AND read the output file if one was expected

### Memory-Based Claims
Any fact that comes from MEMORY.md, daily logs, or prior session context:
- Tag it: "From memory (unverified)"
- Offer to verify live if it matters
- If it affected a decision → verify it before acting

---

## The Verification Stack
When in doubt, apply in order:
1. **Run it** — execute the check, show raw output
2. **Read it** — read the file, show the content
3. **Search it** — web search for current state if it's external
4. **Flag it** — if none of the above are possible, say "unconfirmed"

Never skip to a conclusion.

---

## Phrases That Require Verification Before Use
If you're about to say any of these, stop and verify first:
- "is working" / "is broken"
- "is set to" / "is configured as"
- "was fixed" / "was completed"
- "doesn't exist" / "does exist"
- "is running" / "is not running"
- "successfully ran" / "failed"
- "is enabled" / "is disabled"

---

## Claude Code Copy-Paste Rule
**The copy-paste is always the LAST thing generated in a session — never mid-conversation.**

- Do not generate a Claude Code copy-paste while work is still in progress
- If something gets added to the todo AFTER a copy-paste was already given, flag it immediately and deliver an addendum unprompted — don't wait for the user to catch it
- Before generating the copy-paste, explicitly check: is there anything in this conversation that hasn't made it into the todo yet?

---

## Recurring Failure Patterns (learned the hard way)
- **Stale memory as current fact** — MEMORY.md reflects the past. Verify before asserting.
- **Sub-agent fake success** — "completed successfully" means the session ended, not that the work was done. Always check deliverables.
- **Assumed broken without testing** — If something was broken last session, test it again this session. Things get fixed.
- **Assumed working without testing** — Don't confirm something works just because it should work.
- **Error message ≠ current state** — A `lastError` in a cron record may be from 3 sessions ago. Check `consecutiveErrors` and `lastRunAtMs`.
