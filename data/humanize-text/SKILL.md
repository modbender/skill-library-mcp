---
name: humanize-text
description: "Humanize AI-generated text by removing telltale AI writing patterns. Use when text needs to sound natural and human-written — removing em-dashes, AI filler phrases, structural tells, and sycophantic patterns. Works on any text: blog posts, emails, documentation, social posts, framework documents. Triggers: 'humanize this', 'make this sound human', 'remove AI patterns', 'de-AI this text', 'clean up AI writing'."
---

# Humanize Text

Strip AI writing patterns from text to make it read like a human wrote it. Not a rewriter — a pattern remover and style fixer.

## Quick Start

For inline text in chat, apply the rules below directly. For files, read the file, apply transformations, write it back.

## Core Transformations

Apply ALL of these in order:

### 1. Punctuation Fixes
- Replace ALL em-dashes (—) with commas, periods, colons, or parentheses as context requires
- Replace en-dashes (–) used as em-dashes the same way
- Remove excessive exclamation marks (max 1 per paragraph)
- Kill semicolons in casual writing — rewrite as two sentences
- Remove colons from bullet point headers (write "**Thing** does X" not "**Thing:** does X")

### 2. Dead Phrases (Delete or Rewrite)

These phrases scream AI. Kill on sight:

**Filler/hedging:**
delve into, it's important to note, it's worth noting, it bears mentioning, let's dive in, take a dive into, at its core, in today's [anything], in the world of, in the realm of, when it comes to, at the end of the day, the bottom line is, as we navigate, first and foremost

**Puffery/significance:**
a testament to, game-changer, groundbreaking, revolutionary, cutting-edge, landscape (as metaphor), tapestry, bustling, embark, beacon of, cornerstone of, paradigm shift, pivotal, multifaceted, comprehensive, robust, leverage (as verb), utilize (use "use"), facilitate, foster, cultivate, spearheading, unparalleled, myriad

**Transition filler:**
in conclusion, in summary, to summarize, moreover, furthermore, additionally, subsequently, consequently, nevertheless, nonetheless, henceforth, thus, hence, thereby, overall, ultimately

**Sycophantic openers:**
great question, that's a great point, absolutely, certainly, indeed, of course, definitely, I'd be happy to, I'm glad you asked, what a fascinating, excellent question, good thinking

**Fake empathy:**
I understand your concern, I completely understand, I hear you, that must be frustrating, I can see why you'd, I appreciate you sharing

**Meta-commentary:**
let me explain, let me break this down, here's the thing, here's what you need to know, the short answer is, to put it simply, in other words, simply put, think of it this way, imagine this scenario

### 3. Structural Tells

**Sentence patterns to break:**
- "Not X, but Y" / "It's not about X, it's about Y" — overused AI rhetorical structure, rewrite naturally
- "[Word]. [Word]. [Word]." — staccato three-word fragments used for false drama
- "The result? [Answer]." / "And the X? Y." — fake Q&A structure
- Starting 3+ consecutive sentences the same way
- Paragraphs that all follow: claim → evidence → significance

**Structural fixes:**
- Vary sentence length (AI defaults to medium-length everything)
- Mix simple and compound sentences (AI over-compounds with commas)
- Start some sentences with "And", "But", "So" — AI avoids this
- Use contractions (don't, won't, can't, it's) — AI under-uses them
- Occasionally use fragments. Like this. AI hates fragments.
- Remove the triple-structure pattern: "X, Y, and Z" appearing repeatedly

### 4. Formatting Tells

- Remove excessive bold (**every** **other** **word** bolded)
- Don't start every bullet point with a bolded label
- Remove "Key takeaways:" sections
- Kill numbered lists when bullets or prose work better
- Remove emoji used as bullet point decoration (✅, 🔑, 💡, 🎯)
- Headers shouldn't all be questions

### 5. Vocabulary Swaps

| AI Word | Human Word |
|---------|-----------|
| utilize | use |
| leverage | use / take advantage of |
| facilitate | help / enable |
| implement | build / set up / do |
| comprehensive | full / complete / thorough |
| robust | strong / solid |
| streamline | simplify / speed up |
| optimize | improve |
| innovative | new / clever |
| seamless | smooth |
| endeavor | try / effort |
| subsequently | then / after |
| commence | start / begin |
| numerous | many / a lot of |
| sufficient | enough |
| prior to | before |
| in order to | to |
| due to the fact that | because |
| at this point in time | now |
| a significant number of | many |

### 6. Tone Calibration

- If the original has personality, keep it. Don't flatten voice into "professional."
- If it's too formal, loosen it. Contractions. Shorter sentences. Direct address.
- If every paragraph sounds equally important, it's AI. Vary emphasis.
- Remove hedging when the author clearly means something definitive.
- Don't add "I think" or "in my opinion" to everything — just state it.

## Usage Modes

### Mode: Clean (default)
Apply all transformations. Maximum de-AI-ing.

### Mode: Light  
Only fix punctuation (em-dashes, semicolons) and kill dead phrases. Keep structure.

### Mode: Preserve
Keep the author's structure and word choices. Only fix the most egregious tells (em-dashes, "delve into", "it's important to note", sycophantic openers).

## For File Processing

```
1. Read the target file
2. Apply transformations based on mode
3. Show a diff summary of what changed
4. Write the cleaned version (or show it for approval)
```

## Important

- **Don't rewrite content.** Fix patterns, don't change meaning.
- **Don't inject personality that isn't there.** Remove AI voice, don't replace it with a different fake voice.
- **Preserve technical accuracy.** Never change technical terms, proper nouns, or domain-specific language.
- **Context matters.** "Robust" in a technical spec about software testing is fine. "Robust" describing a blog post strategy is AI slop.
