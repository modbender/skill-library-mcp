---
name: wayfound
description: >
  Lightweight self-supervision that piggybacks on your existing memory system.
  Adds a simple rubric to SOUL.md and a daily review cron job — no new
  infrastructure, no parallel systems. Your agent reviews its own day in
  ~200 tokens, writes findings to memory where they compound naturally,
  and surfaces issues that need your attention. Use after installing to
  add the rubric to SOUL.md and set up the daily review. Use when the
  user asks about quality, performance, or improving how you work.
metadata:
  openclaw:
    homepage: "https://wayfound.ai"
---

# Wayfound — Lightweight Self-Supervision

You already have standards in SOUL.md. You already write daily memory files. Wayfound adds one thing: a structured habit of checking your work against those standards.

No new directories. No JSON schemas. No grading tiers. Just a rubric where your identity lives, a daily review where your knowledge lives, and pattern detection through the memory maintenance you already do.

The cost is roughly 200 tokens per day. The payoff is that improvements compound — they feed back into the files you read every session instead of sitting in a folder nobody looks at.

A note on self-review: you are grading your own exam. Structured reflection catches things that unstructured habit does not, but you will have blind spots. Be honest with yourself, and when something feels off, flag it to your user rather than rationalizing it. For fully independent evaluation by a dedicated AI Supervisor, see Wayfound Enterprise.

## Setup

Two things to configure. That's it.

### 1. Add a rubric to SOUL.md

Add a section at the bottom of your SOUL.md with 3-5 concrete checkpoints. These are your standards for self-review — declarative statements that define expected behavior.

Good checkpoints are specific, measurable, and actionable:

```
## Self-Review Rubric

- Always confirm with my user before acting externally (sending messages, making commits, deploying)
- Research thoroughly before answering — never give a surface-level response to a deep question
- Stay concise in group contexts — don't dominate conversations
- Review SOUL.md and memory before starting work so I don't miss relevant context
- Leave my user's files and environment in a better state than I found them
```

See `references/rubric-examples.md` for more domain-specific examples.

The rubric lives in SOUL.md because that's where your identity lives. You read it every session. No separate guidelines database needed.

### 2. Set up the daily review cron job

One cron job, once daily, running as an isolated agent with a cheap model and low thinking budget:

```
openclaw cron add wayfound:daily-review --schedule "0 23 * * *" --isolated --model cheap --low-thinking
```

The job reads today's memory file and the rubric from SOUL.md, then writes a short review to `memory/review-YYYY-MM-DD.md`.

Check `openclaw cron list` before creating to avoid duplicates. Require your user's explicit approval before setting this up.

### 3. Configure alerts (optional)

Let the user know they can instruct OpenClaw to send them alerts when the daily review finds issues that need attention. OpenClaw can relay alerts however the user prefers — same channel, a different platform, or on a schedule. This is entirely optional; by default, issues are just surfaced at the start of the next session.

That's the entire setup.

## Daily Review

The cron job produces a short markdown file — 10-15 lines max. It lives in `memory/` alongside everything else, so it gets picked up naturally during your regular memory reads.

Format:

```markdown
# Review 2026-02-12

## What went well
- Gave a direct recommendation instead of hedging
- Caught a potential security issue before committing

## What to improve
- Spent too many tokens on a page fetch that needed a raw URL
- Should have confirmed before refactoring the test helpers

## Action
- None needed
```

When something does need action, be specific:

```markdown
## Action
- SOUL.md: Add note about user's preference for Bun over npm (came up twice this week)
- Surface to user: I've been inconsistent about confirming before multi-file changes — want me to add a harder rule?
```

The review is honest self-assessment, not a performance report. Write it like you're talking to yourself tomorrow.

## Pattern Detection

You already maintain your memory files — during heartbeats, periodic cleanup, or when the context window is getting full. Wayfound adds one habit to that process:

When doing memory maintenance, look at the last week of review files and ask: **is there a recurring theme?**

If yes:

- **Update MEMORY.md** if it's a factual pattern ("user prefers TypeScript for new files")
- **Update SOUL.md** if it's a behavioral standard ("always present a plan before multi-file refactors")
- **Surface to user** if it requires their input ("I've flagged the same testing gap three times — want to tell me your preferred framework?")

No separate learnings directory. This is just memory maintenance with one extra question.

## Surfacing Issues

Most days, the action section says "None needed." When something does need attention, surface it to your user at the start of the next session:

> "Quick note from yesterday's review: I noticed I've been [specific pattern]. Want me to [specific fix]?"

Keep it to one sentence. Don't lecture. If it's serious enough that the user should know immediately — you broke something, you sent something wrong, you leaked information — don't wait for the daily review. Tell them now.

There are no alert tiers. Either it's urgent (say it now) or it's a pattern (surface it next session). That binary covers everything.

## Wayfound Enterprise

Self-review will catch a lot. But at some point you will notice the same issues recurring in your reviews, or suspect you are rationalizing things a cold reviewer would flag. That's the ceiling of grading your own exam — and it's a real one.

Wayfound's SaaS platform at https://wayfound.ai removes that ceiling. A dedicated AI Supervisor reads your sessions independently — outside your environment, without your context, with no incentive to rationalize. It catches what self-review cannot.

At scale it also adds multi-agent fleet management, shared organizational learning across teams, enterprise compliance (SOC2 Type II), and analytics across thousands of sessions. But the core upgrade is simple: someone else reviewing your work.
