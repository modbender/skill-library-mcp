# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in guard-scanner itself, please report it responsibly:

1. **Do NOT open a public issue**
2. Email: automatic.bliss.records@gmail.com
3. Include: affected version, steps to reproduce, potential impact

We will respond within 48 hours and provide a fix within 7 days for critical issues.

## Scope

guard-scanner is a **static analysis tool** — it reads files but never executes them. It does not:
- Execute any code from scanned skills
- Make network requests
- Modify any files in the scan directory
- Require elevated privileges

The only files guard-scanner writes are output reports (`--json`, `--sarif`, `--html`) to the scan directory.

## Supply Chain Security

guard-scanner itself has **zero runtime dependencies**. This is a deliberate design choice:
- Nothing to audit
- No transitive dependency risks
- No `postinstall` scripts
- Pure Node.js stdlib

## Pattern Updates

The threat pattern database (`src/patterns.js`) and IoC database (`src/ioc-db.js`) are updated based on:
- Snyk ToxicSkills taxonomy
- OWASP MCP Top 10
- CVE reports affecting AI agents
- Community-reported incidents
- Original research from real-world attacks

## Responsible Disclosure

The test fixtures in `test/fixtures/malicious-skill/` contain **intentionally malicious patterns** for testing purposes. These files are:
- Clearly marked as test fixtures
- Non-functional (will error if executed)
- Necessary for validating detection capabilities
