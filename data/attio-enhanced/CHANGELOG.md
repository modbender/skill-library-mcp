# Attio Enhanced - Changelog

## 2026-01-30 - Error Handling Improvements

### Changes

**Enhanced Error Response Capture:**
- Now captures full Attio API error response body when requests fail
- Stores error body in `error.error_body` attribute on exceptions
- Includes error details in exception message for better debugging

**Better Error Detection:**
- Enables detection of specific error types (e.g., `uniqueness_conflict`)
- Makes it possible to handle duplicate email errors gracefully
- Improves error messages with full API response context

### Technical Details

**Sync requests (`_make_request`):**
```python
# Now captures error response and stores in exception
if response.status_code >= 400:
    error_text = response.text
    error = requests.exceptions.HTTPError(...)
    error.error_body = error_text  # ← New attribute
    raise error
```

**Async requests (`_make_async_request`):**
```python
# Same improvement for async code
if response.status >= 400:
    response_text = await response.text()
    error = aiohttp.ClientResponseError(...)
    error.error_body = response_text  # ← New attribute
    raise error
```

### Benefits

1. **Better error handling** - Can detect specific error codes (like uniqueness_conflict)
2. **Cleaner scripts** - No need to parse log output to understand failures
3. **Graceful degradation** - Can skip known issues instead of failing
4. **Debugging** - Full API error response available in exceptions

### Compatibility

These changes are **backward compatible**. Existing code will continue to work unchanged. The new `error_body` attribute is optional and only used when needed.
