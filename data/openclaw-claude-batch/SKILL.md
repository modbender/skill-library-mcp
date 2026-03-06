---
name: openclaw-claude-batch
description: "Claude Batch API for processing large volumes of requests asynchronously with 50% cost savings. Use for bulk content generation, data analysis, content moderation, batch evaluations, or large-scale testing where immediate responses are not required."
metadata:
  openclaw:
    emoji: "🔄"
    requires:
      env: ["ANTHROPIC_API_KEY"]
      python: ">=3.8"
    credentials:
      - name: ANTHROPIC_API_KEY
        description: "Anthropic API key for Claude Batch API access (sk-ant-...)"
        isRequired: true
---

# Claude Batch API Skill

Process large volumes of Claude API requests asynchronously with 50% cost savings.

## Quick Start

### 1. Prepare Requests (JSONL Format)

Create a request file where each line is a complete request:

```python
import json

requests = [
    {
        "custom_id": "task-1",
        "params": {
            "model": "claude-opus-4-6",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "Summarize this: ..."}
            ]
        }
    },
    {
        "custom_id": "task-2",
        "params": {
            "model": "claude-opus-4-6",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "Analyze this: ..."}
            ]
        }
    }
]

with open("batch_requests.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")
```

### 2. Submit Batch

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

# Read requests from file
with open("batch_requests.jsonl") as f:
    requests = [json.loads(line) for line in f]

# Create batch
batch = client.messages.batches.create(requests=requests)
print(f"Batch created: {batch.id}")
print(f"Status: {batch.processing_status}")
```

### 3. Monitor & Retrieve Results

```python
import time

# Poll for completion
while True:
    batch = client.messages.batches.retrieve(batch.id)
    print(f"Status: {batch.processing_status}")
    if batch.processing_status == "ended":
        break
    time.sleep(60)

# Stream results (memory-efficient)
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(f"{result.custom_id}: SUCCESS")
        print(result.result.message.content[0].text)
    elif result.result.type == "errored":
        print(f"{result.custom_id}: ERROR")
        print(result.result.error)
```

## Key Concepts

### Batch Limits
- Max 100,000 requests per batch OR 256 MB
- Processing: typically < 1 hour, max 24 hours
- Results available for 29 days after creation
- Order of results not guaranteed (use `custom_id` for matching)

### Cost Savings
- **50% discount** on all token usage
- Input tokens, output tokens, and cache usage all discounted
- Cache hits work on best-effort basis (30-98% typical)

### Supported Features
✅ Vision, tool use, system messages, multi-turn conversations, prompt caching, all beta features
❌ Streaming (results polled instead)

### Models
All active Claude models supported (Opus 4.6, Sonnet 4.6, Haiku 4.5, etc.)

## Use Cases

| Use Case | Why Batch API |
|----------|----------------|
| **Bulk content generation** | 1000s of product descriptions, summaries |
| **Large-scale evaluations** | Testing 1000s of test cases |
| **Content moderation** | Analyzing user-generated content at scale |
| **Data analysis** | Generating insights for large datasets |
| **Bulk transformations** | Converting, reformatting, or enhancing data |

## Workflow

1. **Prepare** - Build request list with unique `custom_id` for each
2. **Submit** - Create batch via API
3. **Monitor** - Poll status periodically (check every 60-120 seconds)
4. **Process** - Stream results efficiently from `results_url`
5. **Handle Failures** - Retry errored requests or proceed based on success rate

## API Reference

For complete API documentation, request counts, error handling, and advanced features (prompt caching, cancellation), see `references/api-overview.md`.

For optimization strategies, troubleshooting, and production patterns, see `references/best-practices.md`.

## Scripts

Ready-to-use Python scripts for common operations:

- **scripts/batch_runner.py** - Submit, monitor, cancel, and retrieve batch results
- **scripts/batch_monitor.py** - Real-time batch progress monitoring with adaptive polling
- **scripts/build_batch.py** - Build batch requests from CSV, JSON, text, or Python scripts

## Pricing Example

Submitting 100,000 requests at ~1,000 tokens each:
- Standard API: $0.003 per request = $300
- Batch API: $0.0015 per request = $150 ✅ (50% savings)

Plus 1-hour cache: Additional 25% savings on cached content.
