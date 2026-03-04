# Error Handling Guide

Common errors and solutions when working with Feishu automation.

## Common Error Codes

### Feishu API Errors

| Code | Meaning | Solution |
|------|---------|----------|
| `99991663` | No permission | Check app scopes; ensure document/folder is shared with app |
| `99991664` | File not found | Verify token exists and is accessible |
| `99991665` | Invalid parameter | Check parameter format and required fields |
| `99991672` | Rate limit exceeded | Implement exponential backoff retry |
| `99991673` | Quota exceeded | Upgrade plan or reduce frequency |
| `99991679` | Internal server error | Retry with backoff; contact Feishu support if persistent |
| `99991700` | Invalid access token | Refresh tenant_access_token or user_access_token |

### OpenClaw Tool Errors

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| "Missing required parameter" | Tool call missing parameters | Check tool documentation for required fields |
| "Tool not available" | Feishu integration not configured | Run `openclaw configure` to set up Feishu |
| "Permission denied" | App lacks required scopes | Add missing scopes in Feishu developer console |

## Retry Strategies

### Exponential Backoff
```python
import time
import random

def call_feishu_api_with_retry(api_call, max_retries=3):
    """Call API with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return api_call()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
        except (TokenExpiredError, InvalidTokenError):
            # Refresh token and retry immediately
            refresh_access_token()
            continue
```

### Circuit Breaker Pattern
```python
class FeishuCircuitBreaker:
    """Circuit breaker for Feishu API calls."""
    
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_count = 0
        self.last_failure_time = None
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, api_call):
        if self.state == "OPEN":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = api_call()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
```

## Permission Troubleshooting

### Required Scopes Checklist

Ensure your Feishu app has these scopes enabled:

**Documents:**
- [ ] `docx:document` - Read/write documents
- [ ] `docx:document:readonly` - Read-only access
- [ ] `docx:document.block:convert` - Access to blocks

**Wiki:**
- [ ] `wiki:wiki` - Full wiki access
- [ ] `wiki:wiki:readonly` - Read-only wiki access

**Bitable:**
- [ ] `bitable:app` - Full Bitable access
- [ ] `bitable:app:readonly` - Read-only Bitable access

**Drive:**
- [ ] `drive:drive` - Full drive access
- [ ] `drive:drive:readonly` - Read-only drive access

### Testing Permissions
```bash
# Check current scopes
openclaw tool call feishu_app_scopes

# Test document access
openclaw tool call feishu_doc --action read --doc_token doxcnXXX
```

## Data Validation

### Token Validation
```python
def validate_feishu_token(token, token_type="doc"):
    """Validate Feishu token format."""
    
    patterns = {
        "doc": r"^doxcn[a-zA-Z0-9]+$",
        "wiki": r"^wikcn[a-zA-Z0-9]+$",
        "folder": r"^fldcn[a-zA-Z0-9]+$",
        "bitable": r"^bas[a-zA-Z0-9]+$",
        "table": r"^tbl[a-zA-Z0-9]+$"
    }
    
    import re
    pattern = patterns.get(token_type, r"^[a-zA-Z0-9]+$")
    
    if not re.match(pattern, token):
        raise ValueError(f"Invalid {token_type} token format: {token}")
    
    return True
```

### URL Parsing
```python
def parse_feishu_url(url):
    """Extract tokens from Feishu URLs."""
    
    patterns = {
        r"feishu\.cn/docx/([a-zA-Z0-9]+)": ("doc", "doxcn"),
        r"feishu\.cn/wiki/([a-zA-Z0-9]+)": ("wiki", "wikcn"),
        r"feishu\.cn/drive/folder/([a-zA-Z0-9]+)": ("folder", "fldcn"),
        r"feishu\.cn/base/([a-zA-Z0-9]+)\?table=([a-zA-Z0-9]+)": ("bitable", ("bas", "tbl"))
    }
    
    for pattern, (token_type, prefix) in patterns.items():
        match = re.search(pattern, url)
        if match:
            if token_type == "bitable":
                app_token, table_id = match.groups()
                return {
                    "type": "bitable",
                    "app_token": prefix[0] + app_token,
                    "table_id": prefix[1] + table_id
                }
            else:
                token = prefix + match.group(1)
                return {"type": token_type, "token": token}
    
    raise ValueError(f"Unrecognized Feishu URL format: {url}")
```

## Recovery Strategies

### Failed Document Updates
```python
def safe_document_update(doc_token, content, backup_dir="/tmp/feishu_backup"):
    """Update document with backup and retry."""
    
    # 1. Backup current content
    try:
        backup = read_document(doc_token)
        backup_file = f"{backup_dir}/{doc_token}_{datetime.now().isoformat()}.md"
        save_backup(backup, backup_file)
    except Exception as e:
        log_warning(f"Backup failed: {e}")
    
    # 2. Attempt update with retry
    for attempt in range(3):
        try:
            update_document(doc_token, content)
            log_info(f"Document updated successfully on attempt {attempt + 1}")
            return True
        except Exception as e:
            if attempt == 2:
                log_error(f"Failed to update document after 3 attempts: {e}")
                
                # 3. Restore from backup if possible
                try:
                    if 'backup' in locals():
                        update_document(doc_token, backup)
                        log_info("Restored from backup")
                except Exception as restore_error:
                    log_error(f"Restore also failed: {restore_error}")
                
                return False
    
    return False
```

### Data Corruption Recovery
```python
def recover_from_corruption(doc_token, known_good_version=None):
    """Attempt to recover a corrupted document."""
    
    recovery_strategies = [
        # Strategy 1: Use known good version
        lambda: update_document(doc_token, known_good_version) if known_good_version else None,
        
        # Strategy 2: Extract text from blocks
        lambda: recover_from_blocks(doc_token),
        
        # Strategy 3: Create new document and migrate
        lambda: create_new_and_migrate(doc_token),
        
        # Strategy 4: Use version history if available
        lambda: restore_from_version_history(doc_token)
    ]
    
    for strategy in recovery_strategies:
        try:
            result = strategy()
            if result:
                log_info(f"Recovery succeeded with strategy {recovery_strategies.index(strategy) + 1}")
                return result
        except Exception as e:
            log_warning(f"Recovery strategy failed: {e}")
            continue
    
    raise RecoveryError("All recovery strategies failed")
```

## Monitoring and Alerting

### Health Checks
```python
def check_feishu_health():
    """Perform health check on Feishu integration."""
    
    checks = [
        ("Token validity", check_access_token),
        ("API connectivity", check_api_endpoint),
        ("Rate limit status", check_rate_limit),
        ("Permission status", check_permissions)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            status = check_func()
            results.append({"check": check_name, "status": "PASS", "details": status})
        except Exception as e:
            results.append({"check": check_name, "status": "FAIL", "error": str(e)})
    
    return results
```

### Alert Configuration
```yaml
# Example alert configuration
alerts:
  - condition: "failure_count > 5 in 10min"
    action: "notify_slack channel=#alerts message='Feishu API issues detected'"
  
  - condition: "rate_limit_hit"
    action: "reduce_frequency multiplier=0.5"
  
  - condition: "permission_error"
    action: "notify_admin email=admin@example.com"
```

## Prevention Best Practices

1. **Validate inputs**: Always validate tokens and parameters before API calls
2. **Implement monitoring**: Track API usage, error rates, and latency
3. **Use caching**: Cache frequently accessed data to reduce API calls
4. **Follow rate limits**: Stay well below published rate limits
5. **Regular testing**: Test automation regularly with different scenarios
6. **Keep backups**: Maintain backups of important documents and data
7. **Document procedures**: Document recovery procedures for common failures