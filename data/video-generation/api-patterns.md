# API Patterns (All Providers)

Common patterns for video generation APIs.

## Async Generation

All video APIs use async patterns:
1. Submit generation request → get job ID
2. Poll status endpoint until `completed`
3. Download from signed URL

## Polling Example

```python
import time
import requests

def wait_for_video(job_id, api_key, max_wait=300):
    for _ in range(max_wait // 5):
        resp = requests.get(
            f"https://api.provider.com/generations/{job_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        status = resp.json()
        if status["state"] == "completed":
            return status["assets"]["video"]
        if status["state"] == "failed":
            raise Exception(status["failure_reason"])
        time.sleep(5)
    raise TimeoutError("Generation timed out")
```

## Exponential Backoff

```python
wait_times = [5, 10, 20, 40, 60]  # seconds
for wait in wait_times:
    status = check_status(job_id)
    if status == "completed":
        break
    time.sleep(wait)
```

## Cache Results

- Signed URLs expire (typically 24h)
- Download and store videos immediately after generation
- Store generation IDs for retrieval if re-download needed

## Comparison Table

| Provider | Max Duration | Text-to-Video | Image-to-Video | Approx. Cost/sec |
|----------|--------------|---------------|----------------|------------------|
| Runway Gen-4.5 | 10s | ✅ | ✅ | $0.05 |
| Luma Ray-2 | 5s | ✅ | ✅ | $0.032 |
| Kling V2 | 10s | ✅ | ✅ | $0.10 |
| Pika | 3s | ✅ | ✅ | $0.05 |
| SVD (local) | ~4s | ❌ | ✅ | Free |
| Replicate | Varies | Varies | ✅ | $0.02-0.10 |
