---
name: humanizer-pro
description: Transform AI-generated text into authentic human writing. Detects and removes 24 AI patterns, replaces 500+ AI vocabulary terms, analyzes statistical signals (burstiness, vocabulary diversity), and injects personality through strategic misspellings, parenthetical asides, tangents, and random thoughts. Use when humanizing content, checking for AI tells, removing robotic patterns, adding natural voice, making text sound less polished, or when asked to write like a specific person. Works with social posts, articles, emails, marketing copy, documentation—any text that needs to sound genuinely human.
---

# Humanizer Pro

Transform AI-generated text into authentic human writing by removing robotic patterns and injecting natural personality.

## What This Skill Does

**Core Capabilities:**
- Detects 24 AI writing patterns (significance inflation, promotional language, filler phrases, etc.)
- Identifies 500+ AI vocabulary terms across 3 severity tiers
- Analyzes statistical signals (burstiness, type-token ratio, sentence uniformity)
- Removes chatbot artifacts and sycophantic tone
- **NEW:** Injects personality through parenthetical asides, strategic typos, tangents, and random thoughts

**Based on:** Wikipedia's "Signs of AI writing", Copyleaks research, and real-world pattern analysis.

## Quick Start

### Basic Humanization

When asked to humanize text:

1. **Scan for patterns** → Check all 24 patterns in `references/patterns.md`
2. **Check vocabulary** → Flag Tier 1/2/3 terms from `references/vocabulary.md`
3. **Analyze statistics** → Compute burstiness, TTR, sentence variance
4. **Rewrite** → Remove AI-isms, add personality
5. **Verify** → Read aloud, check if it sounds natural

### Adding Personality

Use the new personality injection features from `references/personality-injection.md`:

- **Parenthetical asides** → (honestly, this part gets me every time)
- **Strategic misspellings** → Natural typos that don't hurt credibility
- **Tangents** → "wait, that reminds me..." moments
- **Random thoughts** → Going off script with authentic reactions

## When to Use Each Component

### Always Check (Core Patterns)

- **Tier 1 vocabulary** → DEAD GIVEAWAYS, ban completely (delve, tapestry, vibrant, seamless, etc.)
- **Filler phrases** → "in order to" → "to", "due to the fact that" → "because"
- **Chatbot artifacts** → "Great question!", "I hope this helps!", "Let me know if..."
- **Generic conclusions** → "The future looks bright", "Exciting times lie ahead"

### Check When Relevant

- **Promotional language** → If writing about places, products, services
- **Significance inflation** → If discussing history, events, milestones
- **Vague attributions** → If making claims without sources
- **Em dash overuse** → If text has many — dashes — everywhere

### Advanced Analysis

For comprehensive humanization or when scoring text:

1. Read `references/patterns.md` → All 24 patterns with examples
2. Read `references/vocabulary.md` → Complete AI term database
3. Read `references/statistical-signals.md` → Burstiness, TTR, readability formulas
4. Read `references/personality-injection.md` → How to add human touches

## Core Principles

### Write Like a Human, Not a Press Release

- Use "is" and "has" freely — "serves as" is pretentious
- One qualifier per claim — don't stack hedges
- Name your sources or drop the claim
- End with something specific, not vague optimism

### Add Actual Personality

- **Have opinions** → React to facts, don't just report them
- **Vary rhythm** → Short. Then longer ones that meander a bit.
- **Acknowledge complexity** → "I genuinely don't know how to feel about this"
- **Let mess in** → Perfect structure feels algorithmic
- **Use contractions** → "don't", "won't", "it's" (natural speech)
- **Sentence fragments** → When it makes sense. Like this.

### Cut the Fat

Remove these automatically:
- "In order to" → "to"
- "Due to the fact that" → "because"
- "At this point in time" → "now"
- "It is important to note that" → (just say it)
- "In the event that" → "if"

## The 24 Patterns (Quick Reference)

For full details with examples, see `references/patterns.md`.

