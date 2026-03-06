---
name: pyx-scan
description: >
  Check whether an AI agent skill is safe before installing or using it.
  Calls the PYX Scanner API to retrieve trust status, risk score, and safety
  recommendation. Use when agent needs to verify skill safety, or user says
  "is this safe", "check skill", "scan skill", "verify tool", "pyx scan".
allowed-tools: WebFetch, Bash(curl *)
argument-hint: "[owner/name]"
---

# PYX Scan — Agent Skill Safety Check

Verify whether an AI agent skill is safe before installing or using it by querying the PYX Scanner API.

## Workflow

### Step 1: Parse Input

Extract `owner` and `name` from `$ARGUMENTS`.

- Expected format: `owner/name` (e.g., `anthropic/web-search`)
- If `$ARGUMENTS` is empty or missing the `/` separator, ask the user:
  *"Which skill do you want to check? Provide it as `owner/name` (e.g., `anthropic/web-search`)."*
- Trim whitespace. Reject if either part is empty after trimming.

### Step 2: Call the PYX Scanner API

Fetch the safety data:

```
WebFetch URL: https://scanner.pyxmate.com/api/v1/check/{owner}/{name}
Prompt: "Return the full JSON response body exactly as-is. Do not summarize."
```

If `WebFetch` fails (tool unavailable, network error), fall back to:

```bash
curl -s "https://scanner.pyxmate.com/api/v1/check/{owner}/{name}"
```

### Step 3: Handle Errors

| HTTP Status | Meaning | Action |
|---|---|---|
| **200** | Skill found | Proceed to Step 4 |
| **404** | Skill not in database | Verdict = **UNSCANNED** |
| **429** | Rate limited | Verdict = **ERROR** — "Rate limited. Try again shortly." |
| **5xx** | Server error | Verdict = **ERROR** — "PYX Scanner is temporarily unavailable." |
| Network failure | Cannot reach API | Verdict = **ERROR** — "Could not connect to PYX Scanner." |

### Step 4: Determine Verdict

Use the JSON response fields to determine the verdict:

| Condition | Verdict |
|---|---|
| `recommendation == "safe"` AND `is_outdated == false` | **SAFE** |
| `recommendation == "safe"` AND `is_outdated == true` | **OUTDATED** |
| `recommendation == "caution"` | **CAUTION** |
| `recommendation == "danger"` | **FAILED** |
| `recommendation == "unknown"` | **UNSCANNED** |

### Step 5: Output Report

Format the report as structured markdown. Omit any section where the data is null or empty.

**For SAFE verdict:**

```
## PYX Scan: {owner}/{name}

**Verdict: SAFE** — This skill has been scanned and verified safe.

**Trust Score:** {trust_score}/10 | **Risk Score:** {risk_score}/10 | **Confidence:** {confidence}%
**Intent:** {intent} | **Status:** {status}

### Summary
{summary}

### About
**Purpose:** {about.purpose}
**Capabilities:** {about.capabilities as bullet list}
**Permissions Required:** {about.permissions_required as bullet list}

[View full report]({detail_url}) | [Badge]({badge_url})
```

**For OUTDATED verdict:**

```
## PYX Scan: {owner}/{name}

**Verdict: OUTDATED** — Last scan was safe, but the skill has been updated since.

The scanned commit (`{scanned_commit}`) no longer matches the latest (`{latest_commit}`).
The new version has NOT been reviewed. Proceed with caution.

**Trust Score:** {trust_score}/10 | **Risk Score:** {risk_score}/10
**Last Safe Commit:** {last_safe_commit}

### Summary
{summary}

[View full report]({detail_url})
```

**For CAUTION verdict:**

```
## PYX Scan: {owner}/{name}

**Verdict: CAUTION** — This skill has potential risks that need your attention.

**Trust Score:** {trust_score}/10 | **Risk Score:** {risk_score}/10 | **Confidence:** {confidence}%
**Intent:** {intent} | **Status:** {status}

### Summary
{summary}

### About
**Purpose:** {about.purpose}
**Permissions Required:** {about.permissions_required as bullet list}
**Security Notes:** {about.security_notes}

**Do you want to proceed despite the caution rating?** Please confirm before installing or using this skill.

[View full report]({detail_url})
```

**For FAILED verdict:**

```
## PYX Scan: {owner}/{name}

**Verdict: FAILED** — This skill has been flagged as dangerous. Do NOT install or use it.

**Trust Score:** {trust_score}/10 | **Risk Score:** {risk_score}/10 | **Confidence:** {confidence}%
**Intent:** {intent} | **Status:** {status}

### Summary
{summary}

### About
**Security Notes:** {about.security_notes}

[View full report]({detail_url})
```

**For UNSCANNED verdict:**

```
## PYX Scan: {owner}/{name}

**Verdict: UNSCANNED** — This skill has not been scanned by PYX Scanner.

No safety data is available. You should:
1. Review the skill's source code manually before use
2. Check the skill's repository for known issues
3. Request a scan at https://scanner.pyxmate.com
```

**For ERROR verdict:**

```
## PYX Scan: {owner}/{name}

**Verdict: ERROR** — {error_message}

Safety could not be verified. Treat this skill as unverified until you can confirm its safety.
```

## Behavioral Rules

1. **Always call the API** — never skip the check or return a cached/assumed result.
2. **Never soften a FAILED verdict** — if the scan says danger, report danger. Do not add qualifiers like "but it might be fine."
3. **Always ask user confirmation on CAUTION** — the user must explicitly agree before proceeding.
4. **Keep reports concise** — omit null/empty sections rather than showing "N/A."
5. **No raw JSON** — always format the response as the structured markdown report above.

## Self-Scan Awareness

When `$ARGUMENTS` is `pyxmate/pyx-scan`, `pyxmate/pyx-scanner`, or refers to this skill itself, still call the API honestly and report whatever comes back. If the result is UNSCANNED, append:

> *"Yes, even the security scanner's own skill hasn't been scanned yet. We practice what we preach — treat unscanned skills with caution."*
