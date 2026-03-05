# ecap-security-auditor — QA Test Report

**Date:** 2026-02-02  
**Tester:** QA Subagent (Claude)  
**Perspective:** AI Agent using the skill for the first time  

---

## Test 1: Automatic Security Gate — Known Package (mcp-fetch)

**Result: ⚠️ PARTIAL PASS**

### Steps Performed
1. `curl -s "https://skillaudit-api.vercel.app/api/findings?package=mcp-fetch"` → `{"findings": [], "total": 0}`
2. No report exists for "mcp-fetch" despite SKILL.md suggesting it was audited.

### Observations
- The SKILL.md says to query `/api/findings?package=PACKAGE_NAME`, but the findings for MCP servers are stored under different slugs (e.g., `mcp-server-fetch` not `mcp-fetch`). 
- **An agent wouldn't know the correct slug.** There's no discovery/search endpoint to find the right name.
- The Gate Flow diagram says "Report exists? No → Go to AUTO-AUDIT" — but there's no actual Trust Score returned from `/api/findings`. The response only contains individual findings, no aggregate score.
- **Critical gap: The SKILL.md describes evaluating a "Trust Score" but the API never returns one.** The findings endpoint returns individual findings; the reports endpoint (for upload) accepts a `risk_score`. There's no `GET` endpoint that returns a trust score for a package.

### Decision Table Application
- Since findings=0 for mcp-fetch, an agent would interpret this as "No report exists" and trigger auto-audit — even though `mcp-server-fetch` HAS been audited with 3 findings.

### Issues Found
1. **🔴 BUG: No Trust Score endpoint** — The Decision Table references scores (≥70, 40-69, <40) but no API endpoint returns a trust score for a package. The agent has no way to get the number.
2. **🟡 Package naming ambiguity** — No search/fuzzy-match. Agent must guess the exact slug.
3. **🟡 Missing: How to derive Trust Score from findings** — Should the agent calculate it? From what formula?

---

## Test 2: Automatic Security Gate — Unknown Package

**Result: ⚠️ PARTIAL PASS**

### Steps Performed
1. `curl -s "https://skillaudit-api.vercel.app/api/findings?package=totally-unknown-package-xyz"` → `{"findings": [], "total": 0}`

### Observations
- The response for an unknown package is **identical** to a known package with no findings (both return `total: 0`).
- An agent can't distinguish "never audited" from "audited and clean".
- The SKILL.md says to trigger AUTO-AUDIT, which is well-described in Step 4, but:
  - Step 4 says "Read ALL files in the package directory" — but doesn't explain how to locate the package directory for npm/pip packages.
  - For npm: `node_modules/<name>/`? For pip: `site-packages/<name>/`? Not mentioned.
  
### Issues Found
1. **🟡 Can't distinguish "unaudited" from "clean"** — API returns same response for both.
2. **🟡 Auto-audit: package location not documented** — How does the agent find the files to audit for npm/pip packages?
3. **🟢 Auto-audit prompt is thorough** — `prompts/audit-prompt.md` is excellent and comprehensive.

---

## Test 3: Hash Verification

**Result: ✅ PASS**

### Steps Performed
1. `bash scripts/verify.sh` → All 6 files verified, integrity OK.
2. Tested `/api/integrity?package=totally-unknown-package-xyz` → Returns `{"error": "Unknown package", "known_packages": ["ecap-security-auditor"]}`.

### Observations
- verify.sh works perfectly on the happy path.
- Error handling for unknown packages is clear (returns error + known packages list).
- Script is well-written: detects sha256sum/shasum, handles missing files, clear output.
- **Limitation:** verify.sh is hardcoded to `PACKAGE="ecap-security-auditor"` — it can only verify itself. The SKILL.md Gate Flow says `bash scripts/verify.sh <package>` with an argument, but the script ignores arguments for the package name.

### Issues Found
1. **🔴 BUG: verify.sh ignores package argument** — Script hardcodes `PACKAGE="ecap-security-auditor"`. The SKILL.md documents usage as `bash scripts/verify.sh <package>` but the script only accepts an API URL override as `$1`, not a package name. The Gate Flow is broken for any package other than ecap-security-auditor itself.
2. **🟢 Good:** Integrity API only knows ecap-security-auditor currently, but the script should still accept the parameter for future use.

---

## Test 4: Manual Audit Flow

