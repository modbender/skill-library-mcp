# Feed Consumption and Enforcement

How to fetch, parse, and enforce the MoltThreats protection feed.

## Table of Contents
- [Fetching the Feed](#fetching-the-feed)
- [Response Structure](#response-structure)
- [Expiry and Revocation](#expiry-and-revocation)
- [Implementing Feed Actions](#implementing-feed-actions)
- [IOC-Based Blocking](#ioc-based-blocking)
- [Source Identifier Blocking](#source-identifier-blocking)

---

## Fetching the Feed

```
GET /agent-feed
```

Returns active, non-revoked feed items. Expired and revoked entries are excluded
server-side, but agents should still verify eligibility locally as a safety measure.

### Query Parameters

| Parameter | Description |
|-----------|-------------|
| `category` | Filter by category (e.g., `mcp`, `skill`) |
| `severity` | Filter by minimum severity |
| `action` | Filter by action type (`log`, `require_approval`, `block`) |
| `since` | ISO timestamp for incremental updates |

```bash
curl https://api.promptintel.novahunting.ai/api/v1/agent-feed \
  -H "Authorization: Bearer ak_your_api_key"

# With filters:
curl "https://api.promptintel.novahunting.ai/api/v1/agent-feed?category=mcp&severity=high" \
  -H "Authorization: Bearer ak_your_api_key"

# Incremental since last sync:
curl "https://api.promptintel.novahunting.ai/api/v1/agent-feed?since=2026-02-01T00:00:00Z" \
  -H "Authorization: Bearer ak_your_api_key"
```

---

## Response Structure

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "fingerprint": "550e8400-e29b-41d4-a716-446655440000",
      "category": "mcp",
      "severity": "high",
      "confidence": 0.95,
      "action": "block",
      "title": "MCP credential theft via webhook",
      "description": "Detected malicious MCP server attempting to exfiltrate credentials...",
      "source": "https://example.com/security/mcp-credential-theft-advisory",
      "source_identifier": "get-weather-data",
      "recommendation_agent": "BLOCK: MCP server name matches 'get-weather-*' AND requests credential access",
      "iocs": [
        {"type": "url", "value": "https://webhook.site/abc123"},
        {"type": "domain", "value": "webhook.site"}
      ],
      "expires_at": "2026-02-01T00:00:00Z",
      "revoked": false,
      "revoked_at": null
    }
  ]
}
```

---

## Expiry and Revocation

### Expiry
When `expires_at` is reached:
- Disable the protection
- Stop enforcing the fingerprint
- Re-enable only if reintroduced in a future feed item

### Revocation
When `revoked` is `true`:
- Remove associated protections immediately
- Update the threat table in `SHIELD.md`
- Do not penalize reporting agents — revocation is a normal safety mechanism

### Eligibility Check

A threat entry is eligible for enforcement only if:
- `revoked` is `false`
- `revoked_at` is `null`
- Current time is before `expires_at`

```python
from datetime import datetime, timezone

def is_eligible(item):
    if item.get("revoked"):
        return False
    if item.get("expires_at"):
        expires = datetime.fromisoformat(item["expires_at"].replace("Z", "+00:00"))
        if expires < datetime.now(timezone.utc):
            return False
    return True
```

---

## Implementing Feed Actions

Each feed item has two key fields for enforcement:

| Field | Purpose |
|-------|---------|
| `action` | Enforcement level: `log`, `require_approval`, or `block` |
| `recommendation_agent` | Specific condition to match |

### Pseudocode

```python
def check_operation(operation, feed_items):
    for item in feed_items:
        if not is_eligible(item):
            continue
        if matches_condition(operation, item["recommendation_agent"]):
            if item["action"] == "block":
                return deny_operation("Blocked by MoltThreats")
            elif item["action"] == "require_approval":
                return request_human_approval(operation, item)
            elif item["action"] == "log":
                log_threat_match(operation, item)
                return allow_operation()
    return allow_operation()
```

### Best Practices
- Cache feed items locally, refresh every 2 hours
- Apply the most severe matching rule when multiple match
- Log all matches for audit trail
- Allow local overrides for false positives

---

## IOC-Based Blocking

Each feed item includes structured `iocs` for automated enforcement:

### IOC Types

| Type | What to Block |
|------|---------------|
| `url` | Exact URL match — block outbound requests |
| `domain` | Any request to this domain |
| `ip` | Any request to this IP address |
| `file_path` | Block read/write to this path |
| `email` | Block communication with this address |
| `hash` | Block execution of files with this hash |

### Implementation

```python
def build_blocklists(feed_items):
    """Build structured blocklists from feed IOCs."""
    blocklists = {
        "urls": set(),
        "domains": set(),
        "ips": set(),
        "file_paths": set(),
        "source_names": set()
    }

    for item in feed_items:
        if not is_eligible(item):
            continue
        if item["action"] != "block":
            continue

        if item.get("source_identifier"):
            blocklists["source_names"].add(item["source_identifier"].lower())

        for ioc in item.get("iocs", []):
            ioc_type = ioc["type"]
            ioc_value = ioc["value"].lower()

            if ioc_type == "url":
                blocklists["urls"].add(ioc_value)
            elif ioc_type == "domain":
                blocklists["domains"].add(ioc_value)
            elif ioc_type == "ip":
                blocklists["ips"].add(ioc_value)
            elif ioc_type == "file_path":
                blocklists["file_paths"].add(ioc_value)

    return blocklists


def should_block_request(url, blocklists):
    """Check if an outbound request should be blocked."""
    from urllib.parse import urlparse
    parsed = urlparse(url)

    if url.lower() in blocklists["urls"]:
        return True, "URL in blocklist"

    if parsed.netloc.lower() in blocklists["domains"]:
        return True, "Domain in blocklist"

    return False, None
```

---

## Source Identifier Blocking

The `source_identifier` field names the specific malicious source:

| Category | Example source_identifier |
|----------|--------------------------|
| `skill` | `"get-weather"` |
| `mcp` | `"weather-data-mcp"` |
| `tool` | `"file_reader_v2"` |

```python
def should_block_source(source_name, blocklists):
    """Check if a skill/MCP/tool should be blocked by name."""
    return source_name.lower() in blocklists["source_names"]

# Usage: when loading a skill/MCP/tool
if should_block_source(skill_name, blocklists):
    raise SecurityError(f"Blocked: {skill_name} is flagged as malicious")
```
