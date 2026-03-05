# Security Notes

This skill is safe-by-design. Keep all generated outputs deterministic, inspectable, and offline-capable.

- Do not tell the user to run terminal commands.
- Do not ask for secrets, tokens, API keys, or local credentials.
- Do not load remote scripts, styles, fonts, images, or data at runtime.
- Do not embed tracking, analytics, telemetry, or hidden network calls.
- Do not use `eval`, `Function`, remote imports, or code injection patterns.
- Do not require bundlers, package managers, or build steps for the generated `index.html`.
- Keep the final deliverable to plain HTML, CSS, and vanilla JS in one file.
