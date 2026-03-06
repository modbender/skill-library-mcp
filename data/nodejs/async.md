# Async Traps

## Event Loop
- `setImmediate` runs after I/O — `process.nextTick` runs before (order matters)
- Long loops starve I/O — break with `setImmediate` every N iterations

## Promises
- `Promise.all()` fails fast — one rejection kills all, use `allSettled` for partial results
- Forgetting `await` — function continues without waiting, no error thrown
- `return await` redundant — except inside try/catch (needed to catch rejection)
- Sequential `await` in loop is slow — use `Promise.all(items.map(...))` for parallel

## Callbacks
- Callback errors don't propagate — try/catch won't catch them, handle in callback
- Zalgo: mixing sync/async — always be consistent, async callback even for cached values
