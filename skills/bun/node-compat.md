# Node.js Compatibility Traps

## APIs That Exist But Differ

- `process.nextTick` — different timing, code that depends on order breaks
- `fs.watch` — different backend, misses events Node catches
- `child_process` — subset of options, some stdio configs ignored
- `http.Server` — mostly compatible but edge cases in keep-alive handling
- `net.Socket` — some events fire in different order
- `stream` — Bun streams not 100% compatible with Node streams

## Missing/Partial APIs

- `cluster` — not implemented, immediate crash if used
- `vm` — partial, sandboxing may not work as expected
- `inspector` — different debugging protocol, some tools incompatible
- `worker_threads` — supported but `SharedArrayBuffer` has limitations
- `async_hooks` — partial, APM tools (DataDog, NewRelic) may not work
- `tls.createSecureContext` — some options silently ignored

## ESM vs CJS Traps

- `__dirname` / `__filename` — don't exist in ESM, use `import.meta.dir/file`
- `require()` in ESM — works in Bun but not standard, code not portable
- `module.exports` — works but mixing with ESM export causes issues
- `.mjs` files — treated as ESM, can't use require
- `"type": "module"` — affects all .js files, may break dependencies

## Native Addon Traps

- Most pure JS addons work — native addons are hit or miss
- `node-gyp` builds — may need rebuild with Bun, or fail entirely
- `better-sqlite3` — works, `sharp` — needs specific version
- N-API addons — better compatibility than node-gyp
- Test each native dep — import success ≠ all functions work

## Runtime Detection

```javascript
// Check runtime before Node-specific code
const isBun = typeof Bun !== 'undefined';
const isNode = typeof process !== 'undefined' && !isBun;

if (isBun) {
  // Bun-specific path
} else {
  // Node fallback
}
```

## Migration Checklist

- [ ] List all native dependencies — test each explicitly
- [ ] Search for `cluster` usage — must refactor
- [ ] Search for `vm` sandboxing — verify security still holds
- [ ] Test `fs.watch` code — add polling fallback
- [ ] Replace `__dirname` with `import.meta.dir`
- [ ] Run full test suite — timing-dependent tests may fail
