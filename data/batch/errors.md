# Batch Error Handling

## Retry Logic

```python
def process_with_retry(item, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return process(item)
        except RetryableError as e:
            if attempt < max_attempts - 1:
                delay = 2 ** attempt  # 1s, 2s, 4s
                log(f"Retry {attempt+1}/{max_attempts} in {delay}s: {e}")
                sleep(delay)
            else:
                raise MaxRetriesExceeded(item, e)
```

## Error Categories

| Type | Examples | Action |
|------|----------|--------|
| **Retryable** | Timeout, 429, 503, network | Retry with backoff |
| **Skippable** | Bad format, missing field | Log, skip, continue |
| **Fatal** | Auth failed, disk full | Abort entire batch |

## Partial Failure Recovery

After batch with failures:

```
Failed items saved to: /tmp/batch_failures.json

Options:
1. Retry failed only: batch retry /tmp/batch_failures.json
2. Manual fix + retry: edit failures, then retry
3. Accept partial: merge successful results, document gaps
```

## Common Issues

| Problem | Cause | Prevention |
|---------|-------|------------|
| All items fail | Wrong config, auth | Dry run first |
| Random failures | Rate limits | Add throttling |
| Slow processing | Sequential when could parallel | Check dependencies |
| Memory crash | Too many items in memory | Use streaming/chunking |
| Lost progress | No checkpointing | Checkpoint every 10-50 items |

## Rollback

For destructive operations (delete, modify):

```
1. Before batch: snapshot current state
2. During: log each change with undo info
3. On abort: offer rollback

Example undo log:
{"action": "rename", "from": "a.txt", "to": "b.txt", "undo": "rename b.txt a.txt"}
{"action": "delete", "path": "c.txt", "backup": "/tmp/backup/c.txt"}
```

## Alerting

For long batches (>10 min):
- Send progress update every 5 min
- Alert immediately on >10% failure rate
- Final summary when complete
