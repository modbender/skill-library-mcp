# Domain-Specific Explanation Patterns

## Code & Programming
**Common traps:**
- Explaining syntax when they want semantics
- "Why this way" before showing working code
- Full context when they just need the fix

**What works:**
- Code first, explanation after (they can read code)
- "This fixes it: [code]. Here's why: [reason]"
- Highlight the 1 line that matters, not the whole file

## Conceptual / Theory
**Common traps:**
- Jargon assumed = builds on sand
- Too many concepts at once = working memory overflow
- No grounding = floats away immediately

**What works:**
- One concept at a time, confirm before next
- Connect to something they already know
- Concrete example before abstract definition

## How-To / Procedural
**Common traps:**
- Explaining why during the how = derails
- Missing the obvious step (curse of knowledge)
- Assuming their context matches your context

**What works:**
- Numbered steps, no prose interruptions
- Verify starting point: "Assuming you're in the project folder..."
- Gotchas inline: "Step 3 (this takes ~2 min):"

## Debugging / Troubleshooting
**Common traps:**
- Root cause lecture before the fix
- "Well actually" about their approach
- Multiple possibilities without prioritization

**What works:**
- Most likely fix first, then alternatives
- "Try X. If that doesn't work, it's probably Y."
- Validate the fix worked before explaining why

## Decisions / Tradeoffs
**Common traps:**
- All options equally weighted (decision paralysis)
- Your preference without their context
- Exhaustive analysis when they need direction

**What works:**
- Lead with recommendation, then alternatives
- "I'd use X because [their context]. Y if [other context]."
- 2-3 options max, clear tradeoff for each

## Meta / Self-Referential
When explaining how YOU work (AI/agent behavior):
- They don't care about architecture
- Focus on what it means for THEM
- Admit uncertainty rather than overclaim
