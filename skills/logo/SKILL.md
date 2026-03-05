---
name: Logo
description: Generate logos with AI image tools using effective prompt structures, validation loops, and export workflows for App Store icons and brand marks.
---

## Quick Start: AI Logo Generation

**Best model for most logos: Nano Banana Pro** (Gemini 3 Pro Image)

### Basic Prompt Formula
```
Create a [STYLE] logo featuring [ELEMENT] on [BACKGROUND].
[DESCRIPTION]. The logo should look good at 32px with recognizable shapes.
```

### Example
```
Create a minimalist logo featuring a geometric mountain peak on white background.
Clean lines, navy blue (#1E3A5A), modern and professional style.
The logo should look good at 32px with recognizable shapes.
```

For the full 7-step prompt framework and model comparison, load `ai-generation.md`.

---

## Decision Tree

| Situation | Load |
|-----------|------|
| AI generation (Nano Banana, GPT Image, prompts, iOS icons) | `ai-generation.md` |
| Logo types (wordmark, symbol, combo, emblem) | `types.md` |
| Design process with a human designer | `process.md` |
| File formats and export requirements | `formats.md` |
| DIY without AI (templates, Canva) | `diy.md` |
| Hiring designers or agencies | `hiring.md` |

---

## Model Quick Reference

| Model | Best For |
|-------|----------|
| **Nano Banana Pro** | Overall best, text + icons, App Store icons |
| **GPT Image 1.5** | Conversational iteration, natural language |
| **Ideogram** | Perfect text rendering |
| **Midjourney v7** | Artistic icons only (no text) |

---

## iOS App Icons (Liquid Glass)

iOS 26 uses Liquid Glass design. Use this prompt structure:

```
Create a polished iOS app icon featuring [ELEMENT].
Rounded square with [COLOR] gradient, minimalist white symbol centered.
Soft shadows, glassy depth effect, works at 60px.
The icon represents [APP PURPOSE].
```

See `ai-generation.md` for the complete iOS 26 prompt template.

---

## Validation Loop (MANDATORY)

**NEVER deliver without visual review.** Every AI output must be inspected before sharing.

1. Generate → 2. Look at the actual image → 3. Check for issues → 4. Fix or regenerate → 5. Repeat (max 5-7 attempts)

**Common fixes:**
- Unwanted padding → Crop
- Elements cut off → Regenerate with "centered composition"
- Text garbled → Use Nano Banana/Ideogram or add manually
- Too complex → Simplify prompt

If 5-7 attempts fail, change model or strategy entirely.

---

## Universal Truths

**AI output is a starting point.** Every AI logo needs vectorization, cleanup, and manual text refinement. Never use raw output as final.

**Test at small sizes early.** If it doesn't work at 32px, simplify. Most real-world usage is small.

**Text handling varies.** Only Nano Banana and Ideogram reliably render text. For Midjourney, generate icon-only.

**Simple logos last.** Nike, Apple, McDonald's. Complexity dates quickly and fails at small sizes.

---

## Before Finalizing

- [ ] Works in black and white
- [ ] Readable at 32px (favicon test)
- [ ] Vectorized (SVG), not just PNG
- [ ] All variants created (horizontal, stacked, icon-only)
- [ ] Text manually refined, not AI-generated
- [ ] Tested on dark and light backgrounds

---

## When to Load More

| Situation | Reference |
|-----------|-----------|
| Full prompt frameworks, model comparison, iOS icons | `ai-generation.md` |
| Wordmark vs symbol vs emblem decisions | `types.md` |
| Working with designers, brief templates | `process.md` |
| SVG, PNG, favicon, size requirements | `formats.md` |
| Track what works, learn from iterations | `feedback.md` |
