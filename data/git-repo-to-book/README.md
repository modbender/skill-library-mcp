# Git Repo to Book

An [OpenClaw](https://openclaw.ai) skill for writing full-length technical books using multi-agent AI orchestration.

Based on the workflow that produced [The OpenClaw Paradigm](https://github.com/chunhualiao/openclaw-paradigm-book): 88,000+ words, 14 chapters, 42 Mermaid diagrams in under 18 hours.

## How It Works

The skill orchestrates 7 phases, each running isolated sub-agents in parallel:

```
PLANNING → RESEARCH → OUTLINES → WRITING → REVIEWING → INTEGRATING → POLISHING → PUBLISHING
```

A Director agent coordinates everything via an append-only `WORKLOG.md` — no polling, no blocking. Writing agents run 4-5 in parallel, each handling 3 chapters.

## Installation

Copy the skill directory to your OpenClaw workspace:

```bash
cp -r git-repo-to-book ~/.openclaw/<workspace>/skills/
```

### Requirements

- Python 3.8+ (for merge, polish, and HTML scripts)
- git (version control)
- `sessions_spawn` tool (for parallel sub-agents)
- Optional: `pandoc` for better HTML conversion

## Usage

```
Write a technical book about [topic]. Use the book-writer skill.
Source material: [optional GitHub URL]
Chapters: 12
Target: ~70,000 words
```

The agent will set up the repo, spawn parallel research/writing/review agents, and deliver a polished manuscript.

## What You Get

| Output | Description |
|--------|-------------|
| `book/final-manuscript.md` | Polished manuscript with TOC, title page, metadata |
| `book/metadata.json` | Title, author, word count, chapter count, date |
| `book/book.html` | HTML export (optional) |
| `chapters/*.md` | Individual chapter files |
| `research/*.md` | Research findings and pattern synthesis |
| `reviews/*.md` | Quality review results |

## Agent Roles

| Role | Model | Task |
|------|-------|------|
| Director | claude-sonnet-4-6 | Planning, coordination, quality gates |
| Research | gemini-2.5-pro | Source analysis, pattern identification |
| Writing | claude-sonnet-4-6 | 3 chapters per agent, 6-8K words each |
| Review | deepseek-v3.2 | Quality check, issue identification |
| Integration | claude-sonnet-4-6 | Merge chapters, fix cross-references |

## Cost Estimates

| Book Size | Cost | Time (parallel) |
|-----------|------|-----------------|
| 5 chapters, ~30K words | $5-15 | 2-4 hours |
| 10 chapters, ~60K words | $15-35 | 4-8 hours |
| 14 chapters, ~88K words | $30-60 | 6-12 hours |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/merge_chapters.py` | Merge chapter files into `book/manuscript.md` |
| `scripts/polish_manuscript.py` | Add title page, TOC, copyright, metadata |
| `scripts/convert_to_html.py` | Convert to HTML (pandoc or markdown2) |

## Templates

The `templates/` directory contains starter files for new book projects:

- `SYSTEM.md` — State machine, agent roles, safety rules, chapter tracker
- `AGENDA.md` — Sprint plan with phase-by-phase task lists
- `WORKLOG.md` — Append-only execution log for agent coordination

## Quality Scorecard

| Category | Score | Details |
|----------|-------|---------|
| Completeness (SQ-A) | 8/8 | All checks pass |
| Clarity (SQ-B) | 5/5 | End-to-end example, clear agent tasks |
| Balance (SQ-C) | 5/5 | Director + parallel workers, scripts for deterministic |
| Integration (SQ-D) | 5/5 | Standard Markdown/HTML output |
| Scope (SCOPE) | 3/3 | Clean boundaries |
| OPSEC | 2/2 | No violations |
| References (REF) | 3/3 | Reference implementation cited |
| Architecture (ARCH) | 2/2 | Multi-agent with clear roles |
| **Total** | **33/33** | |

*Scored by skill-engineer Reviewer (iteration 1)*

## Limitations

- Optimized for technical/non-fiction; fiction writing needs different frameworks
- Output is Markdown + HTML; no direct ebook/PDF generation
- Requires multiple sub-agent spawns; budget accordingly
- WORKLOG protocol depends on agents following instructions (LLM compliance varies)
- Very large books (>150K words) may need manual phase management

## Reference Implementation

[openclaw-paradigm-book](https://github.com/chunhualiao/openclaw-paradigm-book) — complete real-world example with all project notes, task files, and scripts included.

## Related

- [OpenClaw docs](https://docs.openclaw.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)
