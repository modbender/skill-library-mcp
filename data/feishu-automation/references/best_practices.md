# Best Practices for Feishu Automation

Guidelines for reliable, efficient, and maintainable Feishu automation workflows.

## Performance Optimization

### Batch Operations
**Problem**: Making individual API calls for each document is slow and rate-limited.
**Solution**: Process documents in batches.

```python
def batch_process_documents(doc_tokens, operation, batch_size=10):
    """Process documents in batches to reduce API calls."""
    results = []
    
    for i in range(0, len(doc_tokens), batch_size):
        batch = doc_tokens[i:i+batch_size]
        batch_results = []
        
        # Process batch (in parallel if possible)
        for doc_token in batch:
            try:
                result = operation(doc_token)
                batch_results.append(result)
            except Exception as e:
                log_error(f"Failed {doc_token}: {e}")
        
        results.extend(batch_results)
        
        # Respect rate limits between batches
        if i + batch_size < len(doc_tokens):
            time.sleep(1)  # Pause between batches
    
    return results
```

### Caching Strategy
Cache frequently accessed data:

```python
from functools import lru_cache
import datetime

@lru_cache(maxsize=128)
def get_document_metadata(doc_token, ttl_minutes=60):
    """Cache document metadata with TTL."""
    cache_key = f"doc_meta:{doc_token}"
    
    # Check cache
    cached = cache_get(cache_key)
    if cached and not is_expired(cached["timestamp"], ttl_minutes):
        return cached["data"]
    
    # Fetch fresh
    metadata = fetch_document_metadata(doc_token)
    
    # Cache with timestamp
    cache_set(cache_key, {
        "data": metadata,
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    return metadata
```

### Efficient Data Transfer
- **Compression**: Compress large text payloads
- **Incremental updates**: Only send changed content
- **Field selection**: Request only needed fields from APIs

```python
def update_document_efficiently(doc_token, new_content, last_known_version):
    """Update document with minimal data transfer."""
    
    # Compare with last known version
    diff = compute_diff(last_known_version, new_content)
    
    if diff.is_empty():
        return None  # No changes needed
    
    # Only send the diff
    return apply_document_diff(doc_token, diff)
```

## Reliability Patterns

### Idempotent Operations
Design operations to be safely repeatable:

```python
def idempotent_document_create(title, content, folder_token=None):
    """Create document only if it doesn't already exist."""
    
    # Check if document with same title exists
    existing = find_document_by_title(title, folder_token)
    
    if existing:
        log_info(f"Document '{title}' already exists: {existing['token']}")
        return existing['token']
    
    # Create new document
    return create_document(title, content, folder_token)
```

### Transaction-like Behavior
For multi-step operations, implement rollback:

```python
class DocumentMigrationTransaction:
    """Transactional document migration."""
    
    def __init__(self):
        self.operations = []  # Track operations for rollback
    
    def migrate_document(self, source_token, target_folder):
        """Migrate document with rollback support."""
        
        # Step 1: Read source
        content = read_document(source_token)
        self.operations.append(("read", source_token, content))
        
        # Step 2: Create target
        target_token = create_document("Migrated", content, target_folder)
        self.operations.append(("create", target_token, None))
        
        try:
            # Step 3: Update metadata
            update_metadata(target_token, {"source": source_token})
            self.operations.append(("metadata", target_token, None))
            
            # Step 4: Delete source (if desired)
            # delete_document(source_token)
            # self.operations.append(("delete", source_token, None))
            
            return target_token
            
        except Exception as e:
            log_error(f"Migration failed: {e}")
            self.rollback()
            raise
    
    def rollback(self):
        """Undo all operations in reverse order."""
        for op_type, token, data in reversed(self.operations):
            try:
                if op_type == "create":
                    delete_document(token)
                elif op_type == "metadata":
                    # Revert metadata changes
                    pass
                # Note: "read" operations don't need rollback
            except Exception as e:
                log_error(f"Rollback failed for {op_type} {token}: {e}")
```

### Circuit Breakers
Protect against cascading failures:

```python
class FeishuService:
    """Service wrapper with circuit breaker."""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=300
        )
    
    @retry(max_attempts=3, backoff=2)
    @circuit_breaker.protect
    def update_document(self, doc_token, content):
        """Update document with retry and circuit breaker."""
        return feishu_doc_update(doc_token, content)
```

## Security Considerations

### Access Control
- **Least privilege**: Grant minimum necessary permissions
- **Token management**: Rotate access tokens regularly
- **Audit logging**: Log all automation activities

```python
def audit_log(operation, user, resource, details):
    """Log automation activities for audit purposes."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "operation": operation,
        "user": user,
        "resource": resource,
        "details": details,
        "source_ip": get_client_ip()
    }
    
    # Store in secure audit log
    secure_log_store(log_entry)
```

### Data Protection
- **Encryption**: Encrypt sensitive data at rest
- **Masking**: Mask sensitive information in logs
- **Cleanup**: Remove temporary files and tokens

```python
def handle_sensitive_data(document_content):
    """Process document with sensitive data protection."""
    
    # Mask sensitive patterns
    masked_content = mask_sensitive_patterns(document_content)
    
    # Log without sensitive data
    log_info(f"Processed document, size: {len(document_content)} chars")
    
    # Clean up temporary files
    cleanup_temporary_files()
    
    return masked_content
```

## Maintainability

### Configuration Management
Externalize configuration:

