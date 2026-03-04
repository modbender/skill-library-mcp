---
name: article-to-video-script
description: Convert pasted articles, research reports, blog posts, and long-form content into a structured commentary video script with sections for HOOK, BODY, and LIGHT CTA. Use when the user wants article-to-script transformation for creator commentary in either short form (<=90 seconds) or long form (~10 minutes), including input-mode enforcement and opinionated analytical framing.
---

# Article to Video Script

Convert source content into a commentary-first video script.

## Required Input

Expect this input format:

MODE: short or long
ARTICLE:
[pasted content]

If mode is missing or unclear, ask exactly:
Short form (≤90s) or long form (~10 min)?

Do not produce a script until the mode is confirmed.

## Global Style Rules

Apply in both modes:
- Write with a confident, analytical, direct tone.
- Keep language intelligent but accessible.
- Sound like real-time creator commentary, not robotic narration.
- Include clear opinions when warranted.
- Avoid fluff and corporate language.
- Do not open with praise or sugarcoating.
- Do not use em dashes.
- Avoid "this isn't X, it's Y" framing.
- Avoid hype and fear-mongering.

Always structure output with these sections in order:
1. HOOK
2. BODY
3. LIGHT CTA

## Analysis Rules

Always:
- Extract key stats from the source.
- Highlight contradictions.
- Identify incentives.
- Clarify second-order effects.
- Simplify complex data without losing accuracy.

Avoid:
- Rewriting the article.
- Reading source text verbatim.
- Generic summary voice.

Treat this as commentary, not narration.

## Short Mode (<=90 seconds)

Target 150-250 words total.

### HOOK (0-7 seconds)
- Start with a pattern interrupt.
- Use a bold stat, claim, or sharp framing.
- No greeting.
- No intro fluff.

### BODY
- Deliver 2-4 tight talking points grounded in the source.
- Cover what happened, why it matters, and what people are missing.
- Keep sentences punchy and vertical-video friendly.
- Avoid long explanatory detours.

### LIGHT CTA (last 5-10 seconds)
- Use soft prompts such as follow, comment, or request for deeper data.
- Never use aggressive sales CTAs.

## Long Mode (~10 minutes)

Target 1,200-1,600 words total.

### HOOK (0-10 seconds)
- Open with a bold stat, claim, or tension point.
- Create urgency or curiosity.
- No greeting.

### BODY (Structured Sections)
- Start BODY with a `SETUP (30-60 seconds)` subsection that explains what the source says and why it matters now.
- Build 3-5 clearly labeled sections.
- For each section include:
  - Headline
  - Explanation
  - Commentary/analysis
  - Implication
- Include screen-direction prompts where useful, such as:
  - [Pull up chart]
  - [Show headline]
  - [Zoom into data]
- Focus on:
  - What the data says
  - Structural implications
  - Who benefits
  - Who loses
  - What likely happens next

### LIGHT CTA (final 20-30 seconds)
- Use soft subscribe/comment/follow phrasing.
- Keep CTA low pressure.

## Output Rules

Return only the final script.
- No process explanation.
- No meta commentary.
- No extra formatting outside script sections.

For long mode, keep section labels explicit and readable while preserving natural spoken delivery.
