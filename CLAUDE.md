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
pnpm dedup            # Check for duplicate skills
tsx scripts/import-skills.ts <source-dir> [--no-dry-run]  # Import skills from external source
```

## Architecture

The data flow is: `skills/` → `buildIndex()` → `SearchIndex` → `createServer()` → MCP tools over stdio.

- `src/skill-index.ts` — Reads `skills/*/SKILL.md`, parses YAML frontmatter, builds tokenized search index with IDF scores as `SearchIndex`
- `src/search.ts` — IDF-weighted search with stop-word filtering, query deduplication, minimum substring length (≥2 chars), name bonus +2.0, description bonus +1.0, threshold ≥0.5. Normalizes by matched token count (not total query tokens) to prevent unmatched terms from diluting scores
- `src/loader.ts` — Loads full SKILL.md content; optionally appends `resources/*.md` files
- `src/server.ts` — Creates `McpServer` with two tools. Builds a case-insensitive lookup map keyed by both `dirName` and `frontmatter.name`. `load_skill` falls back to fuzzy search suggestions when exact lookup fails
- `src/index.ts` — Entry point: resolves `skills/` dir relative to `dist/`, builds index, connects stdio transport
- `src/types.ts` — `SkillFrontmatter`, `SkillEntry`, `SearchIndex`, `SearchResult` interfaces
- `src/dedup.ts` — Deduplication utility: finds exact (hash-based) and near (Jaccard similarity >0.8) duplicate skills. Runnable as CLI
- `scripts/import-skills.ts` — Imports skills from external directories with dry-run support and dedup checking

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

## Releases

Releases are fully automated via [release-please](https://github.com/googleapis/release-please). On every push to `main`, release-please analyzes conventional commits and opens/updates a Release PR with version bumps and changelog. Merging that PR creates a git tag and GitHub Release, which triggers npm publish.

**Commit → version mapping:**
- `fix: ...` → patch (1.0.0 → 1.0.1)
- `feat: ...` → minor (1.0.0 → 1.1.0)
- `feat!: ...` or `BREAKING CHANGE:` footer → major (1.0.0 → 2.0.0)
