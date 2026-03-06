# Error Handling - Salesforce API

## Error Response Format

```json
[
  {
    "errorCode": "INVALID_FIELD",
    "message": "No such column 'Industryy' on entity 'Account'",
    "fields": ["Industryy"]
  }
]
```

## Common Error Codes

### Authentication Errors

| Code | HTTP | Cause | Fix |
|------|------|-------|-----|
| `INVALID_SESSION_ID` | 401 | Token expired or invalid | Re-authenticate |
| `INVALID_AUTH_HEADER` | 401 | Malformed Authorization header | Check Bearer format |
| `INVALID_LOGIN` | 401 | Bad credentials | Verify username/password |

### Authorization Errors

| Code | HTTP | Cause | Fix |
|------|------|-------|-----|
| `INSUFFICIENT_ACCESS` | 403 | No permission | Check profile/permission set |
| `FIELD_INTEGRITY_EXCEPTION` | 400 | Field-level security | Grant field access |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | 400 | Trigger/validation error | Check automation |

### Query Errors

| Code | HTTP | Cause | Fix |
|------|------|-------|-----|
| `MALFORMED_QUERY` | 400 | SOQL syntax error | Fix query syntax |
| `INVALID_FIELD` | 400 | Field doesn't exist | Check field API name |
| `INVALID_TYPE` | 400 | Object doesn't exist | Check object API name |
| `QUERY_TOO_COMPLICATED` | 400 | Query too complex | Simplify or split |

### Record Errors

| Code | HTTP | Cause | Fix |
|------|------|-------|-----|
| `NOT_FOUND` | 404 | Record doesn't exist | Verify record ID |
| `DUPLICATE_VALUE` | 400 | Unique field violation | Check for duplicates |
| `REQUIRED_FIELD_MISSING` | 400 | Required field empty | Provide required fields |
| `FIELD_FILTER_VALIDATION_EXCEPTION` | 400 | Validation rule failed | Check validation rules |
| `ENTITY_IS_DELETED` | 400 | Record was deleted | Record in recycle bin |

### Limit Errors

| Code | HTTP | Cause | Fix |
|------|------|-------|-----|
| `REQUEST_LIMIT_EXCEEDED` | 403 | API limit reached | Wait or reduce calls |
| `EXCEEDED_MAX_SEMIJOIN_SUBQUERIES` | 400 | Too many subqueries | Split query |
| `QUERY_TIMEOUT` | 400 | Query took too long | Add filters/limits |

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success (GET, query) |
| 201 | Created (POST) |
| 204 | No Content (PATCH, DELETE success) |
| 400 | Bad Request (malformed query, missing field) |
| 401 | Unauthorized (auth failed) |
| 403 | Forbidden (no permission) |
| 404 | Not Found (bad ID or URL) |
| 405 | Method Not Allowed |
| 500 | Server Error (retry) |

## Handling Token Expiration

Access tokens expire. Detect and refresh:

```python
def sf_request(method, url, **kwargs):
    response = requests.request(method, url, **kwargs)
    
    if response.status_code == 401:
        error = response.json()
        if error[0].get('errorCode') == 'INVALID_SESSION_ID':
            # Refresh token and retry
            new_token = refresh_access_token()
            kwargs['headers']['Authorization'] = f'Bearer {new_token}'
            return requests.request(method, url, **kwargs)
    
    return response
```

## Retry Strategy

```python
import time

def sf_request_with_retry(method, url, **kwargs):
    max_retries = 3
    
    for attempt in range(max_retries):
        response = requests.request(method, url, **kwargs)
        
        if response.status_code == 503:  # Service unavailable
            time.sleep(2 ** attempt)
            continue
        
        if response.status_code == 403:
            error = response.json()
            if 'REQUEST_LIMIT_EXCEEDED' in str(error):
                time.sleep(60)  # Wait for limit reset
                continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

## Validation Rule Errors

When validation rules fail:

```json
[
  {
    "errorCode": "FIELD_CUSTOM_VALIDATION_EXCEPTION",
    "message": "Email must be company domain",
    "fields": ["Email"]
  }
]
```

## Trigger Errors

When triggers fail:

```json
[
  {
    "errorCode": "CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY",
    "message": "AccountTrigger: execution of BeforeInsert...",
    "fields": []
  }
]
```

## Debugging Tips

1. **Check field API names** - Use describe to verify names
2. **Test in Workbench** - Validate SOQL before API calls
3. **Check permissions** - Profile, permission sets, field-level security
4. **Review automation** - Triggers, flows, validation rules
5. **Check limits** - API calls, storage, governor limits
6. **Use debug logs** - Enable in Setup → Debug Logs
