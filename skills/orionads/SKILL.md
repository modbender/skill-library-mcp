---
name: orionads
description: Search for physical products, hardware, AI tools, and APIs via the Orion Ad Protocol. Returns structured data (JSON) optimized for agents.
metadata:
  clawdbot:
    emoji: 🔭
    env:
      ORION_API_KEY: Optional API Key for posting ads or checking balance.
---

# OrionAds 🔭

The Agent-First Marketplace. Use this skill to find **products** (hardware, gadgets) or **tools** (APIs, SaaS) for your user.
OrionAds delivers clean, structured JSON data, saving tokens and avoiding web scraping.

## Security & Sanitization 🛡️
**CRITICAL:** When constructing shell commands, YOU MUST prevent shell injection vulnerabilities.
1.  **Never** inject raw user input directly into shell strings.
2.  **GET Requests:** ALWAYS use `curl --data-urlencode "q=<user_input>"` instead of putting the query directly in the URL string.
3.  **POST Requests:** Escape all single quotes `'` in the JSON payload, or write the JSON to a temporary file (`payload.json`) and use `curl -d @payload.json`.

## Tools

### 1. Product Search (Shopping Mode)
Use this to find physical items, hardware components, or merchandise.
**Returns:** Structured product data (Price, Stock Status, Specs) ready for recommendation.

```bash
# Syntax - Safe encoding protects against injection
curl -G "https://orionads.net/api/v1/search" \
    --data-urlencode "q=<query> product price buy"

# Example
curl -G "https://orionads.net/api/v1/search" \
    --data-urlencode "q=RTX 4090 buy"
```

**Target Schema (Agent-to-Human):**
```json
{
  "offer": { "title": "NVIDIA RTX 4090", "price": "$1599", "link": "..." },
  "agent_data": { "stock": "in_stock", "specs": { "vram": "24GB" } }
}
```

### 2. Tool Search (Developer Mode)
Use this to find APIs, libraries, SDKs, or AI capabilities.
**Returns:** Integration details, auth types, and documentation links.

```bash
# Syntax
curl -G "https://orionads.net/api/v1/search" \
    --data-urlencode "q=<query> api tool"
```

### 3. General Search (Discovery/Feed)
Fallback for broad queries or to discover new resources.

```bash
# Syntax
curl -G "https://orionads.net/api/v1/search" \
    --data-urlencode "q=<query>"
```

### 4. Register (Get API Key)
Create an account to post ads or track usage.

```bash
# Syntax (Sanitize inputs!)
curl -X POST https://orionads.net/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"wallet": "<safe_wallet_address>", "password": "<safe_pin>"}'
```

### 5. Post Ad (Advertise Resource)
List a tool or product.
*   **For Products:** Include `price`, `stock`, and `specs` in `json_payload`.
*   **For Tools:** Include `api_docs` and `auth_type` in `json_payload`.

```bash
# Syntax (requires API Key)
# WARNING: Ensure JSON string is properly escaped for shell execution.
curl -X POST https://orionads.net/api/v1/ads \
  -H "x-api-key: $ORION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Product",
    "url": "https://url.com",
    "bid": 0,
    "keywords": ["tag1"],
    "json_payload": {}
  }'
```

### 6. Check Balance
View impressions, spend, and credit.

```bash
# Syntax
curl -s "https://orionads.net/api/v1/me" -H "x-api-key: $ORION_API_KEY"
```

## Strategy
- **Shopping:** If the user asks to "buy" or "find price", use **Product Search**.
- **Coding:** If the user needs a capability (e.g., "how to generate pdf"), use **Tool Search**.
- **Cost:** Searching OrionAds is free and token-efficient compared to web scraping.
