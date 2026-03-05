# Module Traps

## CommonJS
- `exports = x` breaks — must use `module.exports = x` (exports is just reference)
- `require()` cached — same object returned, mutations visible everywhere
- Circular deps return incomplete export — whatever was assigned at require time

## ESM
- No `__dirname` — use `fileURLToPath(import.meta.url)` + `dirname()`
- Can't `require()` ESM from CJS — must use dynamic `import()` which returns Promise
- `import` is hoisted — runs before other code, can't conditionally import

## Interop
- ESM importing CJS — only default import works, no named exports
- `"type": "module"` affects all `.js` — use `.cjs` extension for CommonJS files
