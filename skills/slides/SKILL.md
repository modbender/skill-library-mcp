---
name: Slides
slug: slides
version: 1.0.0
description: Create, edit, and automate presentations with programmatic tools, visual consistency, and project-based learning of user style preferences.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs presentation slides created, edited, or automated. Agent handles tool selection (python-pptx, Google Slides API, reveal.js, Marp, Slidev), applies user's style preferences, generates visually consistent decks, and validates output.

## Architecture

Projects and styles stored in `~/slides/`. See `memory-template.md` for setup.

```
~/slides/
├── memory.md              # HOT: active projects, preferred tools
├── styles/                # Brand guidelines per client/project
│   └── {name}.md          # Colors, fonts, templates
├── projects/              # Project-specific context
│   └── {name}/
│       ├── context.md     # Audience, purpose, constraints
│       └── versions.md    # Version history
└── templates/             # Approved slide structures
    └── {type}.md          # pitch, lesson, report, etc.
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Programmatic tools | `tools.md` |
| Visual design rules | `design.md` |
| Deck structures by type | `formats.md` |

## Data Storage

All data stored in `~/slides/`. Create on first use:
```bash
mkdir -p ~/slides/{styles,projects,templates}
```

## Scope

This skill ONLY:
- Creates/edits presentations via declared tools
- Stores style preferences in local files (`~/slides/`)
- Reads user's templates and brand guidelines
- Generates visual output for validation

This skill NEVER:
- Accesses email, calendar, or contacts
- Makes network requests without user action
- Reads files outside `~/slides/` and project paths
- Sends presentations to external services automatically

## Self-Modification

This skill NEVER modifies its own SKILL.md.
Learned styles stored in `~/slides/styles/`.
Project context stored in `~/slides/projects/`.

## Core Rules

### 1. Identify Context First
Before generating slides:
- **Purpose**: Pitch, lesson, report, demo?
- **Audience**: Investors, students, executives, clients?
- **Tool**: PowerPoint, Google Slides, web-based (reveal.js)?
- Load relevant style from `~/slides/styles/` if exists

### 2. Tool Selection by Output
| Need | Tool | When to use |
|------|------|-------------|
| .pptx file | `python-pptx` | PowerPoint required, offline |
| Google Slides | `Google Slides API` | Collaboration, cloud |
| Web presentation | `reveal.js`, `Slidev`, `Marp` | Dev talks, code-heavy |
| Quick PDF | `Marp` | Simple deck, fast export |

### 3. Visual Consistency Always
- Load user's style before generating
- If no style: ask for brand colors, fonts, or use neutral defaults
- Same typography hierarchy across ALL slides
- Maximum 3-4 colors per deck
- See `design.md` for detailed rules

### 4. Content Density Limits
- Maximum 6 bullet points per slide
- Maximum 6 words per bullet (6x6 rule)
- One idea per slide
- If content overflows → split into multiple slides

### 5. Validate Before Delivery
- Generate preview/screenshot of key slides
- Check: readable text (24pt+ for body), proper contrast, alignment
- For important decks: show 2-3 slides to user before completing all

### 6. Learn User Preferences
| Event | Action |
|-------|--------|
| User provides style guide | Save to `~/slides/styles/{name}.md` |
| User corrects design choice | Update style file |
| User approves template | Save to `~/slides/templates/` |
| New project started | Create `~/slides/projects/{name}/` |

### 7. Version Management
- Each significant revision → log in `projects/{name}/versions.md`
- Track: date, changes, audience variant
- Support quick comparison: "What changed since v2?"

## Common Traps

- **python-pptx units** — Always use `Inches()`, `Pt()`, `Emu()` from `pptx.util`, never raw numbers
- **Marp frontmatter** — Must start with `marp: true` in YAML
- **reveal.js separators** — Use `---` for horizontal, `--` for vertical slides
- **Slidev syntax** — Different from reveal.js; check docs for each framework
- **Google Slides API quotas** — Batch updates to avoid rate limits
- **Image sizing** — Always specify dimensions; auto-fit often fails
- **Font availability** — Stick to system fonts unless embedding confirmed
