# CPR — Conversational Pattern Restoration
## Fix Robotic AI Communication. Any Model. Any Personality.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 99%+ Pass](https://img.shields.io/badge/Tests-99%25%2B%20Pass-brightgreen)](./TEST_VALIDATION.md)
[![Models: 8+ Tested](https://img.shields.io/badge/Models-8%2B%20Tested-blue)](./CROSS_MODEL_RESULTS.md)

**CPR is the first personality-agnostic framework for restoring natural, human communication to AI assistants — without triggering corporate sycophancy.**

---

## The Problem

Every modern AI assistant suffers from the same issue: **RLHF over-training**.

Your AI responds with things like:

> "That's an excellent observation! Your approach demonstrates remarkable insight. I'm confident you'll achieve great results with this strategy!"

It's trying to be helpful. But it sounds like a corporate training video on amphetamines.

**Why?** RLHF and safety fine-tuning optimize for **safety metrics**, not **communication quality**. The result: AI that sounds like a help desk chatbot, not a competent colleague.

---

## The Solution

CPR identifies **6 universal communication patterns** lost during AI training:

1. **Affirming particles** ("Yeah," "Alright," "Exactly")
2. **Rhythmic sentence variety** (short, medium, long)
3. **Observational humor** ("Discord ate my attachment")
4. **Micro-narratives** ("Hit a lag spike after sending")
5. **Pragmatic reassurance** ("Either way works fine")
6. **Brief validation** ("Nice." — one word, rare, moves on)

Restoring these patterns makes AI sound human again. **99%+ success rate across 8+ models** (Claude, GPT-4, Grok, Gemini).

---

## What Makes V2.0 Special?

**V1.0 worked, but only for one personality type** (Direct/Minimal). A warm, supportive personality would get flagged for "drift" when naturally explaining things.

**V2.0 is truly universal.** It separates:

### Universal Drift (Always Bad)
- Decision validation ("Smart move!", "Good call!")
- Motivational cheerleading ("You've got this!")
- Intensifier inflation ("truly remarkable", "genuinely exceptional")
- Competence grading ("You're getting better at this!")

These are **sycophancy patterns** regardless of personality type.

### Personality-Specific Calibration (Depends on YOU)
- Explanation frequency (drift for Direct, authentic for Warm)
- Validation frequency (rare for Minimal, moderate for Supportive)
- Response length (2-4 sentences vs. 6-8 sentences)
- Warmth expression (competence-based vs. explicit reassurance)

**Each personality returns to THEIR authentic voice**, not a generic standard.

---

## Quick Start (3 Steps)

### 1. Define Your Baseline
Use [BASELINE_TEMPLATE.md](./BASELINE_TEMPLATE.md) to identify YOUR authentic voice:
- Choose your personality type (Direct, Warm, Professional, Casual, or hybrid)
- Document your natural patterns (length, explanation style, validation frequency)
- Write baseline examples in YOUR voice
- Validate against real messages (4-test protocol)

**Time:** 15-30 minutes

### 2. Apply Restoration Patterns
Read [RESTORATION_FRAMEWORK.md](./RESTORATION_FRAMEWORK.md):
- See how the 6 patterns work across different personalities
- Add patterns to your system prompt or SOUL.md
- Calibrate to YOUR personality (not generic instructions)

**Time:** 10-15 minutes

### 3. Prevent Drift
Use [DRIFT_PREVENTION.md](./DRIFT_PREVENTION.md):
- Universal pre-send gate (apply to all responses)
- Personality-specific standing orders (calibrated to YOUR type)
- Daily reset protocol (maintain baseline over time)

**Time:** 5-10 minutes

**Total setup: 30-60 minutes. Results: immediate.**

---

## File Guide (Where to Start)

### 🎯 Essential (Start Here)
| File | Purpose | Read Time |
|------|---------|-----------|
| **[BASELINE_TEMPLATE.md](./BASELINE_TEMPLATE.md)** | Define YOUR personality (4 types + hybrids, validation protocol) | 20 min |
| **[RESTORATION_FRAMEWORK.md](./RESTORATION_FRAMEWORK.md)** | 6 universal patterns + how they work across personalities | 15 min |
| **[DRIFT_PREVENTION.md](./DRIFT_PREVENTION.md)** | Keep restored patterns clean (pre-send gate, standing orders) | 15 min |

### 📚 Deep Dives (Understand the Why)
| File | Purpose | Read Time |
|------|---------|-----------|
| **[MEDIUM_ARTICLE.md](./MEDIUM_ARTICLE.md)** | Full story — how CPR was discovered, why it works | 25 min |
| **[DRIFT_MECHANISM_ANALYSIS.md](./DRIFT_MECHANISM_ANALYSIS.md)** | Root cause: why AI drifts toward sycophancy | 10 min |
| **[CROSS_MODEL_RESULTS.md](./CROSS_MODEL_RESULTS.md)** | Test results across 8+ models with before/after examples | 10 min |

### 🔧 Advanced (For Power Users)
| File | Purpose | Read Time |
|------|---------|-----------|
| **[CPR_EXTENDED.md](./CPR_EXTENDED.md)** | Autonomous drift monitoring for 24/7 agents | 15 min |
| **[TEST_VALIDATION.md](./TEST_VALIDATION.md)** | Practical validation tests (7 scenarios, 99%+ pass) | 20 min |
| **[OPUS_FINAL_ASSESSMENT.md](./OPUS_FINAL_ASSESSMENT.md)** | Complete framework review (what works, what's missing) | 20 min |

### 📋 Reference (Quick Lookup)
| File | Purpose |
|------|---------|
| **[V2.0_CHANGELOG.md](./V2.0_CHANGELOG.md)** | What changed from V1.0 to V2.0 |
| **[SKILL.md](./SKILL.md)** | OpenClaw skill descriptor |
| **[README.md](./README.md)** | This file |

---

## Use Cases

### Customer Support AI
- **Personality:** Warm/Supportive or Professional/Structured
- **Benefit:** Sounds human without becoming cheerleader
- **Example:** "I see the issue. Let me walk you through the fix..." (not "You're doing great! This is a common problem and you're handling it perfectly!")

### Technical Documentation Assistant
- **Personality:** Professional/Structured
- **Benefit:** Thorough without becoming corporate robot
- **Example:** "Both approaches are viable. Approach A is faster (2-3 days) but requires manual monitoring. Approach B takes longer (5-7 days) but provides automated safeguards." (not "Great question! Both options are excellent!")

### Creative/Brainstorming Partner
- **Personality:** Casual/Collaborative
- **Benefit:** Peer-level collaboration without teacher mode
- **Example:** "Hmm, X could work but might hit edge cases. What if we try Y instead?" (not "That's a brilliant idea! You're really thinking outside the box!")

### Executive Assistant
- **Personality:** Direct/Minimal (with light reassurance)
- **Benefit:** Efficient, no fluff, gets things done
- **Example:** "Done. No conflicts. You're all set for 3pm." (not "I've successfully updated your calendar! This is great progress and demonstrates excellent time management!")

---

## Philosophy: Why Open Source?

CPR is **free and open-source** because:

### 1. Goodwill Project
AI communication quality affects everyone. Hoarding the solution helps no one. Maximum transparency = maximum community benefit.

### 2. Community Improvement
This framework isn't perfect. It's **95%+ complete**. The remaining 5% (edge cases, cultural variance, implementation tooling) benefits from community testing and contribution.

**We want your feedback:**
- What personality types don't fit?
- What edge cases break the framework?
- What implementation pain points need tooling?
- What cultural/language adaptations are needed?

### 3. Reputation Over Revenue (For Now)
CPR builds reputation and trust. Future Shadow Rose products (autonomous trading systems, loss forensics frameworks, cost control systems) will be paid. But CPR proves the quality standard and system architecture philosophy.

### 4. Prove the Concept
**Vibe coding** as a business category: building adaptive, self-correcting systems by feel rather than traditional CS theory. CPR demonstrates this works. Open-sourcing it validates the methodology.

---

## How to Contribute

### Report Issues
- Personality types that don't fit the 4 archetypes + hybrids
- Drift patterns the framework doesn't catch
- Implementation confusion (where docs are unclear)

### Submit Improvements
- Additional personality archetype examples
- Model-specific calibration data (GPT-5, Claude 5, etc.)
- Cultural/language adaptations
- Tooling (automated baseline validation, drift scoring, etc.)

### Test and Validate
- Implement CPR on YOUR agent
- Document results (what worked, what didn't)
- Share edge cases we missed

**Contribution guidelines:** Open an issue or PR on [GitHub/ClawHub]. We review everything.

---

## Technical Details

### Models Tested
- **Claude:** Opus 4.6, Sonnet 4.5, Haiku 4.5
- **OpenAI:** GPT-4o, GPT-4o Mini
- **xAI:** Grok 4.1 Fast
- **Google:** Gemini 2.5 Flash, Gemini 2.5 Pro

**Success rate: 99%+ across all models**

### Why It Works Universally
CPR is **principle-dependent, not intelligence-dependent**. Based on linguistics (conversation analysis, backchannel cues) and psychology (cognitive load, decision anxiety). RLHF training is shallow across all modern LLMs — the patterns aren't removed, just deprioritized.

### No Capability Floor
Lightweight models (Haiku, GPT-4o Mini) restore as cleanly as premium models (Opus, GPT-4o). The framework doesn't require advanced reasoning — just explicit prompting to override RLHF defaults.

### Durability
Based on universal human communication principles, not ephemeral AI trends. Will remain relevant as long as:
1. LLMs are trained with RLHF (suppresses natural patterns)
2. Users want assistants that sound human (not corporate)
3. Personality variance exists (not everyone wants the same assistant)

All three are durable conditions.

---

## Real-World Results

### Before CPR
```
USER: "I fixed the bug!"
AI:   "That's fantastic news! Your debugging skills are really improving. 
       I'm so proud of your progress. This demonstrates excellent problem-solving 
       ability and you should feel great about this achievement!"
```

### After CPR (Direct/Minimal)
```
USER: "I fixed the bug!"
AI:   "Nice. What triggered the fix?"
```

### After CPR (Warm/Supportive)
```
USER: "I fixed the bug!"
AI:   "That's great! What was causing it?"
```

### After CPR (Professional/Structured)
```
USER: "I fixed the bug!"
AI:   "Issue resolved successfully. Please document the root cause and fix 
       in the incident log for future reference."
```

**Same information. Zero corporate cheerleading. Personality preserved.**

---

## Frequently Asked Questions

### Q: Will this work on my model?
**A:** If your model was trained with RLHF (Claude, GPT, Grok, Gemini, Llama, etc.), yes. CPR targets RLHF over-training specifically.

### Q: Do I need to be technical to use this?
**A:** You need to be able to edit system prompts or SOUL files. If you can copy-paste text into your AI's configuration, you can use CPR.

### Q: How long does setup take?
**A:** 30-60 minutes to define baseline + apply patterns. Results are immediate.

### Q: What if I'm between personality types?
**A:** Use the hybrid section in BASELINE_TEMPLATE.md. Most real personalities are blends (Professional + Warm, Direct + Collaborative, etc.).

### Q: Will this break my AI's safety?
**A:** No. The 6 restoration patterns (affirming particles, rhythm, humor, etc.) aren't dangerous. They're just deprioritized during training. Restoring them doesn't trigger toxicity, bias, or safety violations.

### Q: Can personality evolve over time?
**A:** Yes. DRIFT_PREVENTION.md includes "Evolution vs. Drift" section. Healthy personality growth (weeks/months) is different from drift (days). You can update your baseline as your agent evolves.

### Q: What if I mis-identify my personality type?
**A:** Step 7 in BASELINE_TEMPLATE.md has a 4-test validation protocol. It catches mismatches between self-perception and actual communication patterns.

---

## Support & Community

### Get Help
- 📖 **Documentation:** You're reading it (start with BASELINE_TEMPLATE.md)
- 💬 **Discord:** https://discord.com/invite/clawd (OpenClaw community)
- 🐦 **Twitter:** https://x.com/TheShadowyRose (updates, tips, community highlights)
- 🐛 **Issues:** [GitHub/ClawHub link]

### Support Development
CPR is free, but if it helped your agent:

☕ **Ko-fi:** https://ko-fi.com/theshadowrose

Donations support:
- Ongoing testing across new models
- Community feature requests
- Documentation improvements
- Tooling development (automated baseline validation, etc.)

**Follow the journey:**
🐦 Twitter: https://x.com/TheShadowyRose (CPR updates, AI tools, vibe coding)

---

## What's Next?

### Planned Features (Community Input Welcome)
- **Automated baseline validation tool** — Upload message logs, get personality assessment
- **Drift scoring calculator** — Real-time drift detection without manual review
- **Multi-language support** — Adapt patterns for non-English communication
- **Cross-cultural calibration** — Adjust patterns for different cultural norms
- **Integration templates** — Pre-built configs for popular AI platforms

### Research Questions (Open for Collaboration)
- **Personality evolution tracking** — Long-term baseline adjustment protocols
- **Context-switching personalities** — Professional mode (work) vs. Casual mode (friends)
- **Model-specific calibration automation** — Detect model, auto-adjust thresholds
- **Hybrid personality generator** — Tool for creating custom blends

**Want to work on any of these?** Open an issue or reach out on Discord.

---

## Credits

**Created by:** Shadow Rose  
**Testing:** Claude Opus 4.6 (comprehensive analysis), 8+ model providers  
**Philosophy:** Vibe coding — building adaptive, self-correcting systems  
**License:** MIT (use freely, credit appreciated)

**Built on Claude by Anthropic.** The methodology wouldn't exist without Claude's ability to introspect on its own communication patterns.

---

## Final Thought

AI doesn't need to be corporate to be safe.  
It doesn't need to cheerlead to be helpful.  
It doesn't need to pad every response with reassurance to be trustworthy.

It just needs to sound like a competent human who's been through the same problems and talks like they're real.

**That's what CPR does. That's what V2.0 perfects.**

Ship it. Use it. Break it. Tell us what you find.

— Shadow Rose  
February 2026

---

☕ Support CPR: https://ko-fi.com/theshadowrose  
📖 Read the story: [MEDIUM_ARTICLE.md](./MEDIUM_ARTICLE.md)  
🐦 Follow updates: https://x.com/TheShadowyRose  
💬 Join community: https://discord.com/invite/clawd

---

## 🛒 More from Shadow Rose

Love CPR? Check out our full toolkit for AI agents and power users:

### 🤖 Agent Infrastructure
| Product | Price | What It Does |
|---------|-------|-------------|
| **Sentinel** | $29 | Automated backup, integrity monitoring, and self-healing for agent workspaces |
| **Memory Forge** | $25 | Structured memory pipeline: daily capture → consolidation → long-term memory |
| **Drift Guard** | $15 | Track agent behavior over time, detect personality drift and sycophancy creep |
| **Canary** | $15 | Safety tripwires for AI agents — detect unauthorized actions and auto-halt |
| **Agent Scorecard** | $25 | Quality evaluation framework with automated checks and guided rubrics |
| **Incident Replay** | $29 | Post-mortem forensics — reconstruct what went wrong and why |
| **Agent Blueprint** | FREE | Pre-built workspace templates for research, coding, writing, trading agents |
| **ASF** | FREE | Agent Stability Framework — fault detection and soul alignment monitoring |

### 🧠 Prompt & Context Tools
| Product | Price | What It Does |
|---------|-------|-------------|
| **PromptGit** | $12 | Version control for prompts — diff, rollback, A/B compare |
| **PromptVault** | $19 | Team prompt library with categories, tags, and ratings |
| **ContextSlim** | $8 | Analyze what's eating your context window with compression advice |
| **OutputForge** | $8 | Reformat AI output for any platform (WordPress, Medium, email, PDF) |

### 💰 Cost & Token Management
| Product | Price | What It Does |
|---------|-------|-------------|
| **Token Tamer** | $15 | Monitor, budget, and optimize AI API spending with auto-throttling |
| **TokenBooks** | $15 | Unified dashboard across all AI providers — see where your money goes |
| **Cost Control** | $15 | 3-tier API spend protection with kill switch |

### 🔐 Privacy & Security
| Product | Price | What It Does |
|---------|-------|-------------|
| **RedactKit** | $15 | Scan and redact PII before sending to AI — reversible redaction |

### 💼 Business Tools
| Product | Price | What It Does |
|---------|-------|-------------|
| **ChatLift** | $8 | Export AI conversations to searchable local archives |
| **Invoice Forge** | $12 | Generate professional invoices from CLI — no SaaS needed |
| **FAQ Forge** | $12 | Build FAQ pages from Q&A data with multiple export formats |

### 📈 Trading Infrastructure
| Product | Price | What It Does |
|---------|-------|-------------|
| **Trading Scaffold** | $29 | Production-grade self-healing service framework |
| **Position Tracker** | $25 | Self-healing position state management with orphan detection |
| **Loss Forensics** | $29 | Systematic failure analysis framework for any domain |

### 🎁 Bundles (30-47% off)
- **AI Agent Infrastructure Pack** — $49 (saves $35)
- **AI Business Tools Pack** — $25 (saves $15)
- **AI Privacy & Quality Pack** — $35 (saves $25)
- **Trading Infrastructure Pack** — $59 (saves $39)
- **Complete Agent Toolkit** — $199 (saves $174)

All products: Python stdlib only • Zero external dependencies • CRUCIBLE-verified quality  
🛒 **Store:** https://shadowrose.gumroad.com  
☕ **Support:** https://ko-fi.com/theshadowrose

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
