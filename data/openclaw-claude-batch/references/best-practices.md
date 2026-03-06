# Claude Batch API Best Practices

Production-ready patterns and optimization strategies.

## Request Design

### Meaningful custom_id Values

Use descriptive IDs for easy debugging:

```python
# ❌ Bad
custom_id = "1", "2", "3"

# ✅ Good
custom_id = "user-123-summary", "doc-456-analysis", "batch-789-qa"
custom_id = f"invoice-{invoice_id}-extraction"
```

Benefits: Easier to track which requests succeeded/failed in results.

### Dry-run with Messages API

Always test your request shape first:

```python
# Test single request before batching
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Test content"}]
)
# Verify response structure...

# Then batch identical requests
```

This catches validation errors early before submitting large batches.

## Batch Sizing Strategy

### Optimal Batch Size

- **Small batches (< 1,000 requests):** Fast processing, easier debugging
- **Medium batches (1,000 - 10,000):** Balance speed and efficiency
- **Large batches (> 50,000):** Maximize cost savings, but harder to debug

**Recommendation:** Start with 1,000-5,000 request batches until confident.

### Breaking Up Large Workloads

```python
# For 100,000 requests, split into 10 batches of 10,000
total_requests = 100000
batch_size = 10000

for i in range(0, total_requests, batch_size):
    batch_requests = all_requests[i:i+batch_size]
    batch = client.messages.batches.create(requests=batch_requests)
    batch_ids.append(batch.id)

# Monitor all batches in parallel
for batch_id in batch_ids:
    monitor_batch(batch_id)
```

Benefits: Parallel processing, easier failure isolation, simpler recovery.

## Cost Optimization

### Maximum Savings Strategy

1. **Use Batch API** (50% discount)
2. **Add prompt caching** (25% additional discount on cached tokens)
3. **Use Haiku 4.5** for simple tasks ($0.50 input vs $1.50 for Sonnet)

**Total possible savings:** ~60% vs. standard pricing

### Caching for Batch

```python
# Shared context for multiple requests
shared_docs = "Product database with 10,000 items..."

requests = []
for query in queries:
    requests.append({
        "custom_id": f"query-{query}",
        "params": {
            "model": "claude-opus-4-6",
            "max_tokens": 1024,
            "system": [
                {"type": "text", "text": "You are a product expert..."},
                {
                    "type": "text",
                    "text": shared_docs,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            "messages": [{"role": "user", "content": query}]
        }
    })
```

**Cache hit expectations in batches:** 30-98% (best-effort)

## Monitoring Strategy

### Polling Intervals

```python
import time

elapsed = 0
start = time.time()

while True:
    batch = client.messages.batches.retrieve(batch_id)
    elapsed = time.time() - start
    
    if batch.processing_status == "ended":
        print(f"Completed in {elapsed:.1f}s")
        break
    
    # Adaptive polling: increase interval over time
    if elapsed < 300:      # First 5 minutes: check every 10s
        interval = 10
    elif elapsed < 3600:   # First hour: check every 60s
        interval = 60
    else:                  # After 1 hour: check every 300s
        interval = 300
    
    print(f"Status: {batch.processing_status} | "
          f"Succeeded: {batch.request_counts.succeeded} | "
          f"Processing: {batch.request_counts.processing}")
    
    time.sleep(interval)
```

### Logging Pattern

```python
import json
from datetime import datetime

def log_batch_event(batch_id, event_type, data):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "batch_id": batch_id,
        "event": event_type,
        "data": data
    }
    with open(f"batch_{batch_id}.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Usage
log_batch_event(batch_id, "created", {"status": "in_progress"})
log_batch_event(batch_id, "update", {"succeeded": 100, "processing": 50})
log_batch_event(batch_id, "completed", {"succeeded": 140, "errored": 10})
```

## Result Processing

### Streaming Results (Memory-Efficient)

```python
# ✅ Good: Stream results one at a time
succeeded_count = 0
error_count = 0

for result in client.messages.batches.results(batch_id):
    if result.result.type == "succeeded":
        process_success(result)
        succeeded_count += 1
    elif result.result.type == "errored":
        process_error(result)
        error_count += 1

print(f"Processed {succeeded_count} successes, {error_count} errors")
```

### Batch Download (High Memory Usage)

```python
# ❌ Avoid for large batches
results_url = batch.results_url
response = requests.get(results_url, headers={...})
all_results = response.text.split('\n')  # Entire file in memory!
```

### Processing Patterns

**Pattern 1: Save to Database**

```python
for result in client.messages.batches.results(batch_id):
    if result.result.type == "succeeded":
        db.save({
            "custom_id": result.custom_id,
            "response": result.result.message.content[0].text,
            "tokens": result.result.message.usage.output_tokens,
            "created_at": datetime.now()
        })
```