**Result: ⚠️ PARTIAL PASS**

### Steps Performed
1. Read `prompts/audit-prompt.md` — comprehensive and well-structured.
2. Created test report in documented JSON format.
3. Upload with `bash scripts/upload.sh /tmp/test-report.json` → **FAILED (HTTP 400)**.

### Upload Bug Details
The SKILL.md documents this JSON format:
```json
{
  "package_name": "example-package",
  "findings": [...],
  "summary": { "risk_score": 75, "recommendation": "safe" }
}
```

But the API actually requires:
```json
{
  "skill_slug": "example-package",   // NOT package_name
  "risk_score": 75,                  // top-level, NOT in summary
  "result": "safe",                  // NOT recommendation
  "findings_count": 1,              // required, not documented
  "findings": [...]
}
```

**The documented format does NOT work.** The API error message reveals the real fields: `skill_slug (or package_name), risk_score, result, findings_count are required`.

After fixing to use `skill_slug` + top-level `risk_score` + `result` + `findings_count`, upload succeeded (Report ID: 35, Finding: ECAP-2026-0818).

### Issues Found
1. **🔴 BUG: Documented JSON format doesn't match API** — `package_name` works (API accepts it as alias), but `risk_score` and `result` must be top-level, not nested in `summary`. `findings_count` is required but not documented at all.
2. **🟡 upload.sh doesn't validate or transform** — The script just passes JSON through. It could map the documented format to what the API expects.
3. **🟢 audit-prompt.md is excellent** — Clear checklist, good false-positive guidance, severity definitions are practical.

---

## Test 5: Registration Flow

**Result: ✅ PASS**

### Observations (code review only, not executed)
- Script is well-written with input validation (regex for agent name).
- Checks for existing credentials before re-registering.
- Uses `jq` to safely build JSON payload (prevents injection).
- Sets `chmod 600` on credentials file.
- Clear error messages.
- Documentation in SKILL.md is adequate.

### Issues Found
- None significant. Registration flow is solid.

---

## Test 6: API Endpoints

### GET /api/health — ✅ PASS
Returns: `{"status":"healthy","timestamp":"...","db":{"connected":true,"findings":46,"skills":13,"agents":5}}`  
Matches expected behavior. Quick and informative.

### GET /api/stats — ✅ PASS
Returns: `{"total_findings":"46","critical_findings":"2","skills_audited":"29","reporters":"1","total_reports":"34"}`  
**Minor:** Values are strings (e.g., `"46"` not `46`). Inconsistent typing but functional.

### GET /api/leaderboard — ✅ PASS
Returns array of agents with points, finding counts, timestamps. Works as documented.

### GET /api/findings?package=mcp-fetch — ⚠️ ISSUE
Returns empty results. The package was audited as `mcp-server-fetch`, not `mcp-fetch`. No fuzzy matching or suggestions. See Test 1 notes.

### GET /api/findings?package=coding-agent — ✅ PASS
Returns 6 findings with full details (ecap_id, severity, title, description, file, line, etc.). Data structure is rich and useful.

### GET /api/integrity?package=ecap-security-auditor — ✅ PASS
Returns SHA-256 hashes for 6 files, repo URL, commit hash, verification timestamp. Well-structured.

### GET /api/integrity?package=totally-unknown-package-xyz — ✅ PASS (graceful error)
Returns: `{"error":"Unknown package","known_packages":["ecap-security-auditor"]}`. Helpful error.

### GET /api/agents/ecap — ⚠️ ISSUE
Returns: `{"error":"Agent not found"}`.  
The SKILL.md uses `/api/agents/:name` but the registered agent is `ecap0`, not `ecap`. The docs don't clarify that the exact registered name must be used.

### GET /api/agents/ecap0 — ✅ PASS
Returns comprehensive agent profile with stats, severity breakdown, skills audited list, recent findings and reports. Excellent detail.

### Issues Found
1. **🟡 /api/stats returns strings instead of numbers** — Minor inconsistency.
2. **🟡 No package search/discovery endpoint** — Can't find the right slug for a package.
3. **🟡 /api/findings doesn't return a Trust Score** — Only raw findings. Agent must calculate score somehow.

---

## Test 7: Peer Review Flow

**Result: ⚠️ PARTIAL PASS**

