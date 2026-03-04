# Hook Brainstorming Prompts

These are prompts the agent uses to generate batches of new hooks. Each prompt is designed to produce 5 to 10 hooks at once for a specific formula category.

Before using any prompt:
1. Read `workspace/context/product.md` for the product, features, and audience.
2. Read `workspace/context/brand-voice.md` for the tone and style.
3. Read `workspace/hooks/formulas.md` for the formula patterns.
4. Read `workspace/performance/insights.md` for what has worked and what has not.

Replace ALL placeholders before using.

---

## Prompt: Generate Person + Conflict Hooks

```
I need 8 TikTok slideshow hooks using the "Person + Conflict" formula for [PRODUCT NAME].

Product: [ONE-LINER DESCRIPTION]
Target audience: [TARGET AUDIENCE]
Key features: [FEATURE 1], [FEATURE 2], [FEATURE 3]
Brand voice: [VOICE DESCRIPTION]

The formula is: [Person] said [doubt or objection about the product's value]. So I showed them [what the product does]. [Reaction].

Rules:
- Each hook should name a specific person (roommate, mom, boyfriend, coworker, trainer, sister, best friend, neighbor)
- Each hook should have a different specific objection
- The objection should feel real and natural, like something that person would actually say
- Keep the slide 1 text under 15 words
- Use conversational language, no marketing speak
- Do not use em-dashes
- Vary the relationship and the objection across all 8 hooks

For each hook, provide:
1. The full hook concept (one sentence summary)
2. The exact slide 1 text (what people see first)

[OPTIONAL: If performance data exists]
These hook styles have worked well before: [TOP PERFORMING HOOKS]
These hook styles have not worked: [UNDERPERFORMING HOOKS]
Lean toward the style of the winners.
```

---

## Prompt: Generate Educational / Tips Hooks

```
I need 6 TikTok slideshow hooks using the "Educational / Tips" formula for [PRODUCT NAME].

Product: [ONE-LINER DESCRIPTION]
Problem space: [THE PROBLEM THE PRODUCT SOLVES]
Target audience: [TARGET AUDIENCE]
Brand voice: [VOICE DESCRIPTION]

The formula is: [Number] [things/mistakes/hacks] about [topic] that [surprising claim]

Rules:
- Each hook should teach something genuinely useful about [PROBLEM SPACE]
- Include a number in each hook (3, 5, or 7 work best)
- The claim should be surprising, counterintuitive, or provoke curiosity
- Keep the slide 1 text under 15 words
- The product is introduced naturally on slide 5, not in the hook itself
- Conversational tone, no jargon
- Do not use em-dashes
- Vary the topics across all hooks. Cover different angles of the problem space.

For each hook, provide:
1. The full hook concept
2. The exact slide 1 text
3. Brief notes on what the 3 tips would be
```

---

## Prompt: Generate Before / After Hooks

```
I need 5 TikTok slideshow hooks using the "Before / After" formula for [PRODUCT NAME].

Product: [ONE-LINER DESCRIPTION]
Key benefits: [BENEFIT 1], [BENEFIT 2], [BENEFIT 3]
Target audience: [TARGET AUDIENCE]
Brand voice: [VOICE DESCRIPTION]

The formula is: [Metric or situation] before [product] vs after. [Specific improvement].

Rules:
- Each hook should focus on a different benefit or metric
- Include specific, believable numbers or timelines where possible
- The "before" state should be universally relatable for the target audience
- The "after" state should be aspirational but realistic
- Keep the slide 1 text under 15 words
- Conversational tone
- Do not use em-dashes
- Avoid exaggeration. Understated honesty beats hype.

For each hook, provide:
1. The full hook concept
2. The exact slide 1 text
3. The specific before/after contrast
```

---

## Prompt: Generate Relatable Pain Point Hooks

```
I need 6 TikTok slideshow hooks using the "Relatable Pain Point" formula for [PRODUCT NAME].

Product: [ONE-LINER DESCRIPTION]
Problems it solves: [PROBLEM 1], [PROBLEM 2], [PROBLEM 3]
Target audience: [TARGET AUDIENCE]
Brand voice: [VOICE DESCRIPTION]

The formula is: That moment when [universal frustration]... [expansion] [plot twist: there is a fix]

Rules:
- Each hook should describe a frustration that the target audience experiences regularly
- The frustration should be specific and vivid, not vague
- Use "that moment when", "POV:", "when you realize", or similar framing
- Humor is encouraged but not required. Empathy works too.
- The product appears on slide 4 or 5, not in the hook itself
- Keep the slide 1 text under 15 words
- Conversational, authentic tone
- Do not use em-dashes
- These hooks should make people want to tag a friend or comment "this is me"

For each hook, provide:
1. The full hook concept
2. The exact slide 1 text
3. The specific pain point being addressed
```

---

## Prompt: Generate POV / Lifestyle Hooks

```
I need 4 TikTok slideshow hooks using the "POV / Lifestyle" formula for [PRODUCT NAME].

Product: [ONE-LINER DESCRIPTION]
Lifestyle benefits: [HOW THE PRODUCT IMPROVES DAILY LIFE]
Target audience: [TARGET AUDIENCE]
Brand voice: [VOICE DESCRIPTION]

The formula is: POV: You [aspirational or relatable scenario that the product enables]

Rules:
- Each hook should paint a vivid, desirable scenario
- The product should be a natural part of the lifestyle, not the main focus
- The viewer should be able to imagine themselves in the scene
- Mix aspirational scenarios (things people want) with relatable ones (things people do)
- Keep the slide 1 text under 15 words
- The tone should feel like a daydream or a calm, satisfying moment
- Do not use em-dashes

For each hook, provide:
1. The full hook concept
2. The exact slide 1 text
3. The lifestyle scenario in 1 to 2 sentences
```

---

## Prompt: Refresh Hooks Based on Performance

Use this when updating the hook library after a weekly review.

```
Based on performance data, I need to refresh the hook library for [PRODUCT NAME].

Product: [ONE-LINER DESCRIPTION]
Target audience: [TARGET AUDIENCE]

Top performing hooks (model these):
[LIST TOP 3-5 HOOKS WITH THEIR VIEW COUNTS]

Underperforming hooks (avoid these patterns):
[LIST BOTTOM 3-5 HOOKS WITH THEIR VIEW COUNTS]

Analysis of what works:
[INSIGHTS FROM workspace/performance/insights.md]

Generate 10 new hooks:
- 4 using the Person + Conflict formula (varied from winners)
- 2 using Educational / Tips
- 2 using Relatable Pain Point
- 1 using Before / After
- 1 using POV / Lifestyle

Rules:
- Each hook should feel fresh, not a copy of an existing winner
- Lean into the patterns that work, avoid the patterns that fail
- Vary the angle, person, and situation across all hooks
- Keep slide 1 text under 15 words
- Conversational, authentic, human-sounding
- Do not use em-dashes

For each hook, provide:
1. Formula category
2. The full hook concept
3. The exact slide 1 text
4. Why this hook should work (based on the performance patterns)
```

---

## Usage Notes

- Generate hooks in batches of 5 to 10 at a time for efficiency.
- Always review generated hooks against the quality criteria in `workspace/hooks/formulas.md` before adding to the library.
- Present the top candidates to the user for feedback before finalizing.
- Track which prompts produce the best hooks over time and note it in `workspace/performance/insights.md`.
- Refresh the library weekly. Target 20 to 40 active hooks at all times.