| # | Pattern | What to Watch For |
|---|---------|-------------------|
| 1 | Significance inflation | "marking a pivotal moment in the evolution of..." |
| 2 | Notability name-dropping | Listing media outlets without specific claims |
| 3 | Superficial -ing analyses | "...showcasing... reflecting... highlighting..." |
| 4 | Promotional language | "nestled", "breathtaking", "stunning", "renowned" |
| 5 | Vague attributions | "Experts believe", "Studies show", "Industry reports" |
| 6 | Formulaic challenges | "Despite challenges... continues to thrive" |
| 7 | AI vocabulary (500+ words) | "delve", "tapestry", "landscape", "showcase" |
| 8 | Copula avoidance | "serves as", "boasts" instead of "is", "has" |
| 9 | Negative parallelisms | "It's not just X, it's Y" |
| 10 | Rule of three | "innovation, inspiration, and insights" |
| 11 | Synonym cycling | "protagonist... main character... central figure..." |
| 12 | False ranges | "from the Big Bang to dark matter" |
| 13 | Em dash overuse | Too many — dashes — everywhere |
| 14 | Boldface overuse | Mechanical emphasis everywhere |
| 15 | Inline-header lists | "- Topic: Topic is discussed here" |
| 16 | Title Case headings | Every Main Word Capitalized |
| 17 | Emoji overuse | 🚀💡✅ decorating professional text |
| 18 | Curly quotes | "smart quotes" instead of "straight quotes" |
| 19 | Chatbot artifacts | "I hope this helps!", "Let me know if..." |
| 20 | Cutoff disclaimers | "As of my last training...", "While details are limited..." |
| 21 | Sycophantic tone | "Great question!", "You're absolutely right!" |
| 22 | Filler phrases | "In order to", "Due to the fact that" |
| 23 | Excessive hedging | "could potentially possibly", "might arguably" |
| 24 | Generic conclusions | "The future looks bright", "Exciting times lie ahead" |

## Vocabulary Tiers

### Tier 1 (Dead Giveaways - NEVER USE)
delve, tapestry, vibrant, crucial, comprehensive, meticulous, embark, robust, seamless, groundbreaking, leverage, synergy, transformative, paramount, multifaceted, myriad, cornerstone, reimagine, empower, catalyst, invaluable, bustling, nestled, realm

### Tier 2 (Suspicious - Use Sparingly)
furthermore, moreover, paradigm, holistic, utilize, facilitate, nuanced, illuminate, encompasses, catalyze, proactive, ubiquitous, quintessential

### Tier 3 (Context-Dependent - Watch Density)
landscape (abstract), journey (metaphorical), ecosystem, framework, roadmap, touchpoint, pain point, streamline, optimize, scalable

**See `references/vocabulary.md` for the complete 500+ term database.**

## Statistical Signals

Check these when doing comprehensive analysis:

| Signal | Human | AI | Why |
|--------|-------|----|----|
| Burstiness | 0.5-1.0 | 0.1-0.3 | Humans write in bursts; AI is metronomic |
| Type-token ratio | 0.5-0.7 | 0.3-0.5 | AI reuses vocabulary |
| Sentence length CoV | High | Low | AI makes same-length sentences |
| Trigram repetition | <0.05 | >0.10 | AI reuses 3-word phrases |

**See `references/statistical-signals.md` for formulas and implementation.**

## Personality Injection (NEW)

When asked to add human touches or make text sound less perfect:

