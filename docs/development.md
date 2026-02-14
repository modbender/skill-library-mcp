# Development Guide

## Setup

```bash
git clone <repo-url>
cd skill-library-mcp
pnpm install
```

Requirements: Node.js 22+, pnpm 9.15+

## Testing

Tests use synthetic fixtures in `test/fixtures/`, not the real `skills/` directory. This means tests work in CI without any skill data.

```bash
pnpm test              # Run all tests once
pnpm test:watch        # Run in watch mode
pnpm test:coverage     # Run with coverage report
```

Test files:
- `test/skill-index.test.ts` — Index building, frontmatter parsing, resource detection
- `test/search.test.ts` — Search scoring, ranking, limits, edge cases
- `test/loader.test.ts` — Content loading, resource inclusion, alphabetical ordering

## Build

```bash
pnpm build    # Produces dist/index.js via tsup
```

Build config is in `tsup.config.ts`:
- Entry: `src/index.ts`
- Format: ESM
- Target: Node 22
- Adds `#!/usr/bin/env node` shebang for CLI usage

## Local MCP Testing

Test the MCP server handshake:

```bash
make mcp-test
```

This builds the project and sends a JSON-RPC `initialize` request via stdin. You should see a valid JSON-RPC response with server capabilities.

For interactive testing:

```bash
pnpm dev
```

Then paste JSON-RPC messages to stdin.

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make test` | Run vitest |
| `make build` | Build with tsup |
| `make ci` | Run test + build |
| `make dev` | Run MCP server via tsx |
| `make clean` | Remove dist/, node_modules/, coverage/ |
| `make mcp-test` | Build and test MCP initialize handshake |

## Release Process

1. Bump version in `package.json`
2. Commit: `git commit -m "chore: release v1.x.x"`
3. Tag: `git tag v1.x.x`
4. Push: `git push && git push --tags`
5. GitHub Actions automatically: runs tests → builds → publishes to npm (OIDC) → creates GitHub Release with changelog

## Troubleshooting

**Tests fail with "module not found"**: Make sure you ran `pnpm install`. The project uses ESM with `.js` extensions in imports.

**`make mcp-test` shows no output**: The server writes logs to stderr. Make sure the build succeeded (`pnpm build`).

**pnpm version mismatch**: The project pins `pnpm@9.15.4` via `packageManager` in `package.json`. Use `corepack enable` to auto-install the correct version.
