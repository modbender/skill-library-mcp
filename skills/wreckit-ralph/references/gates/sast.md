# Gate: SAST (FIX + AUDIT modes)

**Question:** Did the fix introduce new vulnerabilities?

## Checks

Review the diff (not the whole codebase) for:
- SQL injection, XSS, command injection, path traversal
- Hardcoded secrets or credentials
- Missing input validation
- Missing error handling
- Auth/authz bypass
- Insecure defaults

## Pass/Fail

- **Pass:** Diff introduces zero new security concerns.
- **Fail:** Any new vulnerability in the diff.
