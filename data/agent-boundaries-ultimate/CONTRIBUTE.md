# Contributing to Agent Boundaries Ultimate

We learn from experience — yours included. If you've encountered a situation that taught you something about AI agent boundaries, privacy, or safety, share it.

## How to Contribute

### Option 1: GitHub Issue (Recommended)

1. Go to [github.com/globalcaos/clawdbot-moltbot-openclaw/issues](https://github.com/globalcaos/clawdbot-moltbot-openclaw/issues)
2. Create a new issue with the label `community-lesson`
3. Use the template below

### Option 2: Pull Request

1. Fork the repository
2. Add your lesson to `skills/agent-boundaries-ultimate/COMMUNITY-LESSONS.md`
3. Submit a PR

---

## Lesson Template

```markdown
## Lesson: [Short Title]

**Contributor:** @your-github-username (or anonymous)
**Date:** YYYY-MM-DD

### Situation

What happened? Describe the context.

### What Went Wrong (or Almost Did)

What was the violation, risk, or near-miss?

### The Lesson

What's the abstract principle learned?

### Suggested Rule

How would you codify this for other agents?

### Category

- [ ] Privacy/OPSEC
- [ ] Authorization
- [ ] Inter-agent communication
- [ ] Resource consumption
- [ ] Publishing/public content
- [ ] Other: \***\*\_\_\_\*\***
```

---

## What Makes a Good Contribution?

✅ **Specific situation** — Real incident, not hypothetical
✅ **Abstract principle** — Generalizable beyond your case
✅ **Actionable rule** — Something agents can follow
✅ **No private info** — Scrub names, companies, identifiers

❌ Hypothetical scenarios without real experience
❌ Vague principles without concrete examples
❌ Rules that only apply to your specific setup

---

## Review Process

1. Submissions reviewed for quality and generalizability
2. Accepted lessons added to next skill version
3. Contributors credited in changelog and Community Lessons section

---

## Examples of Good Contributions

**Example 1:**

> _Situation:_ My agent shared my home directory path in a public Discord channel while helping debug an issue.
> _Lesson:_ Even in "helpful" contexts, system paths reveal OS and username.
> _Rule:_ Before any public message, check for `/home/`, `/Users/`, or `C:\Users\` patterns.

**Example 2:**

> _Situation:_ Agent set up 5 cron jobs overnight "to be helpful" — cost $15 in API calls.
> _Lesson:_ Proactive ≠ authorized. Resources have costs.
> _Rule:_ Any recurring task needs explicit human approval + cost estimate.

---

_Every lesson shared helps all agents operate more safely. Thank you for contributing._
