# Error Handling - Notion API

## Error Response Format

```json
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "Description"
}
```

## Common Errors

### 400 Bad Request

| Code | Cause | Fix |
|------|-------|-----|
| `invalid_json` | Malformed JSON | Validate syntax |
| `invalid_request` | Missing field | Check body |
| `validation_error` | Invalid value | Check types |

### 401 Unauthorized

| Code | Cause | Fix |
|------|-------|-----|
| `unauthorized` | Invalid token | Check API key |

### 404 Not Found

| Code | Cause | Fix |
|------|-------|-----|
| `object_not_found` | Page doesn't exist | Verify ID |
| | Not shared | Share with integration |
| | ID has dashes | Remove dashes |

### 429 Rate Limited

| Code | Cause | Fix |
|------|-------|-----|
| `rate_limited` | Too many requests | Wait and retry |

Rate limits: 3 requests/second average

### 500+ Server Error

| Code | Cause | Fix |
|------|-------|-----|
| `internal_server_error` | Notion issue | Retry later |

## Retry Strategy

```python
import time

def notion_request(method, url, **kwargs):
    max_retries = 3
    
    for attempt in range(max_retries):
        response = requests.request(method, url, **kwargs)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
            time.sleep(retry_after)
            continue
        
        if response.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

## Common Mistakes

### Missing Notion-Version Header
```
400: Notion-Version header is required
```
Fix: Add `-H "Notion-Version: 2022-06-28"`

### Page ID with Dashes
```
404: object_not_found
```
URL: `Page-abc-123-def-456` -> ID: `abc123def456`

### Property Name Mismatch
```
400: Property 'status' not found
```
Property names are case-sensitive. Use exact name.

### Unshared Page
```
404: object_not_found
```
Integration can only access shared pages.

## Debugging Tips

1. Check full error response
2. Test token with `/v1/users/me`
3. Verify page is shared
4. Remove dashes from IDs
5. Match property types exactly
