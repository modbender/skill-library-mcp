# Swaps Intel Skill (ClawHub Launch Pack)

Swaps Intel gives AI agents blockchain risk signals for wallet addresses and transactions. Supports multiple EVM and UTXO chains.

## What this skill does
- Checks a crypto address or transaction using Swaps Intelligence API via `agent.check`, `agent.trace`, `agent.tx` actions.
- Returns risk score, sanctions/labels, confidence tier, and report link.
- Helps users triage potential scam exposure.

## What this skill does **not** do
- Does **not** provide legal advice
- Does **not** provide investment advice
- Does **not** guarantee asset recovery
- Does **not** make definitive criminal allegations

## Trust Signals
- **Version**: 1.1.0
- **Rate Limits**: Free tier allows 10 req/min, 500 req/day. (Pro and Enterprise available).
- **Uptime & SLA**: Best-effort 99.9% uptime on API endpoints.

## API Endpoint
- Base URL: `https://system.swaps.app/functions/v1/agent-api`
- Operations: `POST /` (for generic actions) or `POST /check_address_risk` (compatibility alias)
- Auth: Standardized on `x-api-key: <API_KEY>` header. (Fallback: `Authorization: Bearer <API_KEY>`. If both are provided, `x-api-key` takes precedence).

## Minimal Request Examples

**1. Action-based format (Recommended)**
```bash
curl -X POST https://system.swaps.app/functions/v1/agent-api/ \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "action": "agent.check",
    "payload": {
      "address": "0x1234..."
    }
  }'
```

**2. Compatibility Alias format**
```bash
curl -X POST https://system.swaps.app/functions/v1/agent-api/check_address_risk \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "address": "0x1234..."
  }'
```

## Minimal response (shape)
```json
{
  "ok": true,
  "requestId": "req-123",
  "data": {
    "risk_score": 85,
    "labels": ["Scam"],
    "report_url": "https://swaps.app/report/...",
    "confidence_tier": "high",
    "markdown_summary": "..."
  }
}
```

## Mandatory output policy for agents using this skill
1. Treat output as **risk analytics**, not final truth.
2. Keep factual data unchanged.
3. Always include source/report link if returned.
4. Include disclaimer text in user-facing response.

## Required disclaimer (copy-paste)
> Swaps Search provides blockchain analytics signals for informational purposes only. Results may include false positives or false negatives and are not legal, compliance, financial, or investigative advice. Swaps does not guarantee asset recovery outcomes. Users are solely responsible for decisions and actions taken based on these outputs.

## Links
- Bot: https://t.me/SwapSearchBot
- Product: https://www.swaps.app/search
- Contact: support@swaps.app