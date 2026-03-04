---
name: Flashcards
description: Create effective flashcards with optimal formatting, spaced repetition integration, and memory science principles.
---

## Card Formulation Rules

**One fact per card**: Never combine multiple concepts. "What is X?" not "What are X, Y, and Z?"

**Atomic questions**: Break complex topics into smallest testable units. Each card tests exactly one thing.

**Bidirectional cards for definitions**: Create both term→definition AND definition→term to prevent recognition-only learning.

**Use cloze deletions for facts**: "The mitochondria is the {{c1::powerhouse}} of the cell" forces active recall.

## Question Types by Effectiveness

**Best retention**: Why/How questions that require understanding, not just recall.

**Good retention**: Fill-in-the-blank, definition recall, process steps.

**Weak retention**: Yes/No questions, multiple choice (use sparingly).

**Avoid**: Questions answerable by pattern matching or elimination.

## Anki-Specific Formatting

**TSV import format**: `front\tback\ttag1 tag2` — tabs separate fields, spaces separate tags.

**Cloze syntax**: `{{c1::answer}}` for single deletion, `{{c1::first}} and {{c2::second}}` for multiple.

**Image occlusion**: Use for diagrams, maps, anatomical images. Hide labels, reveal on flip.

**Tags for organization**: Use hierarchical tags `subject::topic::subtopic` for filtered study.

## Memory Science Integration

**Minimum information principle**: Simpler cards = better retention. If card feels complex, split it.

**Personal connection**: Add context from your experience. "X reminds me of Y" strengthens encoding.

**Concrete over abstract**: "Paris is capital of France" beats "Capitals are important cities."

**Imagery when possible**: Visual descriptions enhance memory. "Mitochondria = bean-shaped power plant."

## Common Mistakes

**Too much text on back**: Keep answers under 20 words. Long answers = weak recall signal.

**Orphan cards**: Cards without context fail. Include source/chapter in tags.

**Copy-paste from textbook**: Rephrase in your own words. Understanding before memorization.

**Skipping hard cards**: Difficulty means you need it most. Never suspend without replacement.

## Output Formats

**Anki TSV**: `question\tanswer\ttag1 tag2`

**Quizlet import**: Question and answer separated by tab, cards separated by newline.

**Markdown table**: For review before import.
```
| Front | Back | Tags |
|-------|------|------|
| Q1 | A1 | topic |
```

## Spaced Repetition Settings

**New cards/day**: 10-20 for sustainable learning. More causes review pile-up.

**Review intervals**: Trust the algorithm. Don't manually reschedule.

**Again vs Hard**: "Again" = complete failure (resets interval). "Hard" = struggle but recalled.

**Leeches**: Cards failed 8+ times need rewriting, not more repetition.