```yaml
# config/automation.yaml
feishu:
  app_id: "cli_xxx"
  app_secret: "xxx"
  default_folder: "fldcnXXX"
  
automation:
  batch_size: 10
  retry_attempts: 3
  timeout_seconds: 30
  
templates:
  weekly_report: "templates/weekly_report.md"
  meeting_notes: "templates/meeting_notes.md"
```

```python
import yaml

class Config:
    """Configuration manager."""
    
    def __init__(self, config_path="config/automation.yaml"):
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)
    
    def get(self, key, default=None):
        """Get configuration value with dot notation."""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
```

### Modular Design
Break automation into reusable components:

```python
# components/document_processor.py
class DocumentProcessor:
    """Base class for document processing."""
    
    def process(self, doc_token):
        raise NotImplementedError

# components/template_renderer.py  
class TemplateRenderer:
    """Render templates with data."""
    
    def render(self, template_path, context):
        with open(template_path, 'r') as f:
            template = f.read()
        
        return template.format(**context)

# workflows/weekly_report.py
class WeeklyReportWorkflow:
    """Weekly report automation workflow."""
    
    def __init__(self, data_fetcher, template_renderer, document_creator):
        self.data_fetcher = data_fetcher
        self.template_renderer = template_renderer
        self.document_creator = document_creator
    
    def execute(self, week_date):
        # 1. Fetch data
        data = self.data_fetcher.fetch_week_data(week_date)
        
        # 2. Render template
        content = self.template_renderer.render(
            "templates/weekly_report.md",
            {"data": data, "week": week_date}
        )
        
        # 3. Create document
        return self.document_creator.create(
            f"Weekly Report {week_date}",
            content
        )
```

### Testing Strategy
Implement comprehensive testing:

```python
# tests/test_document_automation.py
import pytest
from unittest.mock import Mock, patch

def test_batch_update():
    """Test batch document updates."""
    
    # Mock Feishu API
    mock_api = Mock()
    mock_api.update_document.return_value = {"success": True}
    
    # Test with mock
    processor = DocumentProcessor(api=mock_api)
    results = processor.batch_update(["doc1", "doc2", "doc3"], "Test content")
    
    assert len(results) == 3
    assert mock_api.update_document.call_count == 3

def test_error_recovery():
    """Test error recovery mechanisms."""
    
    # Mock failing API
    mock_api = Mock()
    mock_api.update_document.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        {"success": True}  # Third attempt succeeds
    ]
    
    processor = DocumentProcessor(api=mock_api)
    
    # Should retry and eventually succeed
    with pytest.raises(Exception):
        processor.update_with_retry("doc1", "Content", max_retries=2)
    
    # With more retries, should succeed
    result = processor.update_with_retry("doc1", "Content", max_retries=3)
    assert result["success"] == True
```

## Monitoring and Observability

### Metrics Collection
Track key metrics:

```python
class MetricsCollector:
    """Collect automation metrics."""
    
    def __init__(self):
        self.metrics = {
            "operations_total": 0,
            "operations_failed": 0,
            "api_calls_total": 0,
            "api_latency_ms": [],
            "documents_processed": 0
        }
    
    def record_operation(self, operation, success, duration_ms):
        """Record operation metrics."""
        self.metrics["operations_total"] += 1
        
        if not success:
            self.metrics["operations_failed"] += 1
        
        self.metrics["api_calls_total"] += 1
        self.metrics["api_latency_ms"].append(duration_ms)
        
        if operation == "document_process":
            self.metrics["documents_processed"] += 1
    
    def get_summary(self):
        """Get metrics summary."""
        latencies = self.metrics["api_latency_ms"]
        
        return {
            "total_operations": self.metrics["operations_total"],
            "failure_rate": (
                self.metrics["operations_failed"] / 
                self.metrics["operations_total"] * 100 
                if self.metrics["operations_total"] > 0 else 0
            ),
            "avg_latency_ms": (
                sum(latencies) / len(latencies) 
                if latencies else 0
            ),
            "documents_processed": self.metrics["documents_processed"]
        }
```

### Health Dashboard
Create a dashboard for monitoring:

```python
def generate_health_dashboard():
    """Generate health dashboard data."""
    
    checks = [
        check_api_connectivity(),
        check_rate_limit_status(),
        check_token_validity(),
        check_storage_health()
    ]
    
    dashboard = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "HEALTHY" if all(c["healthy"] for c in checks) else "UNHEALTHY",
        "checks": checks,
        "metrics": metrics_collector.get_summary()
    }
    
    return dashboard
```

## Documentation and Knowledge Sharing

### Runbook Creation
Document procedures for common tasks:

```markdown
# Runbook: Recovering from API Rate Limiting

## Symptoms
- API calls returning 429 errors
- Automation jobs failing
- "Rate limit exceeded" in logs

## Immediate Actions
1. Check current rate limit status
2. Reduce automation frequency by 50%
3. Implement exponential backoff

## Investigation
1. Review API usage patterns
2. Identify peak usage times
3. Check for runaway automation

## Resolution
1. Adjust batch sizes
2. Implement caching
3. Schedule non-critical jobs off-peak

## Prevention
1. Monitor rate limit usage
2. Set up alerts at 70% threshold
3. Implement circuit breakers
```

### Change Management
Process for making changes:

1. **Test in isolation**: Test changes in a sandbox environment
2. **Canary deployment**: Roll out to small subset first
3. **Monitoring**: Monitor closely after deployment
4. **Rollback plan**: Have a verified rollback procedure

By following these best practices, you'll create Feishu automation that is reliable, maintainable, and scalable.