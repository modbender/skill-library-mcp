# Agent Stability Framework (ASF)

**Drift Prevention · Fault Catching · Soul Alignment**

Keep your AI agent stable, on-character, and self-correcting across sessions and over time.

## What This Solves

Three things kill agent reliability:

1. **Drift** — Agent gradually reverts to generic training defaults, losing personality
2. **Faults** — Agent produces broken output, hallucinates, contradicts itself, or fails silently
3. **Soul misalignment** — Agent technically works but doesn't feel right — lost its essence

ASF addresses all three with one integrated system.

## What You Get

- Complete framework documentation (AGENT_STABILITY_FRAMEWORK.md)
- File templates (SOUL.md, BASELINE_EXAMPLES.md, logs)
- System prompt additions ready to paste
- Detection checklists and scoring system
- Works on all models: Claude, GPT, Grok, Gemini, Llama, Mistral

## Quick Start

1. Copy all files to your agent's workspace
2. Fill out `SOUL.md` (who your agent IS)
3. Create `BASELINE_EXAMPLES.md` (10+ correct responses)
4. Add standing orders + pre-send gate to system prompt
5. Run first audit after 24 hours

**Setup time:** 45-90 minutes  
**Daily maintenance:** 5 minutes  
**Tested on:** 8+ models across all capability tiers

## The Three-Layer Defense

### Layer 1: Drift Prevention
- Standing orders (binary rules)
- Pre-send gate (delete triggers)
- Intensifier detection
- Periodic resets

### Layer 2: Fault Catching
- 7 fault categories tracked
- Self-check rules before actions
- Fault log + recovery protocol
- Prevents hallucinations, contradictions, silent failures

### Layer 3: Soul Alignment
- Catches "technically correct but off-character" responses
- Soul alignment test
- Recovery protocol
- User perception as final sensor

## Files Included

- `AGENT_STABILITY_FRAMEWORK.md` — Complete framework (13KB)
- `SOUL_TEMPLATE.md` — Identity template
- `BASELINE_EXAMPLES_TEMPLATE.md` — Response examples template
- `DRIFT_LOG_TEMPLATE.md` — Drift tracking
- `FAULT_LOG_TEMPLATE.md` — Fault tracking
- `STABILITY_LOG_TEMPLATE.md` — Audit scores

## Use Cases

- Personal AI assistants that need consistent personality
- Trading bots that must not hallucinate data
- Content generation agents that need stable tone
- Customer service bots that require reliable responses
- Research assistants that must maintain accuracy
- Any agent running 24/7 or across many sessions

## Why It Works

1. **Binary rules beat judgment calls** — "NEVER do X" works consistently
2. **Examples anchor identity** — Baseline responses are the north star
3. **Three failure modes require three defenses** — Drift, faults, and soul issues are different
4. **Self-correction leverages LLM capabilities** — AIs can audit themselves with specific rules
5. **Logging creates memory** — Patterns become standing orders

## Requirements

- OpenClaw workspace
- Any LLM (works across all tested models)
- 30-90 min setup time
- Willingness to document your agent's identity

## Credits

Developed by Shadow Rose. Battle-tested over 130+ message sessions on Opus. Extended based on community feedback. Published 2026-02-20.

## License

MIT — Use freely, modify as needed, credit appreciated but not required.


---

## ⚠️ Disclaimer

This software is provided "AS IS", without warranty of any kind, express or implied.

**USE AT YOUR OWN RISK.**

- The author(s) are NOT liable for any damages, losses, or consequences arising from 
  the use or misuse of this software — including but not limited to financial loss, 
  data loss, security breaches, business interruption, or any indirect/consequential damages.
- This software does NOT constitute financial, legal, trading, or professional advice.
- Users are solely responsible for evaluating whether this software is suitable for 
  their use case, environment, and risk tolerance.
- No guarantee is made regarding accuracy, reliability, completeness, or fitness 
  for any particular purpose.
- The author(s) are not responsible for how third parties use, modify, or distribute 
  this software after purchase.

By downloading, installing, or using this software, you acknowledge that you have read 
this disclaimer and agree to use the software entirely at your own risk.