**Pattern 2: Export to File**

```python
with open(f"results_{batch_id}.jsonl", "w") as out:
    for result in client.messages.batches.results(batch_id):
        out.write(json.dumps({
            "id": result.custom_id,
            "status": result.result.type,
            "response": result.result.message.content[0].text 
                        if result.result.type == "succeeded" else None,
            "error": str(result.result.error) 
                     if result.result.type == "errored" else None
        }) + "\n")
```

**Pattern 3: Callback Processing**

```python
def process_result(result):
    if result.result.type == "succeeded":
        # Update dashboard
        # Send webhook
        # Log success
        pass
    elif result.result.type == "errored":
        # Determine if retryable
        if "rate_limit" in str(result.result.error):
            # Queue for retry
            pass
        else:
            # Log permanent failure
            pass

for result in client.messages.batches.results(batch_id):
    process_result(result)
```

## Error Handling

### Retry Strategy

```python
def should_retry(error_type):
    # Permanent errors
    if error_type == "invalid_request_error":
        return False  # Fix request body first
    
    # Transient errors - can retry
    if error_type in ["rate_limit_error", "api_error"]:
        return True
    
    return False

# Collect failed requests
failed_requests = []
for result in client.messages.batches.results(batch_id):
    if result.result.type == "errored":
        if should_retry(result.result.error.type):
            failed_requests.append(original_requests[result.custom_id])

# Resubmit failed batch
if failed_requests:
    retry_batch = client.messages.batches.create(requests=failed_requests)
    print(f"Submitted {len(failed_requests)} for retry: {retry_batch.id}")
```

### Error Classification

| Error Type | Cause | Action |
|-----------|-------|--------|
| `invalid_request_error` | Malformed request | Fix & resubmit |
| `authentication_error` | Bad API key | Fix credentials |
| `rate_limit_error` | Too many requests | Wait & retry later |
| `api_error` | Server error | Retry (usually succeeds) |

## Production Checklist

- [ ] Dry-run requests with Messages API first
- [ ] Use meaningful custom_id values
- [ ] Implement error categorization
- [ ] Stream results instead of downloading all at once
- [ ] Log batch events for auditing
- [ ] Handle expired and canceled results gracefully
- [ ] Test with small batch before large batch
- [ ] Monitor processing status with adaptive polling
- [ ] Implement retry logic for transient errors
- [ ] Set up alerting for high error rates (>10%)
- [ ] Track costs per batch
- [ ] Document SLA expectations (typically < 1 hour)

## Performance Metrics

### Throughput Example

Submitting 100,000 requests:
- **Time to submit:** ~10-30 seconds
- **Processing time:** 10 minutes to 1 hour typical
- **Result download:** 2-5 seconds per 10,000 results
- **Total end-to-end:** ~15 minutes to 1 hour

### Cost Example

Summarizing 10,000 documents (2,000 tokens input, 500 tokens output):

```
Standard API:
  Input:  10,000 × 2,000 × $0.003/1K = $60
  Output: 10,000 × 500 × $0.015/1K = $75
  Total: $135

Batch API:
  Input:  10,000 × 2,000 × $0.0015/1K = $30
  Output: 10,000 × 500 × $0.0075/1K = $37.50
  Total: $67.50 (50% savings)

With 1-hour cache (70% hit rate):
  Cached input: 7,000 × 2,000 × $0.000375/1K = $5.25
  Non-cached: 3,000 × 2,000 × $0.0015/1K = $9
  Output: $37.50
  Total: $51.75 (62% savings vs standard)
```

## Avoiding Common Pitfalls

### ❌ Assuming Result Order

```python
# Wrong - results may be out of order
for i, result in enumerate(results):
    original_request = requests[i]  # Wrong!
```

### ✅ Use custom_id for Matching

```python
# Correct - match by custom_id
for result in results:
    original_request = request_map[result.custom_id]
```

### ❌ Downloading Entire Results

```python
# Wrong for large batches - loads entire file in memory
all_results = requests.get(results_url).text.split('\n')
```

### ✅ Stream Results

```python
# Correct - memory efficient
for result in client.messages.batches.results(batch_id):
    process(result)
```

### ❌ Waiting for Instant Results

```python
# Wrong - no results until batch ends
batch = client.messages.batches.create(requests=requests)
results = client.messages.batches.results(batch.id)  # Empty!
```

### ✅ Poll for Completion

```python
# Correct - poll until batch ends
batch = client.messages.batches.create(requests=requests)
while batch.processing_status != "ended":
    batch = client.messages.batches.retrieve(batch.id)
    time.sleep(60)
results = client.messages.batches.results(batch.id)  # Now ready
```
