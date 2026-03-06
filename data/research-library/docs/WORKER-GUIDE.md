# Extraction Worker Guide

## Overview

The extraction worker system provides asynchronous document text extraction with:

- **Multi-threaded worker pool** for parallel processing
- **Persistent queue** with SQLite backing
- **Exponential backoff retry** for transient failures
- **Graceful shutdown** with job preservation
- **Real-time monitoring** via heartbeats and metrics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ExtractionWorker                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │Worker 1 │  │Worker 2 │  │Worker N │  ... (configurable)  │
│  └────┬────┘  └────┬────┘  └────┬────┘                     │
│       │            │            │                           │
│       └────────────┼────────────┘                           │
│                    │                                        │
│              ┌─────▼─────┐                                  │
│              │QueueManager│                                  │
│              └─────┬─────┘                                  │
│                    │                                        │
│              ┌─────▼─────┐                                  │
│              │ SQLite DB │                                  │
│              └───────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from reslib import ResearchDatabase, ExtractionWorker

# Initialize database
db = ResearchDatabase("research.db")

# Create worker pool
worker = ExtractionWorker(db, num_workers=2)

# Start processing
worker.start()

# Add jobs
attachment_id = db.add_attachment(
    filename="paper.pdf",
    path="/path/to/paper.pdf",
    mime_type="application/pdf"
)
job_id = worker.enqueue(attachment_id)

# Check status
status = worker.get_status()
print(f"Queue depth: {status['queue_depth']}")
print(f"Processing: {status['processing']}")

# Graceful shutdown
worker.stop()
```

## Configuration

### Worker Pool Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `num_workers` | 2 | Number of worker threads |
| `max_retries` | 3 | Maximum retry attempts per job |
| `extraction_timeout` | 300 | Extraction timeout in seconds |
| `heartbeat_interval` | 10 | Heartbeat update interval (seconds) |
| `poll_interval` | 1.0 | Queue poll interval when idle (seconds) |

### Example Configuration

```python
worker = ExtractionWorker(
    db,
    num_workers=4,           # More workers for high throughput
    max_retries=5,           # More retries for unreliable network
    extraction_timeout=600,  # 10 min for large documents
    heartbeat_interval=5,    # Faster heartbeat for monitoring
    poll_interval=0.5,       # Faster polling for low latency
)
```

### Recommended Settings by Use Case

**High-throughput batch processing:**
```python
num_workers=8, max_retries=3, poll_interval=0.1
```

**Memory-constrained environment:**
```python
num_workers=1, extraction_timeout=180
```

**Unreliable extractors:**
```python
max_retries=5, extraction_timeout=600
```

## Queue Management

### Job States

```
    ┌──────────┐
    │ PENDING  │◄────────────────┐
    └────┬─────┘                 │
         │ claim()               │ release() / retry_failed()
         ▼                       │
    ┌──────────┐                 │
    │PROCESSING├─────────────────┤
    └────┬─────┘                 │
         │                       │
    ┌────┴────┐                  │
    ▼         ▼                  │
┌────────┐ ┌────────────────┐    │
│COMPLETE│ │ RETRY_PENDING  ├────┘
└────────┘ └───────┬────────┘
                   │ max retries exceeded
                   ▼
              ┌────────┐
              │ FAILED │
              └────────┘
```

### Priority Queue

Jobs are processed by priority (descending), then by creation time (FIFO):

```python
# High priority job (processed first)
worker.enqueue(attachment_id, priority=10)

# Normal priority
worker.enqueue(attachment_id, priority=0)

# Low priority (processed last)
worker.enqueue(attachment_id, priority=-5)
```

### Batch Enqueue

```python
# Enqueue multiple jobs efficiently
attachment_ids = [1, 2, 3, 4, 5]
job_ids = worker.enqueue_batch(attachment_ids, priority=5)
```

## Error Handling

### Error Types

| Error Type | Behavior | Retry |
|------------|----------|-------|
| `timeout` | Extraction exceeded timeout | Yes |
| `corruption` | File corrupted/unreadable | No (permanent) |
| `extractor_missing` | Required extractor not installed | Yes (30s delay) |
| `unsupported` | File type not supported | No (permanent) |
| `unknown` | Unexpected error | Yes |

### Retry Strategy

Exponential backoff with the following delays:

| Attempt | Delay |
|---------|-------|
| 1 | 0.5s |
| 2 | 2.0s |
| 3 | 10.0s |
| 4 | 30.0s |
| 5+ | 60.0s |

For `extractor_missing` errors, minimum delay is 30s.

### Custom Retry Logic

```python
# Manually retry failed jobs
failed = worker.queue.get_failed_jobs()
for job in failed:
    print(f"Job {job.id} failed: {job.error_message}")

# Retry specific job
worker.queue.retry_failed(job_id=123)

# Retry all failed jobs
count = worker.queue.retry_failed()
print(f"Reset {count} jobs for retry")
```

## Graceful Shutdown

```python
# Request shutdown (waits for in-progress jobs)
success = worker.stop(timeout=60)

if success:
    print("All workers stopped cleanly")
else:
    print("Timeout: some jobs may be released")
```

### What Happens on Shutdown

1. Shutdown signal sent to all workers
2. Workers finish their current job (up to timeout)
3. Jobs still in `processing` are released back to `pending`
4. Worker heartbeats updated to `stopped`
5. Resources cleaned up

### Signal Handlers

```python
from reslib.worker import register_signal_handlers

