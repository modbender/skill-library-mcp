# Error Handling Traps

- Unhandled rejection crashes Node 15+ — always `.catch()` or try/catch with await
- Callback errors don't throw — must check `if (err)` in callback, try/catch useless
- `process.on('uncaughtException')` — log and EXIT, don't try to continue
- `process.on('unhandledRejection')` — same, log and exit gracefully
- Throwing non-Error — loses stack trace, always `throw new Error()`
- `error` event on streams — unhandled crashes process, must attach handler
