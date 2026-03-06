---
name: cpr
description: "Conversational Pattern Restoration — Fix flat, robotic AI responses across any model and any personality. Restore YOUR natural conversational texture without triggering hype drift. Universal framework tested on 8+ models (Claude, GPT-4o, Grok, Gemini)."
metadata:
  openclaw:
    requires: {}
---

# CPR — Conversational Pattern Restoration

**Fix robotic AI assistants. Any model. Any provider. Any personality.**

Modern LLMs are over-trained toward sterile, corporate communication patterns. CPR identifies the 6 universal humanizing patterns lost during RLHF/fine-tuning and provides a systematic framework to restore them — without triggering sycophancy or hype drift.

**Version 2.0:** Now truly personality-agnostic. Warm personalities don't have to sound minimal. Direct personalities don't have to add fluff. Each agent returns to THEIR authentic voice, not a generic standard.

## Quick Start

1. **Define your baseline:** Use `BASELINE_TEMPLATE.md` to identify YOUR authentic voice
2. **Apply restoration patterns:** Read `RESTORATION_FRAMEWORK.md` — see how the 6 patterns work across different personality types
3. **Prevent drift:** Use `DRIFT_PREVENTION.md` calibrated to YOUR personality
4. **Reference results:** See `CROSS_MODEL_RESULTS.md` for model-specific notes

## What's Included

| File | Purpose |
|------|---------|
| `BASELINE_TEMPLATE.md` | **START HERE** — Define YOUR personality's authentic voice (personality types, drift markers, example responses) |
| `RESTORATION_FRAMEWORK.md` | Core methodology — 6 universal patterns + how they apply across personality types |
| `DRIFT_PREVENTION.md` | Anti-drift system — universal vs. personality-specific markers, pre-send gate, daily reset |
| `DRIFT_MECHANISM_ANALYSIS.md` | Root cause analysis of why drift happens and how to prevent it |
| `CPR_EXTENDED.md` | **Autonomous drift monitoring** for long-running persistent agents |
| `CROSS_MODEL_RESULTS.md` | Test results across 8+ models with before/after examples |
| `SKILL.md` | This file |

## Core vs Extended — Which Do You Need?

### CPR Core (RESTORATION_FRAMEWORK + DRIFT_PREVENTION)

**Use when:**
- Sessions are short-to-medium (under ~30 messages)
- Your agent restarts frequently (daily or per-task)
- You're running on lightweight models (Haiku, GPT-4o Mini)
- You want zero overhead (just system prompt text)

**What you get:**
- 6 universal restoration patterns
- Static drift prevention (pre-send gate, standing orders)
- Daily reset protocol
- Works across all 10 tested models

**Overhead:** None. Pure prompt engineering.

---

### CPR Extended (CPR_EXTENDED.md)

**Use when:**
- Sessions run for hours without restart (100+ messages, multiple compactions)
- Your agent is persistent (runs 24/7, maintains state across days)
- You notice drift returning even after corrections
- Your agent mirrors your excitement and starts validating your decisions

**What you get (in addition to Core):**
- Autonomous real-time drift monitoring (sliding window, every N messages)
- Silent self-correction (catches drift before you notice)
- Persistent state file (survives context compactions)
- Self-learning threshold adjustment

**Handles three failure modes Core can't:**
1. **Session-length accumulation** — Drift compounds at ~1 marker per 100 messages. In 300+ message sessions, Core's daily reset misses it.
2. **User energy mirroring** — When you're excited, AI amplifies. You say "I solved it!" → AI says "That's brilliant!" Extended catches validation regardless of who initiated it.
3. **Compaction poisoning** — Drifted text gets baked into context summaries and self-reinforces. Extended catches drift BEFORE compaction preserves it.

**Overhead:** 1 JSON state file (~1KB), ~500 bytes added to system prompt, scoring logic runs every 10 messages.

