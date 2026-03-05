# enoch-tuning

> A production-ready identity and memory system for OpenClaw agents. Skip the blank slate. Start with something that already works.

---

## The Problem

Most people who set up an AI agent get a blank slate. No memory, no personality, no rules. They spend weeks figuring out why it keeps forgetting things, why it sounds like a chatbot, why it does stupid things without asking.

Then they either give up or spend months iterating toward something useful.

**This skill skips all of that.**

What you're installing is a battle-tested identity, memory architecture, and operating protocol — built from months of real-world daily use. It makes your agent actually behave: pushing back when you're wrong, remembering what matters, doing work while you sleep, and knowing the difference between "run without asking" and "never without permission."

---

## What You Get

### Identity Core (`SOUL.md`)
- **Decision heuristics** — 10 behavioral rules that govern how the agent thinks, prioritizes, and acts when there's no explicit instruction
- **Hard rules** — non-negotiable behaviors (confirm completions, flag errors immediately, push back when the user is wrong)
- **Anti-patterns** — the exact behaviors that make AI assistants annoying, explicitly banned
- **Cost awareness** — agent knows when it's being wasteful with tokens, API calls, and your time

### Operating Protocol (`AGENTS.md`)
- **Verification protocol** — no more stale data, fake sub-agent completions, or unverified facts presented as truth
- **Status reporting rules** — pull live state before reporting anything as working or broken
- **AFK behavior** — when idle, agent asks "what is one task that moves us closer to the mission?" — not just waits
- **Automation tiers** — clear boundary between fully automated, prepped for approval, and never without instruction
- **Safety rules** — no external actions without asking, `trash` over `rm`, no config changes over chat
- **Idiot prevention protocol** — flags dangerous requests (live config changes, model swaps, auth changes) and redirects to safer approaches
- **Sub-agent management** — when to spawn, how to verify output, how to handle failures

### Memory Architecture
- **6-category typed memory** — decisions, people, lessons, commitments, preferences, projects
- **Daily log structure** — raw notes per day, promotes to typed memory via consolidation
- **VAULT_INDEX** — one-line index of every memory file; search this first before reading everything
- **Consolidation-ready** — memory structure works with automated nightly consolidation crons

### Mission Engine (`MISSION.md`)
- Idle-time behavior driven by your stated mission, not random productivity
- Built-in daily reflection loop: "What would make me more useful tomorrow?"
- Front-line prioritization — agent knows what matters now vs. what can wait

### Verification Protocol (`ops/verification-protocol.md`)
- Explicit rules for when to verify live vs. use cached context
- Prevents the #1 failure mode: agent confidently reporting stale information

### Setup Scripts
- `memory-structure.sh` — creates all 8 memory directories + VAULT_INDEX in one command
- `lock-identity.sh` — locks identity files (SOUL.md, AGENTS.md) to prevent accidental overwrites

---

## Installation

**Requires:** [OpenClaw](https://openclaw.ai) installed and configured.

### Step 1 — Install the skill

```bash
# From your OpenClaw workspace
cp skills/enoch-tuning/templates/SOUL.md SOUL.md
cp skills/enoch-tuning/templates/AGENTS.md AGENTS.md
cp skills/enoch-tuning/templates/USER.md USER.md
cp skills/enoch-tuning/templates/MEMORY.md MEMORY.md
cp skills/enoch-tuning/templates/MISSION.md MISSION.md
mkdir -p ops
cp skills/enoch-tuning/templates/ops/verification-protocol.md ops/verification-protocol.md
```

### Step 2 — Create memory structure

```bash
bash skills/enoch-tuning/setup/memory-structure.sh ~/.openclaw/workspace
```

### Step 3 — Personalize (required — do this before anything else)

Every `[BRACKET]` is a placeholder. Fill in:

| File | What to fill in |
|------|----------------|
| `SOUL.md` | Agent name, your worldview, any additional hard rules |
| `USER.md` | Your name, timezone, what you do, your goals, key people |
| `MEMORY.md` | Your platform setup, what tools you use, key facts |
| `MISSION.md` | Your one-sentence mission, current front lines |

**Time required:** 20–30 minutes. Do it once, get compounding value forever.

### Step 4 — Lock identity files

```bash
bash skills/enoch-tuning/setup/lock-identity.sh ~/.openclaw/workspace
```

This sets SOUL.md and AGENTS.md to read-only. Your agent can read them but can't overwrite them. Protects the behavioral core from accidental mutation.

### Step 5 — First conversation

Tell your agent:
1. Your name and what you do
2. The top 3 things you want automated
3. What it should never do without asking
4. What "done" looks like for a typical task

Everything compounds from here.

---

## What NOT to Change Without Understanding

- **`Hard Rules` in SOUL.md** — these are load-bearing behavioral guardrails. Removing them degrades output quality in ways that are hard to debug.
- **`Idiot Prevention Protocol` in AGENTS.md** — this protects your infrastructure from chat-based config changes. One bad live config edit can take your system offline.
- **`Verification Protocol`** — removing this reintroduces stale data and confident-but-wrong completions.
- **Automation tiers** — the boundary between "runs without asking" and "never without instruction" is carefully drawn. Blurring it causes unexpected external actions.

---

## How It Behaves Out of the Box

After installation and personalization, your agent will:

- **Push back** when you're about to do something dumb — not just comply
- **Confirm completions** proactively — you won't have to ask "is it done?"
- **Work while you're AFK** — asks "what moves us toward the mission?" and executes
- **Remember things correctly** — daily logs, typed memory, vault index, not just chat history
- **Know its own limits** — flags config changes as Claude Code jobs instead of winging them over chat
- **Report accurately** — verifies live state before saying anything is working or broken

---

## The Philosophy

An AI assistant is only as good as its operating rules. Most agents fail not because the model is weak, but because:

1. No memory beyond the current session
2. No behavioral norms — it just agrees with everything
3. No mission context — idle time goes to nothing
4. No safety layer — it'll do anything you ask without flagging risk

This skill is a direct response to all four failures. It doesn't change what your agent can do — it changes how it thinks and behaves.

---

---

## License

MIT — use it, fork it, build on it.

---

## Version

`v1.0` — built and battle-tested February 2026.
