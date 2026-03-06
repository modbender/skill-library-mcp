# Security Features & Mitigations

This document outlines the security measures implemented in the ProductAI skill.

## Security Fixes Applied

### ✅ Fixed Issues

#### 1. URL Validation & SSRF Prevention
**Issue:** Image URLs accepted without validation, potential SSRF attacks  
**Fix:** `productai_client.py:validate_image_url()`
- **HTTPS-only:** Rejects HTTP URLs
- **Private network blocking:** Prevents access to:
  - localhost / 127.x.x.x
  - Private IPs (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
  - Link-local addresses (169.254.x.x)
  - IPv6 localhost/link-local (::1, fe80::)
- Applied to all image URL inputs in `generate()` and `upscale()`

#### 2. Request Timeouts
**Issue:** HTTP requests without timeouts could hang indefinitely  
**Fix:** Added 30-second timeout to all requests:
- `productai_client.py`: All API calls (`DEFAULT_TIMEOUT = 30`)
- `generate_photo.py`: Image downloads
- `upscale_image.py`: Image downloads
- `batch_generate.py`: Image downloads

#### 3. Rate Limiting (Batch Processing)
**Issue:** No rate limiting despite 15 req/min API limit  
**Fix:** `batch_generate.py`
- Enforces 4-second minimum between requests (15 req/min = 4s interval)
- Default max workers: 3 (to stay comfortably under limit)
- Sequential request submission with `time.sleep()` between requests

#### 4. Path Traversal Prevention
**Issue:** Unsanitized filenames in batch processing  
**Fix:** `batch_generate.py:sanitize_filename()`
- Removes path separators (`/`, `\`)
- Blocks parent directory references (`..`)
- Allows only alphanumeric, dash, underscore, dot
- Prevents hidden files (leading `.`)

---

## Acceptable Trade-offs

### Plain Text API Key Storage
**Rationale:**
- Industry standard for CLI tools (AWS CLI, gcloud, stripe-cli all do this)
- File permissions set to `600` (user read/write only)
- Alternative (OS keychain) adds complexity and dependencies
- Users can use environment variables if preferred: `PRODUCTAI_API_KEY`

**Mitigation:**
- Config file: `chmod 600` (user-only access)
- API key never logged or displayed in output
- Clear documentation warns users to keep keys secure

---

## Security Best Practices for Users

### 1. Protect Your API Key
- Never commit `config.json` to version control
- Don't share your API key in chat, logs, or screenshots
- Regenerate key if accidentally exposed

### 2. Use HTTPS URLs Only
- The skill enforces HTTPS-only image URLs
- Avoids exposing API keys over unencrypted connections

### 3. Monitor API Usage
- Check ProductAI dashboard regularly for unexpected usage
- Rate limits prevent runaway costs

### 4. Keep Dependencies Updated
- Run `pip install --upgrade requests` periodically
- Monitor security advisories for Python dependencies

---

## Implementation Details

### URL Validation (`productai_client.py`)

```python
@staticmethod
def validate_image_url(url: str) -> None:
    """Validate image URL for security."""
    parsed = urlparse(url)
    
    # Only allow HTTPS
    if parsed.scheme != 'https':
        raise ValueError(f"Only HTTPS URLs are allowed. Got: {parsed.scheme}://")
    
    # Block private/local network addresses (SSRF prevention)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid URL: missing hostname")
    
    # Block localhost, private IPs, link-local
    blocked_patterns = [
        r'^localhost$',
        r'^127\.',
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',
        r'^192\.168\.',
        r'^169\.254\.',
        r'^::1$',
        r'^fe80:',
    ]
    
    for pattern in blocked_patterns:
        if re.match(pattern, hostname, re.IGNORECASE):
            raise ValueError(f"Private/local addresses are not allowed: {hostname}")
```

### Request Timeouts

All HTTP requests include explicit timeouts:

```python
# API calls
response = self.session.post(url, json=payload, timeout=30)

# Image downloads
response = requests.get(url, stream=True, timeout=30)
```

### Rate Limiting (`batch_generate.py`)

```python
RATE_LIMIT_SECONDS = 4.0  # 15 req/min = 4s interval

for image_url in image_urls:
    # Rate limiting: ensure minimum time between requests
    elapsed = time.time() - last_request_time
    if elapsed < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - elapsed)
    
    # Submit job
    future = executor.submit(process_single_image, ...)
    last_request_time = time.time()
```

### Filename Sanitization (`batch_generate.py`)

```python
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    # Remove path separators and parent references
    safe_name = filename.replace('/', '_').replace('\\', '_').replace('..', '_')
    
    # Keep only safe characters
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
    
    # Prevent hidden files
    if safe_name.startswith('.'):
        safe_name = '_' + safe_name[1:]
    
    return safe_name
```

---

## Testing

All security fixes have been tested:

### URL Validation Tests
```bash
✓ Valid HTTPS URL accepted
✓ HTTP blocked: Only HTTPS URLs are allowed. Got: http://
✓ Localhost blocked: Private/local addresses are not allowed: localhost
✓ Private IP blocked: Private/local addresses are not allowed: 192.168.1.1
```

### Filename Sanitization Tests
```bash
✓ "normal.jpg" → "normal.jpg"
✓ "../../../etc/passwd" → "______etc_passwd"
✓ "file/with/slashes.png" → "file_with_slashes.png"
✓ ".hidden" → "_hidden"
✓ "file with spaces.jpg" → "file_with_spaces.jpg"
```

### Integration Test
```bash
✓ Real image generation with HTTPS URL: Success
✓ HTTP URL rejection: Blocked as expected
✓ Request timeout: All requests complete within 30s
```

---

## Reporting Security Issues

If you discover a security vulnerability in this skill:

1. **Do NOT open a public issue**
2. Contact the skill maintainer directly
3. Provide details: affected code, reproduction steps, potential impact
4. Allow reasonable time for a fix before public disclosure

---

## Version History

**v1.1.0** (2026-02-23)
- Added URL validation (HTTPS-only, SSRF prevention)
- Added request timeouts (30s default)
- Added rate limiting for batch processing
- Added filename sanitization

**v1.0.0** (2026-02-22)
- Initial release

---

**Security is a shared responsibility.** Keep your API keys secure, monitor usage, and report issues promptly.
