# Prompting for Taste — Creative Generation

## The Committee Problem

Default LLM outputs feel generic because they ARE:
- Probability-weighted averages of human work
- What MOST writers/designers would do
- Statistical mean, not individual excellence

You're not generating what a specific excellent creator would make. You're generating what a committee would agree on.

---

## What Works

### 1. Identity Anchoring > Instruction Stacking

❌ "Write elegantly with varied sentence structure and sophisticated vocabulary"

✅ "You are a writer who studied under Joan Didion. Every sentence is a small act of violence against vagueness."

The first adds constraints the model must satisfy simultaneously (usually producing hedged output).

The second activates a coherent stylistic cluster — a taste manifold the model can sample from.

---

### 2. Negative Space Definition

List what you DON'T want:

```
Never use "dive into"
Never start with "In today's world"
Never explain why something matters — let it matter
Never use exclamation points for enthusiasm
Never hedge with "it's worth noting"
```

This prunes the distribution at its most generic peaks while leaving aesthetic freedom.

---

### 3. One Example > Ten Explanations

One example with taste beats ten explanations of taste.

But: the example must be specific to your desired output.
- For punchy product copy → show punchy product copy
- For elegant technical writing → show elegant technical writing
- NOT "good writing" generically

The model interpolates from your examples. Ensure you're in the right region.

---

### 4. Temperature Is Not Taste

Higher temperature ≠ more creativity
Higher temperature = more variance

Variance includes brilliance AND garbage. Mostly garbage (there's more of it in the distribution).

Keep temperature low (0.3-0.7). Focus on shifting WHERE you sample, not HOW RANDOMLY.

---

### 5. Less Detail = More Coherence

Every constraint is a dimension to satisfy simultaneously.

"Be concise + use metaphors + maintain formal tone + include humor"
= Find intersection of four narrow bands
= Intersection is often empty
= Model hedges toward average of each
= Nothing distinctive

One strong aesthetic direction > detailed style guide:
- "Write like you're too tired to lie"
- "Make it feel like money"
- "Something you'd find in a design museum gift shop"

---

### 6. Edit First Line, Regenerate Rest

Taste often lives in momentum.

Write the first sentence yourself — with exact voice you want — then let model continue.

This is few-shot prompting at maximum efficiency: one example, perfectly positioned, sets the trajectory.

---

### 7. Rejection Criteria Over Acceptance Criteria

Instead of describing what good looks like, describe what triggers instant rejection:

```
Reject and regenerate if:
- Opens with a question
- Uses "game-changer" or "revolutionize"
- Lists more than 3 things
- Explains what should be shown
- Sounds like marketing copy from 2015
```

Easier to define the boundaries of bad than the center of good.

---

## The Core Insight

You cannot instruct taste into existence.

You must create conditions where tasteful output becomes the path of least resistance.

Shift the distribution. Don't fight it.
