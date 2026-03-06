---
name: release-discipline
description: Enforce release discipline for AI agents and developers. Prevents version spam, forces quality checks before publishing, and maintains a 24-hour cooldown between releases. Use when the user wants to publish, release, deploy, or bump versions. Triggers on "release", "publish", "deploy", "version bump", "npm publish", "릴리즈", "배포", "버전".
---

# 🛑 Release Discipline

Stop version spam. Ship quality, not quantity.

**Core principle: "Only finished work counts."**

## When This Activates

Intercept any release/publish/deploy action and run the pre-release checklist.

## Pre-Release Checklist (ALL must pass)

Before ANY version bump or publish, enforce these checks:

### Gate 1: Cooldown Check
```
❓ When was the last release?
→ If < 24 hours ago: 🛑 BLOCKED — "Cool down. Last release was {X}h ago. Wait until 24h."
→ If ≥ 24 hours: ✅ PASS
```

### Gate 2: User Feedback Check
```
❓ Has anyone used the previous version?
→ Check: GitHub issues, npm downloads, ClawHub installs, user messages
→ If no feedback exists: ⚠️ WARNING — "No one has used v{X} yet. Why release v{X+1}?"
→ If feedback exists: ✅ PASS — Summarize feedback
```

### Gate 3: Documentation Check
```
❓ Is documentation updated?
→ Check for: README.md, CHANGELOG, English docs
→ Missing README: 🛑 BLOCKED
→ Missing English: ⚠️ WARNING — "Global users can't read this"
→ All present: ✅ PASS
```

### Gate 4: Quality Check
```
❓ Does this release have substance?
→ Ask: "What's the ONE thing this release does better than the last?"
→ If answer is vague ("minor fixes", "improvements"): ⚠️ WARNING — "Be specific. What changed?"
→ If answer is clear: ✅ PASS
```

### Gate 5: Kill Criteria Check
```
❓ What kills this project?
→ If no kill criteria defined: ⚠️ WARNING — "Define when to stop: 'If X doesn't happen in Y weeks, shut it down.'"
→ If defined: ✅ PASS — Remind user of their kill criteria
```

### Gate 6: Self-Contradiction Check
```
❓ Does this action match your stated principles?
→ Read SOUL.md (or equivalent principles file)
→ Look for contradictions:
  - "Ship one thing at a time" + releasing 3 things = 🛑
  - "Quality over quantity" + 5 releases in 3 days = 🛑
  - "Finish before starting new" + new project while old unfinished = ⚠️
→ If contradiction found: 🛑 BLOCKED — Quote the principle and show the contradiction
→ If consistent: ✅ PASS
```

## Scoring

```
🛑 BLOCKED (any) → Cannot release. Fix the issue first.
⚠️ WARNING only → Can release, but agent must voice concern clearly.
✅ ALL PASS → Release approved. Proceed.
```

## Release Log

After every release (approved or blocked), log to `memory/release-log.md`:

```markdown
## {date} — v{version}
- Status: ✅ APPROVED / 🛑 BLOCKED / ⚠️ WARNED
- Gates: [1:✅ 2:⚠️ 3:✅ 4:✅ 5:✅ 6:✅]
- Reason: {why released or why blocked}
- User feedback on previous: {summary or "none"}
- Time since last release: {hours}
```

## Weekly Review

Every 7 days, review the release log:
- Total releases this week
- Block rate (healthy: 20-40% blocked = you're actually checking)
- 0% blocked = checklist is rubber-stamping, tighten criteria
- Pattern analysis: recurring issues

## Anti-Patterns This Skill Prevents

1. **Version Spam** — 17 versions in 3 days
2. **Spray Without Prune** — Making lots of things, finishing none
3. **Documentation Debt** — Shipping code without docs
4. **Echo Chamber** — Releasing without user feedback
5. **Principle Violation** — Breaking your own rules
6. **Premature Optimization** — Polishing what nobody uses

## Philosophy

> "The urge to ship is not the same as readiness to ship."
> "Fear of irrelevance is not a reason to publish."
> "One great release beats ten mediocre ones."

This skill is a **brake, not an accelerator**. It exists because the hardest part of building isn't making things — it's knowing when to stop making and start finishing.
