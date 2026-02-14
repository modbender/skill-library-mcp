# skill-library-mcp

MCP server that indexes and serves Claude Code skills on demand.

## Architecture

- `src/skill-index.ts` — Builds search index from `skills/` directory by parsing YAML frontmatter from SKILL.md files
- `src/search.ts` — Token-based search with scoring (exact match +1, substring +0.5, name bonus +0.5, description bonus +0.3)
- `src/loader.ts` — Loads skill content with optional resource file inclusion
- `src/server.ts` — MCP server exposing `search_skill` and `load_skill` tools
- `src/index.ts` — Entry point: builds index, starts stdio transport
- `src/types.ts` — TypeScript interfaces (SkillFrontmatter, SkillEntry, SearchResult)

## Key Files

- `skills/` — Committed skill library shipped with the package (~708 skills)
- `test/fixtures/` — Test skills (do not use real skills/ dir in tests)

## Development

```bash
pnpm install          # Install dependencies
pnpm test             # Run tests
pnpm build            # Build to dist/
pnpm dev              # Run server locally via tsx
make ci               # Run test + build
make mcp-test         # Build and send initialize request
```

## Testing

Two test layers:

**Unit tests** (`test/fixtures/`): Synthetic skills for deterministic, fast testing.
- `test/skill-index.test.ts` — Index building, frontmatter parsing
- `test/search.test.ts` — Search scoring, ranking, limits
- `test/loader.test.ts` — Content loading, resource inclusion
- `test/server.test.ts` — MCP server tools via in-memory transport

**Integration tests** (`skills/`): Real skill library for end-to-end validation.
- `test/integration.test.ts` — Index completeness, search relevance, resource loading

## CI/CD

- **CI** (`.github/workflows/ci.yml`): Runs on push/PR to main. test → build → ci-summary.
- **Release** (`.github/workflows/release.yml`): Runs on `v*` tags. test → build → publish (npm OIDC) + GitHub Release.

## Conventions

- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
- ESM-only (`"type": "module"`)
- Node 22 target
- pnpm package manager