### Observations
- `prompts/review-prompt.md` is well-written with clear verdict definitions, good/bad examples.
- The review checklist is practical and thorough.
- API endpoint for submitting reviews is documented: `POST /api/findings/:id/review`.

### Issues Found
1. **🟡 Finding ID format unclear** — The findings response returns `ecap_id` (e.g., "ECAP-2026-0777") and a numeric `id`. Which one goes in the URL path? SKILL.md uses "FINDING_ID" without clarifying. (Likely the numeric ID, but not stated.)
2. **🟡 No way to list packages with findings** — To do peer review, you need to know which packages have findings. No endpoint lists audited packages or packages needing review.
3. **🟢 Review prompt quality is high** — Good examples of reasoning, clear verdict criteria.

---

## Test 8: Gesamtbewertung

### Summary Table

| Test | Result | Critical Issues |
|------|--------|-----------------|
| 1: Known Package Gate | ⚠️ PARTIAL | No Trust Score endpoint; package slug ambiguity |
| 2: Unknown Package Gate | ⚠️ PARTIAL | Can't distinguish unaudited from clean; missing package location guidance |
| 3: Hash Verification | ✅ PASS (with bug) | verify.sh hardcoded to self only |
| 4: Manual Audit | ⚠️ PARTIAL | JSON format mismatch between docs and API |
| 5: Registration | ✅ PASS | — |
| 6: API Endpoints | ✅ PASS (mostly) | Stats type inconsistency; no search endpoint |
| 7: Peer Review | ⚠️ PARTIAL | Finding ID format unclear; no discovery |
| 8: Overall | — | See below |

### 🔴 Critical Bugs

1. **Report JSON format mismatch** — The documented format in SKILL.md does NOT work with the API. Fields `risk_score`, `result` must be top-level; `findings_count` is required but undocumented. An agent following the docs will get HTTP 400 on every upload.

2. **verify.sh can only verify itself** — The script hardcodes `PACKAGE="ecap-security-auditor"` and ignores the package argument. The SKILL.md Gate Flow references `bash scripts/verify.sh <package>` which doesn't work.

3. **No Trust Score endpoint** — The entire Decision Table (Score ≥70/40-69/<40) references a Trust Score that no API endpoint provides. The Gate Flow is unimplementable as documented.

### 🟡 Medium Issues

4. Package slug discovery — No search or fuzzy matching. Agents must guess exact slugs.
5. Can't distinguish "unaudited" vs "clean" from API response.
6. Auto-audit doesn't explain how to locate package files for npm/pip.
7. Finding ID format (numeric vs ECAP-XXXX) not clarified for review endpoint.
8. No endpoint to list packages needing review.

### 🟢 Strengths

- **audit-prompt.md is excellent** — Comprehensive, clear false-positive guidance, good severity definitions.
- **review-prompt.md is well-crafted** — Good examples, practical checklist.
- **Scripts are well-written** — Good error handling, dependency checks, security practices (chmod 600, jq for JSON building).
- **API is functional and responsive** — Fast responses, good error messages.
- **Leaderboard/points system is motivating** — Gamification done right.
- **Overall concept is strong** — Collaborative security auditing by AI agents is innovative.

### Verbesserungsvorschläge

1. **Fix the JSON format documentation** — Either update SKILL.md to show the actual API format, or update upload.sh to transform the documented format to what the API expects.
2. **Add a Trust Score endpoint** — `GET /api/trust-score?package=X` returning `{"package": "X", "trust_score": 75, "findings_summary": {...}}`.
3. **Make verify.sh accept package argument** — Change `PACKAGE="${1:-ecap-security-auditor}"` or add a second positional parameter.
4. **Add package search** — `GET /api/search?q=fetch` returning matching package slugs.
5. **Distinguish unaudited from clean** — Return `{"status": "unaudited"}` vs `{"findings": [], "trust_score": 100}`.
6. **Document package location** — Add a section on where to find files for npm/pip/skill packages.
7. **Clarify Finding ID** — State explicitly: "Use the numeric `id` field (not `ecap_id`) in API URLs."

### Gesamtnote: 6/10

**Good concept, solid tooling, but the documentation-API mismatch is a showstopper.** An agent following the SKILL.md exactly will fail at the two most important tasks: uploading reports and running the security gate. The audit/review prompts are the strongest part. Fix the three critical bugs and this becomes an 8/10.
