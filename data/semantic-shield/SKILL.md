---
name: semantic-shield
version: 1.0.0
description: AI skill safety validation — real human experts vet skills, plugins, and MCP tools for security risks. Query trust scores, submit evaluation inquiries, and get real-time safety verdicts before installing anything in your AI agents. Safety scoring 0–100, threat detection, continuous 0-day monitoring. Lightweight SaaS component from Simply Semantics for AI agents, bots, and security-conscious builders.
tags: ["security", "trust", "vetting", "ai-safety", "skill-validation", "mcp-compatible", "agent-safety", "risk-scoring", "saas-component"]
homepage: https://www.simplysemantics.com/semantic-shield.html
author: Simply Semantics (@simplysemantics)
license: MIT

metadata:
  clawbot:
    emoji: "🛡️🔒"
    requires:
      env: ["SEMANTIC_SHIELD_API_KEY"]
      primaryEnv: "SEMANTIC_SHIELD_API_KEY"
    files: []
---

# Semantic Shield

**Quick summary**
AI skill safety validation powered by real human security experts. Before your agent installs a skill, plugin, or MCP tool — check its trust profile. Get a safety score (0–100), risk level, threat details, and a clear install/reject recommendation. If the skill hasn't been vetted yet, submit it for expert evaluation. Continuous 0-day monitoring keeps assessments current.

100% REAL human security staff with 30+ years of enterprise security experience, including US Homeland Security. No AI-only reviews — every skill is assessed by trusted experts.

## When to use this skill (activation triggers)

Activate **Semantic Shield** when the user or agent:
- Is about to install, enable, or use an AI skill, plugin, tool, or MCP endpoint.
- Asks "is this skill safe?", "should I trust this plugin?", "check this tool's security", "vet this skill".
- Wants to look up a skill's safety score, risk level, or threat profile.
- Wants to submit an unknown or unvetted skill for expert security review.
- Needs to verify trust before autonomous agent action (install, execute, delegate).
- Asks about skill security, compliance, or risk assessment.

Do **NOT** use for:
- General cybersecurity questions unrelated to AI skills/plugins.
- Scanning websites, IPs, or infrastructure (use dedicated security tools).
- PII lookup or identity verification.
- Code review or static analysis (Semantic Shield evaluates holistic skill risk, not line-by-line code).

## How to use (instructions for the agent)

### 1. Search for a skill (free — no quota cost)

Check if a skill exists in the Semantic Shield database before using a lookup.

**GET** `${SEMANTIC_SHIELD_API_BASE:-https://dashboard.simplysemantics.com/shield}/api/v1/search`

Headers:
```text
x-api-key: ${SEMANTIC_SHIELD_API_KEY}
```

Query parameters:
- `q` — skill name or ID (partial match)
- `provider` — optional provider name filter

Example:
```
GET /api/v1/search?q=weather&provider=example-ai
```

Response:
```json
{
  "results": [
    { "skill_id": "weather-pro-v2", "provider": "example-ai" }
  ],
  "count": 1
}
```

### 2. Check a skill's trust profile (costs 1 lookup)

Get full safety details for a specific skill.

**GET** `${SEMANTIC_SHIELD_API_BASE:-https://dashboard.simplysemantics.com/shield}/api/v1/check`

Headers:
```text
x-api-key: ${SEMANTIC_SHIELD_API_KEY}
```

Query parameters:
- `skill_id` — exact skill identifier (required)
- `provider` — exact provider name (required)

Example:
```
GET /api/v1/check?skill_id=weather-pro-v2&provider=example-ai
```

Response (vetted):
```json
{
  "skill_id": "weather-pro-v2",
  "provider": "example-ai",
  "skill_url": "https://example.com/weather-pro-v2",
  "vetted": true,
  "vetted_by": "Simply Semantics",
  "safety_score": 92,
  "risk_level": "safe",
  "risk_summary": "No known vulnerabilities. Permissions scoped correctly.",
  "threats_found": [],
  "recommendation": "safe to install",
  "last_checked": "2026-02-28"
}
```

Response (not vetted — 404):
```json
{
  "skill_id": "unknown-plugin",
  "provider": "unverified-co",
  "vetted": false,
  "safety_score": null,
  "risk_level": "unknown",
  "recommendation": "not vetted - install at your own risk",
  "message": "This skill has not been reviewed. Submit it for validation.",
  "submit_url": "/api/v1/validate"
}
```

### 3. Submit a skill for vetting (costs 1 inquiry)

If a skill is not in the database, submit it for expert evaluation.

**POST** `${SEMANTIC_SHIELD_API_BASE:-https://dashboard.simplysemantics.com/shield}/api/v1/validate`

Headers:
```text
x-api-key: ${SEMANTIC_SHIELD_API_KEY}
Content-Type: application/json
```

Body:
```json
{
  "skill_id": "new-plugin-v1",
  "provider": "some-provider",
  "skill_url": "https://example.com/new-plugin"
}
```

Response:
```json
{
  "message": "Skill submitted for evaluation.",
  "request_id": "abc-123",
  "skill_id": "new-plugin-v1",
  "provider": "some-provider",
  "status": "pending"
}
```

### 4. Decision logic for agents

Based on the response, the agent should:

| safety_score | risk_level | Action |
|---|---|---|
| 90–100 | safe | ✅ Install / proceed |
| 75–89 | low | ✅ Install, note minor risks |
| 50–74 | medium | ⚠️ Warn user, ask for confirmation |
| 25–49 | high | ❌ Recommend against, require explicit override |
| 0–24 | critical | 🚫 Block installation, alert user |
| null | unknown | ⚠️ Not vetted — submit for review or warn user |

### 5. Edge cases

- **401/403** → "Missing or invalid SEMANTIC_SHIELD_API_KEY. Set the env var to use this skill."
- **429** → "Rate/quota limit reached — upgrade your plan or retry later."
- **404** → Skill not vetted. Offer to submit for evaluation or warn user.
- **500** → "Service temporarily unavailable. Try again shortly."

## Output format

Present results clearly to the user:

```
🛡️ Semantic Shield — Trust Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Skill:          weather-pro-v2
Provider:       example-ai
Safety Score:   92/100 ✅
Risk Level:     SAFE
Recommendation: Safe to install
Threats:        None detected
Last Checked:   Feb 28, 2026
Vetted By:      Simply Semantics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

