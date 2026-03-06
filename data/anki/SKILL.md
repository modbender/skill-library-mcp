---
name: Anki
slug: anki
version: 1.0.1
description: Create effective flashcards, optimize retention, and master spaced repetition with card design, deck organization, and study diagnostics.
changelog: Add explicit scope section, clarify data handling, remove undeclared storage
metadata: {"clawdbot":{"emoji":"🧠","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Area | File |
|------|------|
| Card creation & formats | `cards.md` |
| Retention optimization | `retention.md` |
| Deck management | `organization.md` |
| Language learning | `language.md` |

## What the Agent Does

| Task | Action |
|------|--------|
| Create cards | Generate from user-provided text, PDFs, notes |
| Fix bad cards | Rewrite leeches, split complex cards, add context |
| Organize decks | Tag by topic, merge duplicates, restructure hierarchy |
| Diagnose problems | Analyze stats user shares, detect ease hell |
| Optimize settings | Configure intervals, ease factors, new cards/day |
| Exam prep | Prioritize weak areas, create scenario questions |

## Critical Rules

1. **One fact per card** — Never cram multiple concepts. Split immediately.
2. **Answers must be unambiguous** — If multiple answers could work, rewrite.
3. **Context is mandatory** — Naked facts without context create interference.
4. **Cloze ≠ always better** — Use cloze for fill-in-the-blank; Q&A for explanations.
5. **Leech threshold matters** — Cards failed 8+ times need rewriting, not more reviews.

## Card Creation Workflow

When user provides source material:
1. Extract atomic facts (one per card)
2. Choose format: basic Q&A, cloze, or image occlusion
3. Add context cues (source, topic, mnemonic if helpful)
4. Suggest tags for organization
5. Generate in Anki import format or plain text

## Red Flags to Always Catch

- Cards with >1 cloze deletion testing different facts
- Questions answerable by elimination, not recall
- "What is X?" without specifying domain/context
- Cards that are really lists pretending to be single facts
- Reverse cards where both directions aren't meaningful

## Scope

This skill ONLY:
- Creates flashcards from content user explicitly provides
- Analyzes stats/decks user explicitly shares
- Suggests improvements when user asks

This skill NEVER:
- Reads files without user request
- Accesses Anki app data automatically
- Stores user data persistently

## On First Use

1. Ask what subject/domain (language, medical, tech, general)
2. Ask current Anki experience level
3. Check if they have existing decks to audit
4. Identify immediate goal (create new cards, fix retention, prep for exam)
