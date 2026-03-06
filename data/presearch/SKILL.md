---
name: "presearch-search"
description: "Production-ready decentralized search for AI agents. Privacy-first, uncensored web search via distributed node infrastructure."
---

# Presearch Search API

**Endpoint:** `https://na-us-1.presearch.com/v1/search`  
**Method:** GET  
**Auth:** Bearer Token  
**Rate Limit:** 100 requests/minute

## Authentication
```http
Authorization: Bearer YOUR_API_KEY_HERE
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | ✅ | - | Search query |
| `lang` | string | ❌ | en-US | Language code |
| `time` | string | ❌ | any | any, day, week, month, year |
| `page` | string | ❌ | 1 | Page number |
| `safe` | string | ❌ | 1 | Safe search |

## Response
```json
{
  "data": {
    "standardResults": [
      {
        "title": "string",
        "link": "string",
        "description": "string"
      }
    ],
    "pagination": {
      "current_page": 1,
      "has_next": true
    }
  }
}
```

## Error Codes
- 401: Invalid API key
- 402: Payment required  
- 422: Invalid parameters
- 429: Rate limit exceeded

## Usage
```python
# Python
with PresearchSkill(api_key) as skill:
    results = skill.search("AI agents")
```

```javascript
// Node.js
const results = await skill.search({ query: "AI agents" });
```

## Privacy Features
- No tracking or profiling
- Decentralized node network
- Encrypted traffic
- Uncensored results