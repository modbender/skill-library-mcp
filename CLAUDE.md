# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MCP server that indexes and serves Claude Code skills on demand. It exposes three tools (`search_skill`, `load_skill`, `list_categories`) over stdio transport using the Model Context Protocol SDK. Also ships as a Claude Code plugin (manifest in `.claude-plugin/`; `hooks/` must sit at the repo root, not inside `.claude-plugin/`, or Claude Code never loads it) with a SessionStart hook that tells the agent to search the library before each task.

## Commands

```bash
pnpm install          # Install dependencies
pnpm test             # Run unit tests (vitest)
pnpm test:integration # Run integration + dedup tests (slow, uses real data/)
pnpm test -- test/search.test.ts              # Run a single test file
pnpm test -- -t "exact token match"           # Run a single test by name
pnpm build            # sync-version → tsup → bundle-skills (see Build below)
pnpm dev              # Run server locally via tsx (filesystem mode, reads data/)
make ci               # Run test + validate-skills + build
make mcp-test         # Build and send initialize request to verify MCP handshake
pnpm dedup            # Check for duplicate skills
pnpm validate-skills  # Validate data/ directory structure
pnpm clean-skills     # Remove invalid skill dirs (dry run by default, --no-dry-run to apply)
pnpm fix-skills       # Fix broken skills: missing frontmatter, broken YAML, dupes (dry run by default)
tsx scripts/import-skills.ts <source-dir> [--no-dry-run]  # Import skills from external source
```

GitHub CI runs only `pnpm test` and `pnpm build`; `validate-skills` runs only via `make ci`.

## Architecture

Two runtime modes, chosen in `src/index.ts` at startup:

- **Bundle mode (npm package):** `dist/skills-index.json` exists → `buildIndexFromBundle()`. Full content lives in `dist/skills-content.json.gz`, gunzipped lazily on the first `load_skill` call and cached. The npm `files` array does **not** ship `data/`, so the bundle is the only content source for published installs (avoids thousands of files on Windows).
- **Filesystem mode (dev):** no bundle → `buildIndex(data/)` reads `data/*/SKILL.md` directly. `loadSkill()` prepends a `> **Skill directory**: <abs path>` header so the consumer can resolve `scripts/` etc.; `loadSkillFromBundle()` does not (there is no directory on disk).

Note `pnpm dev` after a `pnpm build` still uses filesystem mode, since tsx runs `src/index.ts` and resolves `skills-index.json` next to `src/`, not `dist/`.

Modules:

- `src/skill-index.ts` — `parseFrontmatter()` (full YAML via `yaml`; keeps `name`, `description`, `metadata`, `allowedTools`), `buildIndex()` and `buildIndexFromBundle()`. Both compute IDF scores and categories identically; keep them in sync when changing indexing.
- `src/tokenize.ts` — shared tokenizer: lowercase, strip non-`[a-z0-9-]`, hyphenated words also emit their parts.
- `src/search.ts` — IDF-weighted search with stop-word filtering, query deduplication, minimum substring length (≥2 chars), name bonus +2.0, description bonus +1.0, threshold ≥0.5. Normalizes by matched token count (not total query tokens) so unmatched terms don't dilute scores.
- `src/categories.ts` — `CATEGORY_KEYWORDS` table; each skill goes to the **first** category whose keyword is a substring of `dirName + description`, else `Other`. Order in the table matters.
- `src/loader.ts` — `loadSkill()` (disk) and `loadSkillFromBundle()`; with `include_resources`, appends `resources/*.md` sorted by filename.
- `src/server.ts` — registers the three tools. Case-insensitive lookup map keyed by both `dirName` and `frontmatter.name`; `load_skill` falls back to fuzzy search suggestions on a miss. Server version is read from `package.json`.
- `src/dedup.ts` — exact (hash) and near (Jaccard >0.8) duplicate finder. Runnable as CLI.
- `src/types.ts` — in-memory types (`SkillEntry`, `SearchIndex`) plus on-disk bundle shapes (`SkillsIndex`, `SkillsBundle`).

## Build

`pnpm build` runs three steps:

1. `scripts/sync-version.ts` — copies `package.json` version into `.claude-plugin/plugin.json` and `marketplace.json` (so a build can dirty those files).
2. `tsup` — bundles `src/index.ts` → `dist/index.js` (ESM, node22, `#!/usr/bin/env node` banner). `clean: true` wipes `dist/`, so the bundle step must run after it.
3. `scripts/bundle-skills.ts` — walks `data/` and writes `dist/skills-index.json` + `dist/skills-content.json.gz`.

Gotcha: `bundle-skills.ts` extracts frontmatter with single-line regexes, not the YAML parser, and does not write `metadata`/`allowedTools`. Multi-line YAML descriptions (`description: >`) and those fields therefore differ between bundle mode and filesystem mode.

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
```

## Testing

Two test layers, both using vitest:

**Unit tests** (`pnpm test`) use synthetic skills in `test/fixtures/` (and `test/fixtures-dedup/`) for deterministic results. Never use the real `data/` directory in unit tests. These run in CI.

**Integration tests** (`pnpm test:integration`) use the real `data/` directory to validate index completeness, search relevance, and exact duplicate detection. Slow with 15K+ skills; on-demand, not in CI.

**Near-duplicate detection** (`pnpm dedup`) is O(n²) Jaccard similarity — too slow for CI. Run on-demand only.

## Conventions

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
- ESM-only (`"type": "module"`) — all internal imports use `.js` extensions
- Node 22 target, pnpm package manager
- Log to stderr only (`console.error`, `[skill-library]` prefix); stdout is the MCP stdio channel.

## Releases

Releases are fully automated via [release-please](https://github.com/googleapis/release-please). On every push to `main`, release-please analyzes conventional commits and opens/updates a Release PR with version bumps and changelog. Merging that PR creates a git tag and GitHub Release, which triggers npm publish.

**Commit → version mapping:**
- `fix: ...` → patch (1.0.0 → 1.0.1)
- `feat: ...` → minor (1.0.0 → 1.1.0)
- `feat!: ...` or `BREAKING CHANGE:` footer → major (1.0.0 → 2.0.0)
