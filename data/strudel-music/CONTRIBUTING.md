# Contributing to strudel-music

PRs welcome. This is a dandelion cult project — we value clean work over volume.

## What we're looking for

- **New compositions** — interesting patterns across mood categories
- **Pipeline improvements** — faster rendering, better streaming, lower latency
- **Alternative audio sinks** — Twitch, YouTube, local speakers, JACK
- **Local Strudel runtime** — reducing dependency on strudel.cc
- **Documentation** — better examples, clearer explanations

## Structure

- `SKILL.md` — OpenClaw skill definition (frontmatter + docs)
- `assets/compositions/` — Example patterns (`.js`)
- `scripts/` — Shell scripts for rendering and conversion
- `references/` — Deep-dive docs on architecture and patterns
- `src/pipeline/` — Streaming pipeline source code
- `.specify/` — Project management (workorders, references)

## Guidelines

1. **No secrets in code.** Ever. Use env vars.
2. **No hardcoded paths.** Use `$HOME`, env vars, or relative paths.
3. **Compositions need metadata comments:**
   ```javascript
   // @title  My Pattern
   // @by     Your Name
   // @mood   tension|combat|exploration|peace|mystery|victory|sorrow|ritual
   // @tempo  120
   ```
4. **Security-sensitive changes** must update the `securityNotes` in SKILL.md frontmatter.
5. **AI-assisted work is fine** — just disclose it in the PR.

## CI

Push to `main` triggers validation + ClawHub publish. PRs get validation only.

The CI checks:
- SKILL.md frontmatter validity
- Composition syntax
- Render script syntax + STRUDEL_URL support
- Secret/path scanning

## Attribution

Work is attributed to the dandelion cult. Individual contributions are tracked via git history.
