# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MCP server that indexes and serves Claude Code skills on demand. It exposes two tools (`search_skill`, `load_skill`) over stdio transport using the Model Context Protocol SDK.

## Commands

```bash
pnpm install          # Install dependencies
pnpm test             # Run all tests (vitest)
pnpm test -- test/search.test.ts              # Run a single test file
pnpm test -- -t "exact token match"           # Run a single test by name
pnpm build            # Build to dist/ (tsup, ESM-only, node22 target)
pnpm dev              # Run server locally via tsx
make ci               # Run test + build
make mcp-test         # Build and send initialize request to verify MCP handshake
```

## Architecture

The data flow is: `skills/` → `buildIndex()` → `SkillEntry[]` → `createServer()` → MCP tools over stdio.

- `src/skill-index.ts` — Reads `skills/*/SKILL.md`, parses YAML frontmatter, builds tokenized search index as `SkillEntry[]`
- `src/search.ts` — Token-based search: exact match +1, substring +0.5, name bonus +0.5, description bonus +0.3, normalized by query token count, threshold ≥0.2
- `src/loader.ts` — Loads full SKILL.md content; optionally appends `resources/*.md` files
- `src/server.ts` — Creates `McpServer` with two tools. Builds a case-insensitive lookup map keyed by both `dirName` and `frontmatter.name`. `load_skill` falls back to fuzzy search suggestions when exact lookup fails
- `src/index.ts` — Entry point: resolves `skills/` dir relative to `dist/`, builds index, connects stdio transport
- `src/types.ts` — `SkillFrontmatter`, `SkillEntry`, `SearchResult` interfaces

## Testing

Two test layers, both using vitest:

**Unit tests** use synthetic skills in `test/fixtures/` for deterministic results. Never use the real `skills/` directory in unit tests.

**Integration tests** (`test/integration.test.ts`) use the real `skills/` directory to validate index completeness and search relevance.

## Conventions

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
- ESM-only (`"type": "module"`) — all internal imports use `.js` extensions
- Node 22 target, pnpm package manager
- tsup bundles `src/index.ts` to `dist/index.js` with `#!/usr/bin/env node` banner
- `skills/` lives at project root, resolved at runtime as `join(__dirname, "..", "skills")` from `dist/`
