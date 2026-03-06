# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MCP server that indexes and serves Claude Code skills on demand. It exposes two tools (`search_skill`, `load_skill`) over stdio transport using the Model Context Protocol SDK.

## Commands

```bash
pnpm install          # Install dependencies
pnpm test             # Run unit tests (vitest)
pnpm test:integration # Run integration + dedup tests (slow, uses real data/)
pnpm test -- test/search.test.ts              # Run a single test file
pnpm test -- -t "exact token match"           # Run a single test by name
pnpm build            # Build to dist/ (tsup, ESM-only, node22 target)
pnpm dev              # Run server locally via tsx
make ci               # Run test + validate-skills + build
make mcp-test         # Build and send initialize request to verify MCP handshake
pnpm dedup            # Check for duplicate skills
pnpm validate-skills  # Validate data/ directory structure
pnpm clean-skills     # Remove invalid skill dirs (dry run by default, --no-dry-run to apply)
pnpm fix-skills       # Fix broken skills: missing frontmatter, broken YAML, dupes (dry run by default)
tsx scripts/import-skills.ts <source-dir> [--no-dry-run]  # Import skills from external source
```

## Architecture

The data flow is: `data/` → `buildIndex()` → `SearchIndex` → `createServer()` → MCP tools over stdio.

- `src/skill-index.ts` — Reads `data/*/SKILL.md`, parses YAML frontmatter, builds tokenized search index with IDF scores as `SearchIndex`
- `src/search.ts` — IDF-weighted search with stop-word filtering, query deduplication, minimum substring length (≥2 chars), name bonus +2.0, description bonus +1.0, threshold ≥0.5. Normalizes by matched token count (not total query tokens) to prevent unmatched terms from diluting scores
- `src/loader.ts` — Loads full SKILL.md content; optionally appends `resources/*.md` files
- `src/server.ts` — Creates `McpServer` with two tools. Builds a case-insensitive lookup map keyed by both `dirName` and `frontmatter.name`. `load_skill` falls back to fuzzy search suggestions when exact lookup fails
- `src/index.ts` — Entry point: resolves `data/` dir relative to `dist/`, builds index, connects stdio transport
- `src/types.ts` — `SkillFrontmatter`, `SkillEntry`, `SearchIndex`, `SearchResult` interfaces
- `src/dedup.ts` — Deduplication utility: finds exact (hash-based) and near (Jaccard similarity >0.8) duplicate skills. Runnable as CLI
- `scripts/import-skills.ts` — Imports skills from external directories (supports flat and nested `author/skill-name` layouts) with content-based dedup and dry-run support
- `scripts/validate-skills.ts` — Validates all skill dirs have `SKILL.md` with valid frontmatter (`name` + `description`) and detects exact duplicates (O(n) hash-based). Runs in CI
- `scripts/clean-skills.ts` — Removes skill dirs that lack `SKILL.md`. Dry run by default
- `scripts/fix-skills.ts` — Fixes broken skills: adds missing frontmatter, repairs broken YAML (unquoted colons, numeric names), fills missing descriptions, removes exact duplicates. Dry run by default

## Skill Data Directory

**IMPORTANT:** Skill data lives in `data/`, NOT `skills/`. The `skills/` directory name is reserved by Claude Code's plugin system for auto-discovered plugin skills. Using `data/` prevents the plugin from injecting 15K+ skills into context.

Each skill is a directory under `data/` containing at minimum a `SKILL.md` file with YAML frontmatter (`name` and `description` fields required).

**IMPORTANT:** Skills may contain ANY files alongside `SKILL.md` — scripts (`.py`, `.sh`), code (`.js`, `.ts`), templates, fonts, configs, etc. These files are referenced by `SKILL.md` and are part of the skill. **Never delete non-md files from skill directories.** The loader only serves `SKILL.md` and `resources/*.md` over MCP, but other files exist for the skill consumer to use locally.

```
data/
  my-skill/
    SKILL.md              # Required: frontmatter with name + description
    resources/            # Optional: extra .md files served by load_skill
      guide.md
    scripts/              # Optional: scripts referenced by SKILL.md
      setup.sh
    templates/            # Optional: any supporting files
      template.js
```

## Testing

Two test layers, both using vitest:

**Unit tests** (`pnpm test`) use synthetic skills in `test/fixtures/` for deterministic results. Never use the real `data/` directory in unit tests. These run in CI.

**Integration tests** (`pnpm test:integration`) use the real `data/` directory to validate index completeness, search relevance, and exact duplicate detection. These are slow with 15K+ skills and run on-demand, not in CI.

**Near-duplicate detection** (`pnpm dedup`) is O(n²) Jaccard similarity — too slow for CI with 15K+ skills. Run on-demand only.

## Conventions

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
- ESM-only (`"type": "module"`) — all internal imports use `.js` extensions
- Node 22 target, pnpm package manager
- tsup bundles `src/index.ts` to `dist/index.js` with `#!/usr/bin/env node` banner
- `data/` lives at project root, resolved at runtime as `join(__dirname, "..", "data")` from `dist/`

## Releases

Releases are fully automated via [release-please](https://github.com/googleapis/release-please). On every push to `main`, release-please analyzes conventional commits and opens/updates a Release PR with version bumps and changelog. Merging that PR creates a git tag and GitHub Release, which triggers npm publish.

**Commit → version mapping:**
- `fix: ...` → patch (1.0.0 → 1.0.1)
- `feat: ...` → minor (1.0.0 → 1.1.0)
- `feat!: ...` or `BREAKING CHANGE:` footer → major (1.0.0 → 2.0.0)