# Install handlers for SIGTERM and SIGINT
register_signal_handlers(worker)

# Now Ctrl+C or kill will gracefully shutdown
worker.start()
```

## Monitoring

### Get Status

```python
status = worker.get_status()

print(f"Running: {status['running']}")
print(f"Queue depth: {status['queue_depth']}")
print(f"Processing: {status['processing']}")
print(f"Workers: {status['num_workers']}")

# Per-worker info
for w in status['workers']:
    print(f"  {w['worker_id']}: {w['status']}, "
          f"completed={w['jobs_completed']}, failed={w['jobs_failed']}")

# Stats
stats = status['stats']
print(f"Throughput: {stats['throughput_per_second']:.2f} jobs/sec")
print(f"Avg extraction: {stats['avg_extraction_time_ms']}ms")
```

### Queue Statistics

```python
queue_stats = worker.queue.get_queue_stats()

print(f"Pending: {queue_stats['pending']}")
print(f"Processing: {queue_stats['processing']}")
print(f"Retry pending: {queue_stats['retry_pending']}")
print(f"Completed (24h): {queue_stats['completed_24h']}")
print(f"Avg time: {queue_stats['avg_extraction_time_ms']}ms")
```

### Worker Heartbeats

Workers update the `worker_heartbeat` table every 10s (configurable).
Use this to detect dead workers:

```sql
SELECT * FROM worker_heartbeat
WHERE last_heartbeat < datetime('now', '-60 seconds')
AND status != 'stopped';
```

### Event Callbacks

```python
def on_started(job, worker_id):
    print(f"[{worker_id}] Started job {job.id}")

def on_completed(job, result):
    print(f"Job {job.id} done: {len(result.text)} chars")

def on_failed(job, error):
    print(f"Job {job.id} failed: {error}")

worker.on("job_started", on_started)
worker.on("job_completed", on_completed)
worker.on("job_failed", on_failed)
```

## Troubleshooting

### Jobs Stuck in Processing

**Symptom:** Jobs remain in `processing` state indefinitely.

**Causes:**
1. Worker crashed without cleanup
2. Extraction timeout not working
3. Database lock preventing updates

**Solutions:**
```python
# Clean up stale jobs (default: 30 min threshold)
count = worker.queue.cleanup_stale_jobs(stale_threshold_minutes=30)
print(f"Cleaned up {count} stale jobs")
```

### Queue Not Draining

**Symptom:** Jobs stay in `pending` despite running workers.

**Check:**
```python
status = worker.get_status()
print(f"Running: {status['running']}")
print(f"Paused: {status['paused']}")
print(f"Active workers: {status['active_workers']}")
```

**Solutions:**
1. Ensure workers are started: `worker.start()`
2. Check if paused: `worker.resume()`
3. Check for extractor errors in logs

### High Failure Rate

**Symptom:** Many jobs failing.

**Diagnosis:**
```python
failed = worker.queue.get_failed_jobs(limit=10)
for job in failed:
    print(f"Job {job.id}: {job.error_message}")
```

**Common causes:**
- Missing extractor dependencies (install `pdfplumber`, `python-docx`)
- Corrupted source files
- Insufficient timeout for large files

### Database Lock Errors

**Symptom:** "database is locked" errors.

**Solutions:**
1. Reduce `num_workers` to decrease contention
2. Increase database timeout:
   ```python
   db = ResearchDatabase("research.db", timeout=60.0)
   ```
3. Ensure WAL mode is enabled (automatic)

### Memory Issues

**Symptom:** Memory usage grows over time.

**Solutions:**
1. Reduce `num_workers`
2. Set extraction timeout to prevent runaway extractions
3. Monitor for leaks in custom extractors

## Database Schema

### Tables

- `attachments` - Document metadata and extracted text
- `extraction_queue` - Job queue with status tracking
- `worker_heartbeat` - Worker health monitoring
- `extraction_metrics` - Performance metrics
- `attachments_fts` - FTS5 full-text search index

### Key Indexes

- `idx_queue_status_created` - Fast queue polling
- `idx_queue_status_retry` - Retry scheduling

## API Reference

### ExtractionWorker

```python
class ExtractionWorker:
    def __init__(self, db, num_workers=2, max_retries=3, ...)
    def start() -> None
    def stop(timeout=60.0) -> bool
    def pause() -> None
    def resume() -> None
    def is_running() -> bool
    def is_paused() -> bool
    def enqueue(attachment_id, priority=0) -> Optional[int]
    def enqueue_batch(attachment_ids, priority=0) -> List[int]
    def get_status() -> Dict
    def get_recent_jobs(limit=20) -> List[Dict]
    def retry_failed_jobs(job_ids=None) -> int
    def on(event, callback) -> None
```

### QueueManager

```python
class QueueManager:
    def enqueue(attachment_id, priority=0, deduplicate=True) -> Optional[int]
    def claim(worker_id) -> Optional[Job]
    def complete(job_id, extraction_time_ms=None, confidence=None) -> bool
    def failed(job_id, error_message, error_type="unknown", max_retries=3) -> bool
    def release(job_id) -> bool
    def cancel(job_id) -> bool
    def get_job(job_id) -> Optional[Job]
    def get_pending_count() -> int
    def get_failed_jobs(limit=100) -> List[Job]
    def retry_failed(job_id=None) -> int
    def cleanup_stale_jobs(stale_threshold_minutes=30) -> int
    def get_queue_stats() -> Dict
```
