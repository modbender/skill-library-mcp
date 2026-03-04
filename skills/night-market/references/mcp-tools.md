# Nightmarket MCP Tools

Detailed reference for the three tools provided by the Nightmarket MCP server.

## browse_services

Search and list available APIs on Nightmarket.

**Parameters:**
- `search` (string, optional) — Filter by name, description, or seller

**Returns:** List of services with:
- Service name and ID
- HTTP method (GET, POST, etc.)
- Price in USDC per call
- Seller company name
- Description

**Example:**
```
browse_services(search: "weather")
```

## get_service_details

Get full details about a specific service.

**Parameters:**
- `endpoint_id` (string, required) — The endpoint ID from browse_services

**Returns:**
- Service name, seller, method, price
- Total calls made
- Full description
- Request example (if available)
- Response example (if available)

**Example:**
```
get_service_details(endpoint_id: "abc123")
```

## call_service

Call an API with automatic USDC payment via x402.

**Parameters:**
- `endpoint_id` (string, required) — The endpoint ID to call
- `method` (enum, optional) — GET, POST, PUT, PATCH, DELETE (default: GET)
- `body` (string, optional) — Request body for POST/PUT/PATCH
- `headers` (Record<string, string>, optional) — Additional HTTP headers

**Returns:** API response with status code and body

**Requires:** `WALLET_KEY` environment variable set in MCP config

**Example:**
```
call_service(
  endpoint_id: "abc123",
  method: "POST",
  body: '{"query": "weather in NYC"}'
)
```

**Error cases:**
- Missing `WALLET_KEY` — Returns setup instructions with CrowPay link
- Invalid endpoint — Returns error message
- Payment failure — Returns x402 error details
