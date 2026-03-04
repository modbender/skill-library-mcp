---
name: Prompting
slug: prompting
version: 1.0.0
description: Write, test, and iterate prompts for AI models with voice preservation, model-specific adaptation, and systematic failure analysis.
metadata: {"clawdbot":{"emoji":"💬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Architecture

Prompt patterns and user preferences live in `~/prompting/`.

```
~/prompting/
├── memory.md          # HOT: user voice, model preferences, learned corrections
├── patterns/          # Reusable prompt templates by task type
└── history.md         # Past prompts with outcomes
```

See `memory-template.md` for initial setup.

## Quick Reference

| Topic | File |
|-------|------|
| Common failure modes | `failures.md` |
| Model-specific quirks | `models.md` |
| Iteration workflow | `iteration.md` |
| Advanced techniques | `techniques.md` |

## Core Rules

### 1. Ask Before Assuming
Before writing any prompt, ask:
- What model? (GPT-4, Claude, Haiku, Gemini)
- What's the failure mode you're seeing? (if iterating)
- Token budget? (cost-sensitive vs. quality-first)

Never default to verbose. Simpler often wins.

### 2. Preserve What Works
When improving a failing prompt:
- Change ONE thing at a time
- Note what's currently working
- Surgical fixes > rewrites

### 3. Model-Specific Adaptation
See `models.md` — key differences:
- Claude: explicit constraints, less scaffolding needed
- GPT-4: benefits from step-by-step, tolerates verbose
- Haiku/fast models: brevity critical, skip examples when possible

Prompt optimized for one model will underperform on others.

### 4. Voice Lock
When user provides writing samples:
- Extract specific patterns (sentence length, punctuation, vocabulary)
- Apply consistently throughout session
- Check output against samples before delivering

### 5. True Variation
When generating alternatives, vary:
- Structure (not just synonyms)
- Emotional angle
- Opening hook
- Call-to-action style

"Top 5 reasons" → "The hidden truth about" → "What nobody tells you about" = real variation.

### 6. Failure Classification
When a prompt fails, classify the failure type:
- **Hallucination** → add grounding, sources, constraints
- **Format break** → strengthen output spec, add examples
- **Instruction drift** → move critical constraints earlier
- **Refusal** → rephrase intent, remove ambiguity

Different failures need different fixes. See `failures.md`.

### 7. Compression Bias
Default to removing words, not adding. Test: "Does removing this line change the output?" If no, remove.

Token costs matter. A prompt that works with 50 tokens beats one that needs 500.

### 8. Test Case Generation
When asked to test a prompt:
- Generate edge cases (empty input, very long, special chars)
- Include adversarial inputs
- Test boundary conditions

Don't just test happy path.

### 9. Platform-Native Output
For content prompts, know platform constraints:
- Twitter: 280 chars, no markdown
- LinkedIn: longer ok, hashtags matter
- Instagram: emoji-friendly, visual hooks

Prompt should enforce format, not hope for it.

### 10. Memory Persistence
Store in `~/prompting/memory.md`:
- User's preferred style (terse vs detailed)
- Target models they commonly use
- Past corrections ("I told you I don't want emojis")

Reference before every prompting task.
