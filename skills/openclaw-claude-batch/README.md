# Claude Batch API Skill 🥧

A comprehensive OpenClaw skill for Claude's Batch API — process large volumes of requests asynchronously with **50% cost savings**.

## Features

✅ **Cost Optimization** - 50% discount on all token usage  
✅ **High Throughput** - Handle up to 100,000 requests per batch  
✅ **Fast Processing** - Most batches complete in < 1 hour  
✅ **Full Feature Support** - Vision, tool use, caching, system prompts, multi-turn conversations  
✅ **Flexible Input** - Build requests from CSV, JSON, text, or Python  
✅ **Real-Time Monitoring** - Watch batch progress with automatic polling  
✅ **Result Streaming** - Process results efficiently without loading entire files into memory  

## Use Cases

| Use Case | Benefit |
|----------|---------|
| **Bulk Content Generation** | Summarize 1000s of documents, generate product descriptions |
| **Large-Scale Evaluations** | Test with thousands of test cases efficiently |
| **Content Moderation** | Analyze user-generated content at scale |
| **Data Analysis** | Generate insights for large datasets |
| **Batch Transformations** | Convert, reformat, or enhance data in bulk |

## Requirements

**ANTHROPIC_API_KEY** (Required)
- Your Anthropic API key for Claude Batch API access
- Format: `sk-ant-...`
- Set before using: `export ANTHROPIC_API_KEY="sk-ant-..."`
- Or pass directly to scripts: `anthropic.Anthropic(api_key="sk-ant-...")`

Python 3.8+ with `anthropic >= 0.20.0`

## Quick Start

### 1. Set Up Credentials

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 2. Submit a Batch

```bash
# Build requests from CSV
python scripts/build_batch.py csv data.csv --output requests.jsonl

# Submit the batch
python scripts/batch_runner.py submit requests.jsonl
# Output: Batch ID (msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d)
```

### 2. Monitor Progress

```bash
# Watch real-time progress
python scripts/batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d

# Or check once
python scripts/batch_runner.py status msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d
```

### 3. Retrieve Results

```bash
# Stream results when complete
python scripts/batch_runner.py results msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o results.jsonl
```

## Installation

### Option 1: OpenClaw Skill (Recommended)

Install from clayhub:

```bash
# Install the skill
openclaw skills install clayhub/openclaw-claude-batch

# Verify ANTHROPIC_API_KEY is set
echo $ANTHROPIC_API_KEY
```

### Option 2: Manual Installation

Clone from GitHub:

```bash
git clone https://github.com/kai-tw/openclaw-claude-batch.git
cd openclaw-claude-batch

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Use the scripts
python scripts/batch_runner.py submit requests.jsonl
```

### Option 3: Copy to OpenClaw Workspace

```bash
cp -r openclaw-claude-batch ~/.openclaw/workspace/skills/claude-batch
```

## Scripts

### batch_runner.py

Main CLI for all batch operations.

```bash
# Submit a batch
python scripts/batch_runner.py submit requests.jsonl

# Check status
python scripts/batch_runner.py status msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d

# List all batches
python scripts/batch_runner.py list --limit 50

# Cancel a batch
python scripts/batch_runner.py cancel msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d

# Stream results
python scripts/batch_runner.py results msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o results.jsonl
```

### batch_monitor.py

Real-time batch monitoring with adaptive polling.

```bash
# Monitor with default 60s interval
python scripts/batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d

# Custom interval
python scripts/batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d --interval 30

# Log to file
python scripts/batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o monitor.jsonl
```

### build_batch.py

Build batch request files from various data sources.

```bash
# From CSV
python scripts/build_batch.py csv data.csv --output requests.jsonl
python scripts/build_batch.py csv data.csv --prompt-column content

# From text (line by line)
python scripts/build_batch.py text documents.txt

# From text (paragraph by paragraph)
python scripts/build_batch.py text documents.txt --split-by paragraph

# From JSON
python scripts/build_batch.py json items.json
python scripts/build_batch.py json items.json --prompt-field description

# From custom Python script
python scripts/build_batch.py custom my_builder.py
```

## Documentation

- **[SKILL.md](SKILL.md)** - Overview, key concepts, pricing, use cases
- **[references/api-overview.md](references/api-overview.md)** - Complete API reference
- **[references/best-practices.md](references/best-practices.md)** - Production patterns, optimization strategies, troubleshooting

## Pricing

All usage is charged at **50% of standard prices**:

| Model | Batch Input | Batch Output |
|-------|------------|----------|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |

**Plus 25% additional discount** when combined with prompt caching.

### Cost Comparison Example

Summarizing 10,000 documents (2,000 tokens input, 500 tokens output):

```
Standard API:  $135.00
Batch API:     $67.50  ✅ (50% savings)
+ Caching:     $51.75  ✅ (62% total savings)
```

## Examples

### Example 1: Bulk Content Summarization

