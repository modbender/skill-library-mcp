# Security Traps

- `process.env` values are strings — `PORT=3000` is `"3000"`, parseInt needed
- Missing env var is `undefined` — no error, check explicitly on startup
- `eval()` with user input — remote code execution
- `exec(userInput)` — command injection, use `execFile` with args array
- Path traversal — `../../../etc/passwd`, validate with `path.resolve` + prefix check
- Prototype pollution — `obj[userKey] = val` can modify `__proto__`
- `npm audit` regularly — dependencies have vulnerabilities
- Never log secrets — sanitize before logging, check for tokens/passwords
