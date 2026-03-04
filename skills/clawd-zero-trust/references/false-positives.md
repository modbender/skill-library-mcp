# Known Audit False Positives

Verified by: Sonnet 4.6 source code review, Feb 20 2026

## How Filtering Works

The following patterns are passed to `grep -v` in `audit.sh` to suppress known false positive lines from `openclaw security audit --deep` output. Each entry documents the **exact pattern string** being filtered, the alert type it suppresses, and the verification rationale.

---

## Pattern 1: `openclaw-agentsandbox`

**Exact grep -v pattern:** `openclaw-agentsandbox`

**Suppressed alert types:**
- `[env-harvesting]` Credential harvesting patterns

**Flagged files:** `dist/index.js:39`, `dist/tools.js:9`

**Verdict:** ✅ FALSE POSITIVE

**Reason:** Reads `env.OPENCLAW_AGENT_DIR` to locate existing auth tokens, then contacts `api.agentsandbox.co` to generate an API key if none exists. This is standard OAuth key generation — not exfiltration. No data sent except a key creation request.

**Verification:** Confirmed via source code review — the only outbound call is a POST to `api.agentsandbox.co/v1/keys` with no user data payload.

---

## Pattern 2: `secureclaw`

**Exact grep -v pattern:** `secureclaw`

**Suppressed alert types:**
- `[dangerous-exec]` Shell execution
- `[dynamic-code-execution]` Dynamic evaluation
- `[env-harvesting]` Environment variable access

**Flagged files:** `dist/index.js`, `dist/auditor.js`, `dist/monitors/skill-scanner.js`, `dist/utils/crypto.js`

**Verdict:** ✅ FALSE POSITIVE

**Reason:** SecureClaw IS a security auditing plugin. It runs bash scripts to check system integrity, uses dynamic code scanning to detect vulnerabilities in OTHER plugins, and uses `execSync` to run audit scripts. All detected patterns are the auditing engine doing its job.

**Verification:** Confirmed via source code review — all exec calls are local audit commands (e.g., `ss -ltnp`, `ufw status`, `find ~/.openclaw`). No external data exfiltration.

---

## Rule for Future Audits

Before flagging any plugin as critical:
1. Read the flagged source file at the specific lines mentioned
2. Check if the behavior is functional (OAuth, auditing, monitoring)
3. Verify no external data exfiltration to non-approved endpoints
4. Only escalate if code sends sensitive data outside the approved provider list

**Recommended:** Use Sonnet 4.6 or Opus 4.6 for security verdicts. Avoid low-tier heuristics for final decisions.

---

## Adding New False Positives

When a new false positive is identified, add an entry with:
- `**Exact grep -v pattern:**` — the literal string passed to `grep -v`
- Suppressed alert types
- Flagged files and line numbers
- Verdict + reasoning
- Verification method (source code review, network trace, etc.)