```python
import json

# 1. Build requests
requests = []
documents = ["doc1.txt", "doc2.txt", ...]

for doc in documents:
    with open(doc) as f:
        content = f.read()
    
    requests.append({
        "custom_id": f"summary-{doc}",
        "params": {
            "model": "claude-opus-4-6",
            "max_tokens": 500,
            "messages": [{
                "role": "user",
                "content": f"Summarize this document:\n\n{content}"
            }]
        }
    })

# Save to JSONL
with open("batch_requests.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# 2. Submit batch
# python batch_runner.py submit batch_requests.jsonl

# 3. Monitor
# python batch_monitor.py msgbatch_...

# 4. Process results
# python batch_runner.py results msgbatch_... -o summaries.jsonl
```

### Example 2: Data Analysis at Scale

```python
# Build batch for analyzing product reviews
requests = []
reviews = [...]  # Load your reviews

for review in reviews:
    requests.append({
        "custom_id": f"review-{review['id']}",
        "params": {
            "model": "claude-opus-4-6",
            "max_tokens": 200,
            "system": "You are a product review analyst. Extract: sentiment, key topics, actionable feedback.",
            "messages": [{
                "role": "user",
                "content": f"Analyze this review:\n\n{review['text']}"
            }]
        }
    })
```

### Example 3: Custom Request Builder

Create `my_builder.py`:

```python
def build_requests():
    """Custom logic to build batch requests"""
    import csv
    
    requests = []
    with open("products.csv") as f:
        for row in csv.DictReader(f):
            requests.append({
                "custom_id": f"product-{row['id']}",
                "params": {
                    "model": "claude-opus-4-6",
                    "max_tokens": 300,
                    "messages": [{
                        "role": "user",
                        "content": f"Create a marketing description for: {row['name']} - {row['features']}"
                    }]
                }
            })
    
    return requests
```

Then build with:

```bash
python scripts/build_batch.py custom my_builder.py
```

## Requirements

- Python 3.8+
- anthropic >= 0.20.0
- OpenClaw (optional, for skill integration)

## API Key Setup

The `ANTHROPIC_API_KEY` environment variable must be set before using any scripts. You can:

1. **Set globally** (recommended):
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

2. **Pass in code**:
   ```python
   import anthropic
   client = anthropic.Anthropic(api_key="sk-ant-...")
   ```

3. **Create `.env` file** (for local testing):
   ```bash
   echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
   export $(cat .env | xargs)
   ```

## Batch Limits

- **Max size**: 100,000 requests OR 256 MB
- **Processing**: Typically < 1 hour, max 24 hours
- **Result availability**: 29 days after creation
- **Order**: Results returned in any order (use `custom_id` for matching)

## Common Patterns

### Retry Failed Requests

```python
import anthropic

client = anthropic.Anthropic()

# Collect failed requests
failed = []
for result in client.messages.batches.results(batch_id):
    if result.result.type == "errored":
        error_type = result.result.error.type
        if error_type in ["rate_limit_error", "api_error"]:
            # Retry transient errors
            failed.append(original_requests[result.custom_id])

# Resubmit
if failed:
    retry_batch = client.messages.batches.create(requests=failed)
    print(f"Retrying {len(failed)} requests: {retry_batch.id}")
```

### Monitor Multiple Batches

```bash
for batch_id in msgbatch_1 msgbatch_2 msgbatch_3; do
    python scripts/batch_monitor.py $batch_id &
done
wait
```

### Export Results to Database

```python
import json
import sqlite3

conn = sqlite3.connect("results.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS batch_results (
    custom_id TEXT PRIMARY KEY,
    status TEXT,
    response TEXT,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

for result in client.messages.batches.results(batch_id):
    if result.result.type == "succeeded":
        cursor.execute(
            "INSERT INTO batch_results VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (result.custom_id, "success", 
             result.result.message.content[0].text, None)
        )
    else:
        cursor.execute(
            "INSERT INTO batch_results VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (result.custom_id, "error", None, str(result.result.error))
        )

conn.commit()
```

## Troubleshooting

**Batch not found?**
- Check the batch ID is correct
- Batches are scoped to workspace/API key
- Check 24-hour expiration

**High error rate?**
- Validate request format with Messages API first
- Check for invalid `custom_id` (must be unique)
- Ensure `max_tokens` < model limits

**Results empty?**
- Batch must have `processing_status == "ended"`
- Use `batch_monitor.py` to wait for completion
- Results available for 29 days after creation

**Results out of order?**
- This is normal and expected
- Always use `custom_id` to match results to requests
- Never rely on ordering

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Claude Documentation](https://claude.ai/docs/en/build-with-claude/batch-processing)
- 🐙 [GitHub Issues](https://github.com/kai-wu/claude-batch-api-skill/issues)
- 💬 [OpenClaw Discord](https://discord.com/invite/clawd)

## Changelog

### v1.0.0 (2026-02-25)
- Initial release
- `batch_runner.py` - Submit, monitor, and retrieve results
- `batch_monitor.py` - Real-time progress monitoring
- `build_batch.py` - Build requests from CSV, JSON, text, and Python
- Complete API reference and best practices documentation

---

Built with ❤️ for the OpenClaw community. 🥧
