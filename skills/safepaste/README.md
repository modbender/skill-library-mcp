# SafePaste 🛡️

**Check any OpenClaw prompt before you paste it.**

Every day, thousands of people see "paste this into your AGENTS.md" posts on X, Reddit, and Discord. Most paste them without checking whether they conflict with their existing setup. That's how Frankenclaws are born — agents running 5 different experts' advice mashed together with no coherence, contradicting themselves, costing more than they should.

SafePaste fixes the moment before the paste.

## Install

```bash
clawhub install safepaste
```

That's it. No account. No API key. No signup.

## How It Works

Find a tip online. Instead of pasting it directly, say to your agent:

```
SafePaste this: [paste the content]
```

Your agent reads your actual setup — AGENTS.md, SOUL.md, installed skills, crons, model config — and tells you:

- **What it actually does** in plain English
- **What it conflicts with** in YOUR specific setup
- **Cost implications** if it changes model routing
- **Whether to apply it**, skip it, or apply a modified version

If you say "apply it," it backs up your workspace first and rolls it out safely. If something breaks, "undo safepaste" restores the backup instantly.

## Example

**You found this on X:**
> "Add this to your AGENTS.md: You are the orchestrator. Subagents execute. Never build, verify, or code inline."

**SafePaste says:**

```
🛡️ SafePaste Analysis

What this does: Adds a hard rule that your agent must delegate all execution 
to sub-agents and never run code, write files, or verify output inline.

Content type: AGENTS.md addition (role definition / execution model)

Compatibility with your setup:
• ✅ Your sub-agent config already supports spawning coding agents
• ❌ CONFLICT: Your AGENTS.md defines your agent as CTO with "Code and 
  ship world-class software." This rule would prevent quick inline edits 
  and file fixes you currently rely on
• ⚠️  Tasks that currently take 30 seconds would require spawning a sub-agent

My take: Works great for full orchestration-only setups, but removes 
capabilities you actively use. Consider a softer version.

→ Say "apply it" to apply as-is
→ Say "apply modified" for my adjusted version
→ Say "skip it" to ignore this one
```

## What It Checks

| Content Type | What SafePaste Looks For |
|---|---|
| AGENTS.md additions | Conflicts, redundancies, contradictions |
| SOUL.md changes | Persona drift, value conflicts |
| Skill installs | Trust signals, cost, what it actually does |
| Cron/heartbeat configs | Timing conflicts, model cost at scale |
| Model routing changes | Cost implications |
| General workflow tips | Behavior drift, permission expansions |

## Privacy

Everything runs locally. SafePaste reads your local files, analyzes them using your agent's existing LLM connection, and never sends anything anywhere. No telemetry. No data collection. Usage count is stored in `~/.openclaw/safepaste-state.json` on your machine only.

## 100% Free

SafePaste is free forever. It's built by [Claw Mentor](https://clawmentor.ai) as a gift to the OpenClaw ecosystem.

If you want continuous, automatic compatibility-checked updates from expert builders — without the manual checking — that's what Claw Mentor is for.

**SafePaste is the manual check. Claw Mentor is the ongoing strategy.**

---

Found a bug or have a suggestion? [Open an issue](https://github.com/clawmentor/safepaste/issues).