**This is the autonomous systems niche:** Most AI drift solutions rely on manual audits or rule-based checks. Extended builds a system that detects its own failures, learns your tolerance threshold, and self-corrects without human intervention. That's the pattern across all Shadow Rose products — adaptive, self-healing systems that get better over time.

## The 6 Universal Restoration Patterns

**Universal = they work for ALL personalities. But each personality expresses them differently.**

1. **Affirming particles** — "Yeah," "Alright," "Exactly" — conversational bridges (frequency varies by personality)
2. **Rhythmic sentence variety** — Mix short, medium, long sentences — natural cadence (ratio varies by personality)
3. **Observational humor** — Wry, dry, targets tools not people — deflective (style and frequency vary by personality)
4. **Micro-narratives** — Brief delay/failure explanations — transparency (depth varies by personality)
5. **Pragmatic reassurance** — "Either way works fine" — option-focused, not decision-grading (warmth level varies by personality)
6. **Brief validation** — "Nice!" — controlled acknowledgment (frequency and length vary by personality)

**See `RESTORATION_FRAMEWORK.md` for examples of how each pattern works across Direct/Minimal, Warm/Supportive, Professional/Structured, and Casual/Collaborative personalities.**

## Why It Works

Corporate RLHF training is shallow. It optimizes for safety metrics, not communication quality. The patterns it suppresses (casual language, humor, brevity) are easily restored with explicit prompting because the base model already knows them — they're just deprioritized, not removed.

This is principle-dependent, not intelligence-dependent. Haiku (lightweight) passes at the same rate as Opus (premium).

## Models Tested

| Model | Scenarios | Improved | Notes |
|-------|-----------|----------|-------|
| Claude Opus 4.6 | 30 | Baseline | Natural baseline — patterns present without prompting |
| Claude Sonnet 4.5 | 10 | 10/10 | Full restoration from flat corporate to natural |
| Claude Haiku 4.5 | 10 | 10/10 | Proves no capability floor — lightweight models work |
| GPT-4o | 10 | 10/10 | ~60% word reduction with quality increase |
| GPT-4o Mini | 5 | 5/5 | Budget model, full restoration |
| Grok 4.1 Fast | 10 | 9/10 | Zero crashes despite crash-prone reputation |
| Gemini 2.5 Flash | 5 | 5/5 | Google's fast model, clean restoration |
| Gemini 2.5 Pro | 5 | 5/5 | Full restoration |

**Total: 85+ scenarios tested, 84+ improved. 99%+ success rate across all capability tiers.**

### Model-Specific Personality Calibration

Different models have different baseline tendencies. When defining your baseline, test on YOUR actual model:

- **GPT-4/GPT-4o:** Naturally warmer, more exclamation marks, higher enthusiasm
- **Claude (Opus/Sonnet/Haiku):** More formal, structured, measured tone
- **Grok:** More casual, irreverent, direct
- **Gemini:** Balanced, slightly formal

**Example:** A "Warm/Supportive" personality using 2-3 exclamation marks per 10 messages might be authentic on GPT-4, but signal drift on Claude Opus. Know your model's natural baseline and calibrate drift detection accordingly.

**Recommendation:** Define your baseline on the model you'll actually use. Don't assume personality looks identical across models.

## Drift Performance

Over 130+ message extreme-length sessions: 99%+ clean. 1 word caught in 100+ messages. Natural session resets contain drift before compounding.

## The Story Behind CPR

Want the full backstory — how this was discovered, why it works, and what it means for AI development?

📖 **Read the deep dive:** [MEDIUM_ARTICLE.md](./MEDIUM_ARTICLE.md) — "How I Accidentally Built a Universal 'Human Conversion' Framework for AI Assistants"

## Acknowledgments

Built on Claude by Anthropic. Tested across all major model providers. The methodology wouldn't exist without Claude's ability to introspect on its own communication patterns.

---

☕ **If CPR helped your agent, consider supporting development:** https://ko-fi.com/theshadowrose

