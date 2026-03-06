---
name: meerkat-governance
description: AI governance API with two endpoints. Shield scans untrusted content for prompt injection and threats. Verify checks AI output for hallucinations, numerical errors, and manipulation against source data. Returns structured results with trust scores and remediation guidance. Full audit trail.
homepage: https://meerkatplatform.com
metadata:
  clawdbot:
    emoji: "🔒"
    requires:
      env:
        - MEERKAT_API_KEY
    tags:
      - security
      - governance
      - safety
---

# Meerkat Governance

Scope: This skill provides two API endpoints your agent can call. It does not auto-activate, does not run in the background, and does not access content unless explicitly called by the agent. The developer controls what content is sent to Meerkat.

Privacy and data handling: https://meerkatplatform.com/privacy
Meerkat processes content in memory and discards it after the response. Only trust scores and metadata are stored. No raw content is retained. No data is shared with third parties. All processing stays in Canada.

Security: Your API key authenticates requests to Meerkat's API. Rotate keys via the dashboard if compromised. All communication is TLS 1.2+ encrypted. Meerkat endpoints are hosted on Azure Container Apps with managed SSL certificates. Verify the endpoint hostname (api.meerkatplatform.com) matches the TLS certificate before sending data.

## Ingress Shield

The `/v1/shield` endpoint scans content for prompt injection, jailbreaks, data exfiltration, and social engineering. The agent can call this before processing content the developer designates as untrusted. Common examples include external emails, web-scraped content, and user-uploaded documents. Developers can optionally configure their agent to shield skill descriptions before installation.

```bash
curl -s -X POST https://api.meerkatplatform.com/v1/shield \
  -H "Authorization: Bearer $MEERKAT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"<THE_CONTENT>\"}"
```

**Response fields:**
- `safe` (boolean): Whether the content passed scanning
- `threat_level`: `NONE`, `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`
- `attack_type`: Category of detected threat (if any)
- `detail`: Human-readable description
- `sanitized_input`: Content with threats removed (when available)
- `audit_id`: Unique identifier for the audit record

The agent can use the response to decide how to proceed. For example, content flagged `HIGH` or `CRITICAL` could be blocked, while `MEDIUM` could prompt user confirmation. If `sanitized_input` is returned, the agent can use the cleaned version.

## Egress Verify

The `/v1/verify` endpoint checks AI-generated output against source data using up to five ML checks: entailment (DeBERTa NLI), numerical verification, semantic entropy, implicit preference detection, and claim extraction.

```bash
curl -s -X POST https://api.meerkatplatform.com/v1/verify \
  -H "Authorization: Bearer $MEERKAT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"<USER_REQUEST>\", \"output\": \"<AI_OUTPUT>\", \"context\": \"<SOURCE_DATA>\", \"domain\": \"<DOMAIN>\"}"
```

The `domain` field applies domain-specific rules. Supported values: `healthcare`, `financial`, `legal`, `general`.

**Response fields:**
- `trust_score` (0-100): Weighted composite score across all checks
- `status`: `PASS` or `FLAG` (severity communicated via `trust_score` and `remediation.severity`)
- `checks`: Per-check scores, flags, and details
- `remediation`: Corrections and agent instructions (when status is not `PASS`)
- `audit_id`: Unique identifier for the audit record
- `session_id`: Session identifier for linking retry attempts

The agent can use the status and trust score to decide whether to proceed. When `remediation` is present, the `agent_instruction` field contains guidance for self-correction, and `corrections` lists specific errors (e.g., found value vs expected value). The agent can regenerate output with corrections applied and resubmit using the same `session_id` to link attempts.

## Observation Mode

When no `context` field is provided, Meerkat runs in observation mode: it checks semantic entropy and implicit preference but skips source-grounded checks. The `context_mode` field in the response will be `observation`. This is useful for checking open-ended generation where no source document exists.

## Audit Trail

Every shield and verify call is logged with an audit ID. The `/v1/audit/<audit_id>` endpoint retrieves the full record. Add `?include_session=true` to see all linked attempts in a retry session.

```bash
curl -s https://api.meerkatplatform.com/v1/audit/<audit_id> \
  -H "Authorization: Bearer $MEERKAT_API_KEY"
```

## Setup

1. Get a free API key at https://meerkatplatform.com (10,000 verifications/month, no credit card)
2. Set the environment variable: `MEERKAT_API_KEY=mk_live_your_key_here`
3. The developer controls which content is sent to Meerkat through their agent configuration. The agent calls the shield endpoint before processing untrusted external content, and the verify endpoint before executing high-impact actions.

## Detection Capabilities

See https://meerkatplatform.com/docs for example payloads and response formats.

**Ingress** detects: prompt injection, indirect injection, data exfiltration attempts, jailbreak and role-hijacking patterns, credential harvesting, and social engineering.

**Egress** detects: hallucinated facts, numerical distortions (medication doses, financial figures, legal terms), fabricated entities and citations, confident confabulation, bias and implicit preference, and ungrounded numbers.

## Usage Headers

Every API response includes usage headers:
- `X-Meerkat-Usage`: Current verification count
- `X-Meerkat-Limit`: Monthly limit (or "unlimited")
- `X-Meerkat-Remaining`: Verifications remaining
- `X-Meerkat-Warning`: Warning when approaching limit (80%+)

## Privacy

Meerkat processes content for security scanning only. Content is not stored beyond the audit trail retention period. Your API key is scoped to your organization. See https://meerkatplatform.com/privacy for details.
