# Security Hardening Task

Harden `scripts/mandate-ledger.sh` against the security concerns flagged by ClawHub's automated scanner. The goal is to get reclassified from "suspicious" to "safe."

## Scanner's concerns:
1. Shell injection via user-controlled input
2. Path traversal vulnerabilities
3. Dynamic command construction risks
4. Complexity of bash handling authorization logic

## What to do:
1. **Quote ALL variable expansions** — every `$var` should be `"$var"` unless there's a specific reason not to
2. **Sanitize all user inputs** — add input validation functions that reject dangerous characters (semicolons, backticks, $(), pipes, etc.) in action names, resource paths, agent IDs, etc.
3. **Prevent path traversal** — validate that file paths don't contain `..` or absolute paths where relative are expected
4. **Use `--` with commands** where applicable to prevent option injection
5. **Replace any `eval` usage** with safer alternatives
6. **Add `set -euo pipefail`** at the top if not already there
7. **Ensure all temp files use mktemp** with restrictive permissions
8. **Validate JSON inputs** before processing with jq
9. **Keep all existing functionality intact** — this is a hardening pass, not a rewrite

## Constraints:
- Do NOT change the command interface or output format
- Do NOT remove any features
- All existing tests/smoke tests must still pass
- Keep it bash — don't rewrite in Python
- The script should still work with `bash -n` (syntax check)

## When done:
- Run `bash -n scripts/mandate-ledger.sh` to verify syntax
- Run a quick smoke test: `./scripts/mandate-ledger.sh init && ./scripts/mandate-ledger.sh create-quick "test" "allow browsing for 1 hour" && ./scripts/mandate-ledger.sh check '{"action":"browsing","resource":"google.com"}' && ./scripts/mandate-ledger.sh kill "test" && ./scripts/mandate-ledger.sh unlock`
