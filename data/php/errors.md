# Error Traps

- `@` suppresses errors — hides problems, never use in production
- Exception vs Error — `\Error` is separate hierarchy, catch `\Throwable`
- `set_error_handler` — doesn't catch fatal errors
- `try/finally` — finally runs even on return, but not on `exit()`
- Uncaught exception — fatal error, process dies
- `error_reporting(0)` — still logs to file if configured, not silent
- `trigger_error` for warnings — won't throw exception