### 1. Parenthetical Asides
Add authentic reactions in parentheses:
- **(honestly, this part gets me every time)**
- **(which, let's be real, is kind of absurd)**
- **(I still don't fully understand why)**

**Rule:** Use for genuine reactions, not filler. 1-3 per 500 words max.

### 2. Strategic Misspellings
Natural typos that don't hurt credibility:
- Acceptable: "teh" → "the", "recieve" → "receive", "definately" → "definitely"
- Avoid: Professional contexts, names, technical terms, key claims

**Rule:** 1-2 per 1000 words in casual contexts only.

### 3. Tangents and Going Off Script
Let thoughts wander naturally:
- "Speaking of which..."
- "That reminds me..."
- "Okay, slight tangent..."
- "Wait, this connects to..."

**Rule:** Allow 1-2 per longer piece (1000+ words).

### 4. Random Thoughts
Inject authentic human processing:
- "Honestly didn't think this would work but..."
- "I keep coming back to..."
- "There's something unsettling about..."
- "I genuinely don't know how to feel about this"

**Rule:** Use when genuine uncertainty or strong reaction fits.

**See `references/personality-injection.md` for comprehensive examples and context guidance.**

## Process

1. **Read the input text carefully**
2. **Identify all pattern instances** (use the 24-pattern checklist)
3. **Flag vocabulary issues** (Tier 1 = remove, Tier 2 = reduce, Tier 3 = watch density)
4. **Check statistics** (if comprehensive analysis requested)
5. **Rewrite problematic sections**
6. **Add personality** (if requested or if text is sterile)
7. **Verify naturally** (read aloud, check rhythm)
8. **Present humanized version** with brief change summary

## Example Transformation

### Before (AI-sounding)
Great question! Here is an overview of sustainable energy. Sustainable energy serves as an enduring testament to humanity's commitment to environmental stewardship, marking a pivotal moment in the evolution of global energy policy. In today's rapidly evolving landscape, these groundbreaking technologies are reshaping how nations approach energy production, underscoring their vital role in combating climate change. The future looks bright. I hope this helps!

### After (Humanized)
Solar panel costs dropped 90% between 2010 and 2023 (according to IRENA data). That single fact explains why adoption took off—it stopped being an ideological choice and became an economic one.

Germany gets 46% of its electricity from renewables now. The transition is happening, but it's messy and uneven, and the storage problem is still mostly unsolved.

### Changes Made
- Removed "Great question!" and "I hope this helps!" (chatbot artifacts)
- Removed "serves as an enduring testament" (significance inflation)
- Removed "marking a pivotal moment" (AI vocabulary)
- Removed "rapidly evolving landscape" (AI vocabulary)
- Removed "groundbreaking", "underscoring", "vital" (AI vocabulary)
- Removed "The future looks bright" (generic conclusion)
- Added specific data points and sources
- Added personal observation (parenthetical)
- Added acknowledgment of complexity
- Varied sentence rhythm

## Using the CLI Tool

The `scripts/humanize.js` tool provides command-line access:

```bash
# Score text (0-100, higher = more AI-like)
node scripts/humanize.js score "Your text here"

# Full analysis report
node scripts/humanize.js analyze -f draft.md

# Humanization suggestions
node scripts/humanize.js suggest article.txt

# Auto-fix common patterns
node scripts/humanize.js fix --autofix -f article.txt
```

## Always-On Mode

To make this skill's rules your default writing style (not just when explicitly asked to humanize):

1. Ban Tier 1 vocabulary completely from all writing
2. Kill filler phrases automatically
3. No sycophancy, chatbot artifacts, or generic conclusions
4. Vary sentence length, have opinions, use concrete specifics
5. If you wouldn't say it in conversation, don't write it

These rules can be added to SOUL.md or agent personality config for permanent application.

## Tips for Effective Humanization

- **Start with Tier 1 vocabulary** → Easiest wins, most obvious AI tells
- **Check for em dashes** → Quick scan for — overuse
- **Read the last paragraph** → Generic conclusions are common
- **Listen to rhythm** → Read aloud, hear if it sounds robotic
- **Don't over-polish** → Some imperfection is human
- **Match the context** → Formal documents need different treatment than social posts
- **Preserve meaning** → Remove patterns without changing core message

## Troubleshooting

**Text still sounds robotic after fixing patterns?**
→ You removed AI tells but didn't add personality. Review `references/personality-injection.md`.

**Humanization made text too casual?**
→ Personality injection should match context. Use fewer asides/typos in formal writing.

**Text is TOO perfect now?**
→ Add strategic imperfection: vary sentence length, include a tangent, acknowledge uncertainty.

**Not sure if a word is AI vocabulary?**
→ Check `references/vocabulary.md`. When in doubt, ask "Would I say this in conversation?"
