# Stream Traps

- `write()` returns false — buffer full, keep writing = memory bloat
- Must wait for `drain` event — before resuming writes after false
- `.pipe()` doesn't propagate errors — source error won't reach destination handler
- `pipeline()` over `.pipe()` — handles errors AND cleanup on all streams
- Missing error handler crashes — `stream.on('error', handler)` on EVERY stream
- `readable.destroy()` — call on error to prevent leaks, pipeline does this
