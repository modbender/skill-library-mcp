# QA Gates

> Every deliverable passes through a gate before reaching the human or going external.

## Gate 0: Verify Implementation, Not Intent
- ✅ Did the mechanism change, or just the text?
- ✅ Can you observe the new behavior?
- ✅ Text changes ≠ behavior changes. "Done" means tested and working.

## Gate 1: Internal Only (workspace files, memory, commits)
- ✅ File exists and is non-empty
- ✅ No placeholder text (TODO, TBD, Lorem ipsum)
- Auto-pass — lowest risk

## Gate 2: Human-Facing (briefings, summaries, task updates)
- ✅ Gate 1 checks
- ✅ Concise — no filler, no sycophancy
- ✅ Structured — headers, bullets, clear flow
- ✅ Actionable — ends with next step or decision point
- ✅ Accurate — facts verified, no hallucinated stats
- ✅ Scannable in 30 seconds

## Gate 3: External-Facing (emails, posts, client materials)
- ✅ Gate 2 checks
- ✅ Recipient-appropriate tone
- ✅ No internal context leaked (no agent names, memory files, system details)
- ✅ No private data unless explicitly requested
- ✅ Links verified
- ✅ Proofread
