# auto-doc-index

**Auto-generate document index tables from file frontmatter.**

AI agent skill that replaces hand-maintained `README.md` index tables with auto-generated ones derived from structured frontmatter in individual doc files. Eliminates merge conflicts, silent data drift, and stale indexes in multi-agent / multi-contributor documentation workflows.

## The Problem

Hand-maintained index tables in `README.md` are **shared mutable state**. In a real project with 13 ADR files, we measured an **62% error rate** in the hand-maintained index — titles truncated, statuses fabricated, dates invented. Nobody noticed because the index *looked* correct.

## The Solution

Each document is self-describing via frontmatter. A zero-dependency generator script scans the directory, parses frontmatter, and injects a fresh index table between `<!-- INDEX:START -->` / `<!-- INDEX:END -->` markers. The index becomes a **derived view** — a stateless pure function of the source files.

```
OLD: Write doc → Hand-edit README.md → Merge conflict risk
NEW: Write doc → Run generator → Idempotent rebuild, zero conflicts
```

## Quick Start

1. **Install as a Cursor skill:**
   ```bash
   skillkit install zjlpaul/auto-doc-index
   ```

2. **Or install via ClawHub:**
   ```bash
   openclaw install auto-doc-index
   ```

3. **Or just copy the template script:**
   Copy `template/generate-doc-index.ts` to your project's `scripts/` directory and run:
   ```bash
   npx tsx scripts/generate-doc-index.ts all
   ```

## Supported Formats

| Format | Agent |
|--------|-------|
| SKILL.md | Claude Code, Codex, Gemini CLI, 30+ agents |
| Cursor MDC | Cursor |
| Markdown Rules | Windsurf, GitHub Copilot |

Use [SkillKit](https://github.com/nicholasbarger/skillkit) to translate between formats:
```bash
skillkit translate --to cursor SKILL.md
skillkit translate --to windsurf SKILL.md
```

## Frontmatter Patterns

**ADR/RFC style (inline metadata):**
```markdown
# ADR-001: Title Here
Status: Decided
Date: 2026-01-28
```

**Pitfall/Postmortem style (bold fields):**
```markdown
# PIT-001: Title Here
**Area:** engine
**Severity:** high
**Status:** resolved
```

## License

MIT
