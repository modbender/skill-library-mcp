# Batch Strategies

## Decision Matrix

| Items | Dependencies | Rate Limits | Strategy |
|-------|--------------|-------------|----------|
| <10 | Any | Any | Sequential |
| 10-100 | None | None | Parallel (5 workers) |
| 10-100 | None | Yes | Sequential + throttle |
| 10-100 | Yes | Any | Sequential |
| >100 | None | None | Chunked parallel |
| >100 | Any | Any | Chunked sequential |

## Sequential

```
for item in items:
    process(item)
    report_progress()
```

**Use when:**
- Order matters (item N depends on N-1)
- Rate limits exist (API calls)
- Need clear progress visibility
- Debugging/first run

## Parallel

```
workers = 5
queue = items
results = parallel_map(process, queue, workers)
```

**Use when:**
- Items fully independent
- I/O bound (network, disk)
- Speed critical
- No rate limits

**Limits:**
- Max 5 concurrent sub-agents (avoid overload)
- Max 10 concurrent API calls (respect rate limits)

## Chunked

```
chunk_size = 50
for chunk in split(items, chunk_size):
    process_parallel(chunk)
    save_checkpoint()
    report_progress()
```

**Use when:**
- >100 items
- Need checkpointing
- Memory constraints
- Mix of speed and safety

## Throttling

For rate-limited APIs:
```
requests_per_minute = 60
delay = 60 / requests_per_minute  # 1 second

for item in items:
    process(item)
    sleep(delay)
```

## Checkpointing

Save state every N items:
```json
{
  "batch_id": "abc123",
  "total": 200,
  "processed": 50,
  "last_item_id": "item_50",
  "results_path": "/tmp/batch_abc123_partial.json",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

To resume: read checkpoint, skip processed, continue from last_item_id.
