# Bundler Traps

## Target Mismatches

- `--target=browser` strips Node APIs silently — build succeeds, runtime crashes
- `--target=node` includes browser shims — bundle larger than needed
- `--target=bun` — smallest bundle but only runs in Bun
- No target specified — defaults may not match deploy environment

## Tree-Shaking Failures

- `"sideEffects": false` missing — nothing tree-shaken
- `export *` — re-exports may not tree-shake properly
- Dynamic imports — can't be analyzed, always included
- Circular dependencies — may prevent proper shaking
- Imports for side effects only — removed if not detected

## Code Splitting

- `--splitting` requires `--format=esm` — error doesn't say this
- `--splitting` with CJS — silently does nothing
- Chunks named by hash — hard to debug which is which
- Shared chunks — may create more HTTP requests than expected

## External Packages

- Everything bundled by default — server bundles node_modules
- `--external:express` — express not bundled, must be installed
- `--external:*` — nothing bundled, useless for browsers
- Regex externals not supported — list each package explicitly
- Peer deps — should usually be external

## Source Maps

- `--sourcemap=external` — creates .map file, for production debugging
- `--sourcemap=inline` — embedded in bundle, larger but simpler
- Source maps reveal source code — don't deploy if code is sensitive
- Minified + source map — map file can be large

## CSS and Assets

- CSS imports work — but not identical to webpack
- `url()` paths — resolved relative to CSS file, may be wrong after bundling
- Fonts and images — need explicit handling or broken paths
- CSS modules — limited support, may not work as expected

## Common Flag Combinations

```bash
# Production web app
bun build ./src/index.ts --outdir=./dist --target=browser --minify --splitting --format=esm

# Server bundle (external node_modules)
bun build ./src/server.ts --outfile=./dist/server.js --target=node --external:*

# Development
bun build ./src/index.ts --outdir=./dist --sourcemap=external

# Library (nothing bundled)
bun build ./src/index.ts --outdir=./dist --format=esm --external:*
```

## Debugging Build Issues

```bash
# See what's included
bun build ./src/index.ts --outdir=./debug

# Check output size
ls -lh ./debug/

# Inspect chunks
cat ./debug/chunk-*.js | head -50
```
