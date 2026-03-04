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

## Local Plugin Testing

To test the plugin locally without publishing:

```bash
pnpm build
claude plugin install --plugin-dir .
```

This installs the plugin from the current directory. Verify the MCP tools are available by starting Claude Code and checking for `search_skill`, `load_skill`, and `list_categories`.

To uninstall:

```bash
claude plugin remove skill-library
```

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

Releases are automated via [release-please](https://github.com/googleapis/release-please). On every push to `main`, release-please analyzes conventional commits and opens/updates a Release PR with version bumps and changelog. Merging that PR creates a git tag and GitHub Release, which triggers npm publish.

When bumping the version, also update `version` in `.claude-plugin/plugin.json` to match.

## Troubleshooting

**Tests fail with "module not found"**: Make sure you ran `pnpm install`. The project uses ESM with `.js` extensions in imports.

**`make mcp-test` shows no output**: The server writes logs to stderr. Make sure the build succeeded (`pnpm build`).

**pnpm version mismatch**: The project pins `pnpm@9.15.4` via `packageManager` in `package.json`. Use `corepack enable` to auto-install the correct version.
