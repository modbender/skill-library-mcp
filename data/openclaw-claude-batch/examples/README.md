# Claude Batch API Examples

Complete working examples demonstrating how to use the Batch API for real-world tasks.

## Prerequisites

```bash
# Install dependencies
pip install -r ../requirements.txt

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Example 1: Document Summarization

Summarize multiple documents in bulk.

```bash
# Build requests from sample documents
python example_1_summarization.py build
# Creates: batch_requests_summary.jsonl

# Submit batch
python ../scripts/batch_runner.py submit batch_requests_summary.jsonl
# Returns: Batch ID (msgbatch_...)

# Monitor progress
python ../scripts/batch_monitor.py msgbatch_...

# Get results when complete
python ../scripts/batch_runner.py results msgbatch_... -o summaries.jsonl
```

**What it does:**
- Reads 5 sample documents
- Creates a summarization request for each
- Submits as a batch
- Shows how to handle results

**Cost savings:**
- 5 documents × ~500 tokens output = 2,500 tokens
- Standard API: $0.04 | Batch API: $0.02 (50% savings)

## Example 2: Marketing Copy Generation

Generate marketing descriptions for products from CSV data.

```bash
# Build batch from sample products
python example_2_marketing.py build
# Creates: batch_requests_marketing.jsonl

# Submit batch
python ../scripts/batch_runner.py submit batch_requests_marketing.jsonl

# Monitor
python ../scripts/batch_monitor.py msgbatch_...

# Process results
python example_2_marketing.py results msgbatch_... marketing_results.json
```

**What it does:**
- Reads product data from CSV
- Generates marketing copy for 10 products
- Processes and saves results to JSON
- Shows CSV → batch workflow

**Cost savings:**
- 10 products × ~300 tokens output = 3,000 tokens
- Standard API: $0.045 | Batch API: $0.0225 (50% savings)

## Step-by-Step Workflow

### Step 1: Build Requests

Choose one:

```bash
# From text file
python ../scripts/build_batch.py text sample_documents.txt

# From CSV
python ../scripts/build_batch.py csv sample_products.csv

# Custom Python script
python ../scripts/build_batch.py custom my_builder.py

# Or write your own
python example_1_summarization.py build
```

### Step 2: Submit Batch

```bash
python ../scripts/batch_runner.py submit batch_requests.jsonl
# Output: Batch ID msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d
```

### Step 3: Monitor Progress

```bash
# Real-time monitoring
python ../scripts/batch_monitor.py msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d

# Or check status once
python ../scripts/batch_runner.py status msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d
```

### Step 4: Retrieve Results

When batch is complete:

```bash
# Stream results
python ../scripts/batch_runner.py results msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d

# Save to file
python ../scripts/batch_runner.py results msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d -o results.jsonl
```

### Step 5: Process Results

```python
import json

with open("results.jsonl") as f:
    for line in f:
        result = json.loads(line)
        if result.get("status") == "succeeded":
            print(f"{result['custom_id']}: {result['response']}")
        else:
            print(f"{result['custom_id']}: ERROR")
```

## Sample Files

- **sample_documents.txt** - 5 tech-related documents for summarization
- **sample_products.csv** - 10 products for marketing copy generation

## Creating Your Own Examples

### Example Template

```python
#!/usr/bin/env python3
"""
Your Example: Description

Usage:
    python your_example.py build
    python your_example.py submit
"""

import json

def build_batch():
    """Build your custom batch"""
    requests = []
    
    # Load your data
    # Create requests
    # Save to JSONL
    
    with open("batch_requests_custom.jsonl", "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")
    
    print(f"Created {len(requests)} requests")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    if command == "build":
        build_batch()

if __name__ == "__main__":
    main()
```

## Common Patterns

### Pattern 1: Load from CSV

```python
import csv

requests = []
with open("data.csv") as f:
    for row in csv.DictReader(f):
        requests.append({
            "custom_id": f"row-{row['id']}",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": f"Process: {row['content']}"
                }]
            }
        })
```

### Pattern 2: Load from Database

```python
import sqlite3

requests = []
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

for row in cursor.execute("SELECT id, content FROM items"):
    requests.append({
        "custom_id": f"db-{row[0]}",
        "params": {
            "model": "claude-opus-4-6",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": row[1]
            }]
        }
    })
```

### Pattern 3: Process Results to Database

```python
import sqlite3
import anthropic

client = anthropic.Anthropic()
conn = sqlite3.connect("results.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS batch_results (
    custom_id TEXT,
    response TEXT,
    status TEXT
)
""")

for result in client.messages.batches.results(batch_id):
    if result.result.type == "succeeded":
        cursor.execute(
            "INSERT INTO batch_results VALUES (?, ?, ?)",
            (result.custom_id,
             result.result.message.content[0].text,
             "success")
        )

conn.commit()
```

### Pattern 4: Export to CSV

```python
import csv
import json
import anthropic

client = anthropic.Anthropic()

with open("results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["custom_id", "response", "tokens"])
    
    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            writer.writerow([
                result.custom_id,
                result.result.message.content[0].text,
                result.result.message.usage.output_tokens
            ])
```

## Tips & Tricks

### Batch Size Strategy

- **Small batches (< 1,000)**: Fast feedback, easier debugging
- **Medium batches (1-10,000)**: Good balance
- **Large batches (> 50,000)**: Maximum cost savings

**Recommendation:** Start with 100-1,000 requests to test, then scale up.

### Cost Optimization

```python
# Use Haiku for simple tasks (cheaper)
# Use Opus for complex reasoning

# Simple summarization
"model": "claude-haiku-4-5",  # $0.50 / MTok input

# Complex analysis
"model": "claude-opus-4-6",   # $2.50 / MTok input
```

### Error Handling

```python
for result in client.messages.batches.results(batch_id):
    if result.result.type == "errored":
        error_type = result.result.error.type
        
        if error_type == "invalid_request_error":
            # Fix request format
            print(f"Fix request: {result.custom_id}")
        elif error_type in ["rate_limit_error", "api_error"]:
            # Safe to retry
            print(f"Retry: {result.custom_id}")
```

### Monitoring Multiple Batches

```bash
# Submit multiple batches
BATCH_1=$(python ../scripts/batch_runner.py submit requests_1.jsonl | grep "ID:")
BATCH_2=$(python ../scripts/batch_runner.py submit requests_2.jsonl | grep "ID:")

# Monitor in parallel
python ../scripts/batch_monitor.py $BATCH_1 &
python ../scripts/batch_monitor.py $BATCH_2 &
wait
```

## Performance Metrics

### Example 1: Document Summarization
- Documents: 5
- Avg input: 200 tokens
- Avg output: 100 tokens
- Processing time: ~5-10 minutes
- Cost: ~$0.002 (50% savings vs standard)

### Example 2: Marketing Copy
- Products: 10
- Avg input: 150 tokens
- Avg output: 300 tokens
- Processing time: ~10-15 minutes
- Cost: ~$0.0045 (50% savings vs standard)

## Troubleshooting

**Batch not processing?**
- Check API key is correct
- Verify request format (test with Messages API first)
- Check custom_id values are unique

**Results empty?**
- Batch must be in "ended" status
- Results available for 29 days only
- Use `batch_runner.py status` to verify completion

**High error rate?**
- Validate requests with Messages API first
- Check model names (use "claude-opus-4-6" format)
- Verify max_tokens is appropriate

## Next Steps

1. Try Example 1 or 2
2. Adapt the pattern to your data
3. Test with small batch first (< 100 requests)
4. Monitor the batch
5. Process results
6. Scale up to larger batches

Good luck! 🚀
