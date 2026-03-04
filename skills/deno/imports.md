# Import and Dependency Traps

## URL Import Risks

- Remote URL at runtime — network failure = app won't start
- URL changes content — no semver, same URL different code
- CDN goes down — deno.land, esm.sh, unpkg all have outages
- Typo in URL — no error until runtime import fails

## Lockfile

```bash
# Generate/update lockfile
deno cache --lock=deno.lock --lock-write main.ts

# Verify in CI (fails if deps changed)
deno cache --lock=deno.lock main.ts

# Production: offline mode
deno run --lock=deno.lock --cached-only main.ts
```

- No lockfile by default — must explicitly create
- Lockfile must be committed — or CI uses different versions
- `--cached-only` requires prior cache — run `deno cache` first

## Import Maps (deno.json)

```json
{
  "imports": {
    "std/": "https://deno.land/std@0.210.0/",
    "oak": "https://deno.land/x/oak@v12.6.1/mod.ts",
    "@/": "./src/"
  }
}
```

- Import map must be in `deno.json` — separate file ignored in Deno 2.x
- Trailing slash for prefixes — `"std/"` not `"std"`
- Version in URL — `std@0.210.0` not `std@latest`
- Relative paths — start with `./` or `../`

## npm Specifier

```typescript
// Import from npm
import express from "npm:express@4.18.2";
import { z } from "npm:zod@3.22.0";
```

- `npm:` prefix required — `import express from 'express'` fails
- Version recommended — `npm:express` uses latest, unstable
- Native addons — most don't work, check before using
- `node:` for builtins — `import fs from 'node:fs'`

## Versioning Traps

- `@^1.0.0` doesn't exist — use exact version in URL
- `@latest` — different every run, don't use
- `/mod.ts` convention — main entry, not `index.ts`
- `x/` namespace — third party, less stable than `std/`

## Vendoring (Recommended for Production)

```bash
# Download all dependencies locally
deno vendor main.ts --output=vendor

# Import map points to local vendor
# deno.json automatically updated
```

- Vendor directory committed — no network needed
- Import map updated — points to `./vendor/`
- Update manually — re-run `deno vendor` for updates

## Dependency Inspection

```bash
# See dependency tree
deno info main.ts

# Check for updates
deno outdated  # Deno 2.x

# Find duplicate deps
deno info --json main.ts | jq '.modules | group_by(.specifier)'
```

## Common Import Patterns

```typescript
// Standard library
import { assertEquals } from "https://deno.land/std@0.210.0/assert/mod.ts";

// Third party
import { Application } from "https://deno.land/x/oak@v12.6.1/mod.ts";

// npm package
import chalk from "npm:chalk@5.3.0";

// Node builtin
import { readFile } from "node:fs/promises";

// Local with alias
import { db } from "@/database.ts";
```
