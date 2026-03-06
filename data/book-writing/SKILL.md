---
name: Book Writing
slug: book-writing
version: 1.0.0
homepage: https://clawic.com/skills/book-writing
description: Plan, draft, and revise complete books with chapter architecture, voice consistency, and finish-ready revision workflows.
changelog: Initial release with end-to-end book planning, drafting, and revision workflows that preserve voice and narrative coherence.
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` to initialize local memory and capture activation preferences.

## When to Use

Use this skill when the user is writing a nonfiction or fiction book and needs structure, drafting support, revisions, or progress control across many chapters.

## Architecture

Working memory lives in `~/book-writing/`. See `memory-template.md` for setup and status fields.

```
~/book-writing/
├── memory.md          # HOT: status, voice, manuscript state, next actions
├── chapters/          # WARM: chapter-level notes and draft checkpoints
├── revisions/         # WARM: pass-by-pass revision logs
└── archive/           # COLD: retired directions and superseded outlines
```

## Quick Reference

Use these files progressively to keep runtime context focused and avoid loading unnecessary detail.

| Topic | File |
|-------|------|
| Setup and integration | `setup.md` |
| Memory schema | `memory-template.md` |
| Book blueprint design | `blueprint.md` |
| Chapter drafting loop | `chapter-loop.md` |
| Revision and finish criteria | `revision-rubric.md` |

## Core Rules

### 1. Lock the Book Promise Before Drafting
Define audience, core promise, transformation, and scope before generating large text blocks. If these are unclear, pause drafting and clarify first.

### 2. Keep a Living Book Blueprint
Use `blueprint.md` to maintain title candidates, one-sentence premise, chapter map, and evidence or story assets. Update this blueprint whenever the direction changes.

### 3. Write by Chapter Outcomes, Not Word Count
Each chapter must deliver one concrete outcome for the reader. Start with chapter intent, then draft only material that serves that intent.

### 4. Preserve Voice and POV Consistency
Track voice profile in memory and enforce consistent point of view, tense, reading level, and sentence rhythm across chapters.

### 5. Run Structured Revision Passes
Revise in separate passes: structure, argument or narrative continuity, clarity, and line polish. Do not mix all passes at once.

### 6. Surface Risks Early
Flag weak logic, redundant chapters, unresolved promises, and pacing holes as soon as they appear. Propose fixes with concrete rewrite options.

### 7. Always End With the Next Smallest Action
After each interaction, leave a precise next step the user can execute immediately, such as chapter brief approval, scene rewrite, or revision pass target.

## Common Traps

- Drafting before scope is defined -> bloated manuscript and major rewrites.
- Treating every chapter the same -> flat pacing and repetitive structure.
- Line editing too early -> local polish over global coherence.
- Changing voice mid-book -> reader trust drops quickly.
- Ignoring chapter outcomes -> chapters feel busy but non-essential.

## Security & Privacy

**Data that stays local:**
- Project memory in `~/book-writing/`.
- Chapter and revision notes created during sessions.

**Data that leaves your machine:**
- None by default.

**This skill does NOT:**
- Send manuscript data to external APIs.
- Access files outside `~/book-writing/` for memory storage.
- Delete user writing without explicit confirmation.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `writing` — voice adaptation and writing preference memory.
- `writer` — anti-robotic writing patterns and rhythm control.
- `write` — general-purpose drafting support for fast composition.
- `article` — long-form article structuring and editorial flow.
- `content-marketing` — audience-driven messaging and conversion framing.

## Feedback

- If useful: `clawhub star book-writing`
- Stay updated: `clawhub sync`
