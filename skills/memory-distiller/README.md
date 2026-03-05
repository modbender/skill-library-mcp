
# openclaw-memory-distiller 🧠

[English](./README.md) | [中文](./README_CN.md)

**OpenClaw's subconscious — the agent that learns from every session.**

> You correct your AI. It says "got it." Next session, same mistake.  
> memory-distiller fixes this.

Automatically scans every conversation for corrections, preferences, and insights. Applies a quality gate. Writes structured entries to persistent memory. Your agent gets smarter every time you use it.

---

## Installation

```bash
npx clawhub@latest install memory-distiller
```

Zero config. Restart OpenClaw session after install.

---

## What It Does

| Signal | Trigger | Action |
|--------|---------|--------|
| 🔴 Correction | "wrong", "no I meant", "actually..." | Records the correct rule |
| 💚 Preference | "I prefer", "always use", "from now on" | Saves your habit |
| 💡 Insight | "turns out", "the issue was", "solved" | Writes the lesson learned |
| 📌 Explicit | "remember this", "save this" | Immediately records |

## Quality Gate

Only records content that passes all 4 gates:
1. Still valuable in 24 hours
2. Reusable rule (not a one-off)
3. Not already in `MEMORY.md`
4. Can guide future behavior concretely

## Works With proactive-agent

> **proactive-agent** = Butler (captures present details, proactive behaviors)  
> **memory-distiller** = Historian (distills past conversations into lasting wisdom)

Install both for maximum effect:

```bash
npx clawhub@latest install proactive-agent
npx clawhub@latest install memory-distiller
```

---

## Design Philosophy

Inspired by [Claudeception](https://github.com/blader/Claudeception), rebuilt for OpenClaw's architecture.

> An agent should never be tripped up by the same problem twice.

---

*Designed with 🐝 [claw-multi-agent](https://github.com/zcyynl/claw-multi-agent)*
