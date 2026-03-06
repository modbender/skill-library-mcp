# Node.js Migration Traps

## Required Changes

| Node | Deno | Notes |
|------|------|-------|
| `require()` | `import` | No CJS in Deno |
| `__dirname` | `import.meta.dirname` | Deno 1.40+ |
| `__filename` | `import.meta.filename` | Deno 1.40+ |
| `process.env.X` | `Deno.env.get("X")` | Different API |
| `fs.readFile` | `Deno.readTextFile` | Or use `node:fs` |
| `Buffer` | `Uint8Array` | Or import from `node:buffer` |

## node: Specifier

```typescript
// Node builtins require node: prefix
import { readFile } from "node:fs/promises";
import { Buffer } from "node:buffer";
import path from "node:path";
import { createServer } from "node:http";
```

- Without `node:` — import fails
- Not all Node APIs — some missing or different
- Different error types — catch logic may need update

## npm: Specifier

```typescript
// npm packages
import express from "npm:express@4.18.2";
import { PrismaClient } from "npm:@prisma/client";
```

- Native addons — generally don't work
- Pure JS packages — usually work
- TypeScript packages — may need `@types` separately
- Check each dependency — import success ≠ functions work

## package.json Support

```json
// deno.json
{
  "nodeModulesDir": true
}
```

- Creates `node_modules` for npm packages
- Some tools require this — bundlers, etc.
- Increases disk usage — tradeoff for compatibility

## Common Migration Failures

- `require()` anywhere — Deno doesn't support
- `module.exports` — only `export` works
- Extensionless imports — `.ts` required
- `process.on('SIGTERM')` — use `Deno.addSignalListener`
- `child_process.exec` — use `Deno.Command`
- `crypto` module — different API, use Web Crypto

## Step-by-Step Migration

1. **Replace require with import**
   ```typescript
   // Before
   const fs = require('fs');
   // After
   import fs from 'node:fs';
   ```

2. **Add file extensions**
   ```typescript
   // Before
   import { helper } from './utils/helper';
   // After
   import { helper } from './utils/helper.ts';
   ```

3. **Update Node globals**
   ```typescript
   // Before
   console.log(__dirname);
   // After
   console.log(import.meta.dirname);
   ```

4. **Replace process.env**
   ```typescript
   // Before
   const key = process.env.API_KEY;
   // After
   const key = Deno.env.get("API_KEY");
   ```

5. **Test npm dependencies**
   ```typescript
   // Add npm: prefix
   import express from "npm:express@4.18.2";
   // Test all used functions
   ```

## Compatibility Checklist

- [ ] All `require()` → `import`
- [ ] All imports have `.ts` extension
- [ ] `__dirname` → `import.meta.dirname`
- [ ] `process.env` → `Deno.env.get()`
- [ ] Node builtins have `node:` prefix
- [ ] npm packages have `npm:` prefix
- [ ] Test native addons — may not work
- [ ] Run full test suite
- [ ] Document required permissions
