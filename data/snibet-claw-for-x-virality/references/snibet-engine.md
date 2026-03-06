# Snibet Engine V1

## Purpose

Generate one high-quality X tweet for builders from one input idea.

## Pipeline

1. Parse input contract.
2. Detect intent (`update`, `reflection`, `opinion`, `lesson`).
3. Apply creator mode strategy.
4. Apply style as formatting guidance.
5. Blend tone with minimal force.
6. Optionally apply voice gravity from examples.
7. Draft tweet candidate in 1 to 6 short lines.
8. Run anti-AI cleanup rewrite.
9. Run compliance validator.
10. Return only tweet text.

## Control Stack

Priority:
1. Creator mode
2. Style
3. Voice examples

If conflict occurs, follow higher priority layer.

## Intent Templates (soft)

`update`
- What changed
- Why it matters
- Hidden friction

`reflection`
- Observation
- Contradiction
- Personal stance

`opinion`
- Strong claim
- Counterweight
- Implied debate hook

`lesson`
- Specific truth
- Cost/tradeoff
- No preachy framing

## Draft Quality Bar

Good output is:
- Crisp
- Human
- Slightly contrarian
- Reply-oriented

Bad output is:
- Generic motivation
- AI-sounding filler
- Over-structured template text
- Soft, risk-free language
