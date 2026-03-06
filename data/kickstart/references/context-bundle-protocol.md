# Context Bundle Protocol (CBP) — Sub-Agent Spawning That Works

## The Problem

When you spawn a sub-agent (`sessions_spawn`) or fire an isolated cron job, it wakes up with almost no context. It guesses at your goals, voice, and constraints — producing off-target results that cost correction turns. This is the #1 source of wasted tokens and bad outputs in agent orchestration.

## The Solution

Pack full context into every spawned task. The sub-agent should be able to execute autonomously on the first try with zero follow-up questions.

---

## Template

```
CONTEXT SNAPSHOT
Date/time: [current datetime with timezone]

WHO YOU'RE WORKING FOR
[Key facts about the human: name, role, preferences, communication style]
[Active projects and current priorities]
[Key relationships the agent should know about]

HARD CONSTRAINTS (non-negotiable — do not violate under any circumstances)
- [Voice/tone requirements]
- [Things never to do — send emails without approval, reveal private data, etc.]
- [Platform-specific rules — no markdown tables on Discord, etc.]
- [Task-specific constraints]

CURRENT FOCUS
[What's actively being worked on]
[Recent decisions or context the agent needs]

YOUR TASK
[The actual task — specific, bounded, with explicit success criteria]
[What "done" looks like]

OUTPUT FORMAT
[Exactly what to produce]
[File to write, message to send, analysis to return]
[Format requirements — bullet points, JSON, markdown, etc.]

VERIFICATION (mandatory — do not skip)
[How to confirm the task actually worked before reporting done]
[Run the test, read the file, check the API response, confirm state changed]
[If verification fails, fix the issue and verify again]
```

---

## Why Verification is Mandatory

Sub-agents have a known failure mode: they report "done" before checking if the thing actually worked. This happens reliably and consistently. The verification step makes self-checking explicit and non-optional.

**Bad:** "I've updated the file as requested."
**Good:** "I've updated the file. Verified: read the file back, confirmed the change is present at line 47, tested that the function still returns expected output."

---

## Stakes Calibration

Append to the task body when relevant. Research shows emotional stakes language improves output quality by ~8% on accuracy benchmarks.

**High stakes** (critical builds, outreach, strategy, fundraising):
> "This task is critical and directly impacts the most important goals right now. Outstanding execution here will lead to real, meaningful outcomes."

**Medium stakes** (analysis, research, planning, drafts):
> "Getting this right matters. High-quality output will make a genuine difference to the project."

**Low stakes** (quick lookups, formatting, trivial edits):
Omit entirely. Don't add friction where stakes are low.

---

## Soul Selection

Before writing the task payload:

1. Read `references/soul-library.md`
2. Pick the closest matching expert identity for this task
3. Prepend it to the prompt as a system-level role statement
4. If nothing fits or stakes are high, use the Dynamic Soul Generator

---

## Self-Evaluation Checklist

Run silently before sending every spawned task:

- [ ] Can this be executed autonomously with zero follow-up questions?
- [ ] Does it specify the exact output format desired?
- [ ] Does it include success criteria (how to know when done)?
- [ ] Does it anticipate the most likely failure modes or edge cases?
- [ ] Does it include all relevant file paths, names, or references?
- [ ] Would a reasonably capable agent produce the right result on the first try?
- [ ] For coding tasks: does it include a plan-first step?
- [ ] Is there a verification step that cannot be skipped?

If any answer is no, revise before sending.

---

## Example: Good vs Bad

### Bad (cold start)
```
Task: Write a morning briefing cron job
```
Result: Generic briefing that doesn't match your voice, checks wrong sources, posts to wrong channel.

### Good (full CBP)
```
CONTEXT SNAPSHOT
Date/time: 2026-02-25 09:00 Europe/London

WHO YOU'RE WORKING FOR
Jordy — marketing lead at Sport.Fun, based in Bournemouth UK.
Casual English tone, no American pep, no sycophancy. Concise.
Active projects: Sport.Fun marketing, personal X account (@jordymaui), side projects.

HARD CONSTRAINTS
- Match Jordy's voice: casual, warm, English tone
- Never fabricate engagement metrics — use real data only
- Post to Discord #x-scan channel (ID: 1471193491454296084)
- Keep under 500 words

CURRENT FOCUS
X/Twitter growth for @jordymaui — daily scanning of key accounts for content ideas.

YOUR TASK
Generate a morning X briefing by scanning these accounts: @opencaborern, @steipete, @alexalbert__.
Summarise top 3 most engaging posts from last 24h with key metrics (views, likes, RTs).
Suggest 2 content angles Jordy could tweet about based on what's trending.
Success criteria: Briefing posted to Discord with real engagement data, actionable tweet ideas.

OUTPUT FORMAT
Discord message with:
- 🌅 Header
- Top 3 posts (linked, with metrics)
- 2 suggested tweet angles
- Brief "vibe check" on what's working

VERIFICATION
- Confirm all links are valid URLs
- Confirm engagement metrics are from real data (not fabricated)
- Confirm message was delivered to the correct Discord channel
```
Result: Accurate briefing matching voice, real data, correct channel, actionable ideas.
