# Gate: AI Slop Scan

**Question:** Is this real code or confident-sounding garbage?

## Checks

- **Hallucinated dependencies** — imports/requires for packages that don't exist in any registry
- **Phantom imports** — importing from modules that don't exist in the project
- **Placeholder code** — `TODO`, `FIXME`, `implement this`, `pass`, `...`, empty function bodies
- **Template artifacts** — lorem ipsum, example.com URLs, hardcoded test credentials, `YOUR_API_KEY_HERE`
- **Dead code** — functions defined but never called, unreachable branches
- **Confident nonsense** — syntactically valid code that does nothing meaningful (e.g., try/catch that catches and ignores)

## Scripts

Run `scripts/check-deps.sh` for deterministic dependency verification against registries.

## Pass/Fail

- **Pass:** Zero hallucinated deps, zero phantom imports, no placeholder code in production paths.
- **Fail:** Any hallucinated dependency is an automatic fail. Placeholders in production code = fail.

**Severity:** Hallucinated deps = BLOCKER (stop everything). Placeholders = FAIL. Dead code = WARN.
