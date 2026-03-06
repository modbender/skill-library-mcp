---
name: huggingface-trends
description: Monitor and fetch trending models from Hugging Face with support for filtering by task, library, and popularity metrics. Use when users want to check trending AI models, compare model popularity, or explore popular models by task or library. Supports export to JSON and formatted output.
---

# Hugging Face Trending Models

## Quick Start

Fetch the top trending models:

```bash
scripts/hf_trends.py -n 10 -p http://172.28.96.1:10808
```

## Core Features

### Fetch Trending Models

Basic usage:

```bash
# Get top 10 trending models
scripts/hf_trends.py -n 10 -p http://172.28.96.1:10808

# Get top 5 most liked models
scripts/hf_trends.py -n 5 -s likes -p http://172.28.96.1:10808

# Get most downloaded models
scripts/hf_trends.py -n 10 -s downloads -p http://172.28.96.1:10808
```

### Filter by Task

Filter models by specific AI tasks:

```bash
# Text generation models
scripts/hf_trends.py -n 10 -t text-generation -p http://172.28.96.1:10808

# Image classification models
scripts/hf_trends.py -n 10 -t image-classification -p http://172.28.96.1:10808

# Translation models
scripts/hf_trends.py -n 10 -t translation -p http://172.28.96.1:10808
```

Common task filters:
- `text-generation` - Large language models
- `image-classification` - Vision models
- `image-to-text` - Multimodal models
- `translation` - Machine translation
- `summarization` - Text summarization
- `question-answering` - QA models

### Filter by Library

Filter by ML framework:

```bash
# PyTorch models only
scripts/hf_trends.py -n 10 -l pytorch -p http://172.28.96.1:10808

# TensorFlow models only
scripts/hf_trends.py -n 10 -l tensorflow -p http://172.28.96.1:10808

# JAX models
scripts/hf_trends.py -n 10 -l jax -p http://172.28.96.1:10808
```

### Export to JSON

Save results for further analysis:

```bash
# Export to JSON file
scripts/hf_trends.py -n 10 -j trending_models.json -p http://172.28.96.1:10808

# Export with specific filters
scripts/hf_trends.py -n 20 -t text-generation -j text_models.json -p http://172.28.96.1:10808
```

### Proxy Configuration

The script requires an HTTP proxy to access Hugging Face API (network restrictions).

Use the `-p` flag:

```bash
scripts/hf_trends.py -p http://172.28.96.1:10808
```

For most WSL2 environments with v2rayN:
- Proxy URL: `http://172.28.96.1:10808`
- Or use dynamic IP: `http://$(ip route show | grep default | awk '{print $3}'):10808`

## Command-Line Options

| Flag | Long Form | Description | Default |
|------|-----------|-------------|---------|
| `-n` | `--limit` | Number of models to fetch | 10 |
| `-s` | `--sort` | Sort by: trending, likes, downloads, created | trending |
| `-t` | `--task` | Filter by task/pipeline | None |
| `-l` | `--library` | Filter by library (pytorch, tensorflow, jax) | None |
| `-j` | `--json` | Export results to JSON file | None |
| `-p` | `--proxy` | Proxy URL for HTTP requests | None |

## Output Format

The script displays models in a structured format:

```
🤖 Hugging Face 热门模型 (5 个)
============================================================
1. moonshotai/Kimi-K2.5
   ⭐ 2.0K likes   📥 647.6K downloads
   📊 Task: image-text-to-text   📚 Library: transformers
   📅 Created: 2026-01-01   Updated: N/A
...
```

### Model Information

Each model entry includes:
- **Model ID**: Full Hugging Face model name
- **Likes**: Number of likes (popularity metric)
- **Downloads**: Total download count
- **Task**: Primary task/pipeline (e.g., text-generation)
- **Library**: ML framework (transformers, pytorch, tensorflow)
- **Created/Updated**: Date information

## Use Cases

### Daily Monitoring

Check trending models daily for new releases:

```bash
# Create cron job for daily monitoring
0 9 * * * cd /home/ltx/.openclaw/workspace && \
  /home/ltx/.openclaw/workspace/skills/huggingface-trends/scripts/hf_trends.py \
  -n 20 -p http://172.28.96.1:10808 >> /tmp/hf-trends.log 2>&1
```

### Task-Specific Research

Explore popular models for specific AI tasks:

```bash
# Research trending text generation models
scripts/hf_trends.py -n 15 -t text-generation -s likes -p http://172.28.96.1:10808

# Find popular image-to-text models
scripts/hf_trends.py -n 15 -t image-to-text -s downloads -p http://172.28.96.1:10808
```

### Framework-Specific Analysis

Compare models by ML framework:

```bash
# Compare PyTorch vs TensorFlow popularity
scripts/hf_trends.py -n 20 -l pytorch -j pytorch_models.json -p http://172.28.96.1:10808
scripts/hf_trends.py -n 20 -l tensorflow -j tensorflow_models.json -p http://172.28.96.1:10808
```

## Integration with OpenClaw

Use within OpenClaw sessions:

```python
# Fetch trending models programmatically
from skills.huggingface-trends.scripts import hf_trends

fetcher = hf_trends.HuggingFaceTrends(proxy="http://172.28.96.1:10808")
models = fetcher.fetch_trending_models(limit=10)

# Format for display
output = fetcher.format_models(models)
print(output)
```

## Troubleshooting

### Network Errors

**Problem:** "Network is unreachable" or connection errors

**Solution:** Ensure proxy is specified with `-p` flag:
```bash
scripts/hf_trends.py -p http://172.28.96.1:10808
```

Check if v2rayN proxy is running on Windows.

### Empty Results

**Problem:** "No models found"

**Solution:** Try different filters or increase limit:
```bash
scripts/hf_trends.py -n 50 -p http://172.28.96.1:10808
```

### Dependencies Missing

**Problem:** "requests package not installed"

**Solution:** Install required dependencies:
```bash
pip install requests
```

## Technical Notes

- **API Limitation:** Hugging Face's public API doesn't provide a dedicated trending endpoint without authentication. The script fetches recent models and sorts by popularity metrics.
- **Proxy Requirement:** Due to network restrictions, all requests must go through a proxy. The script supports HTTP proxy configuration.
- **Rate Limits:** The public API has rate limits. Avoid making too many requests in quick succession.
- **Data Freshness:** Models are fetched from the Hugging Face API. Recent changes may take time to reflect.

## Reference

See [Hugging Face API Documentation](https://huggingface.co/docs/huggingface_hub/guides/models) for more details on model metadata and available filters.
