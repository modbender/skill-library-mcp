# keyword-extract

Extract keywords and key phrases from text.

## Overview

This skill extracts important keywords, multi-word phrases, and main topics from text. Useful for SEO, content tagging, and search indexing.

## Usage

### CLI Mode

```bash
export OPENAI_API_KEY=sk-...

cat article.txt | expanso-edge run pipeline-cli.yaml
MAX_KEYWORDS=5 echo "Your text here..." | expanso-edge run pipeline-cli.yaml
```

### MCP Mode

```bash
PORT=8080 expanso-edge run pipeline-mcp.yaml &
curl -X POST http://localhost:8080/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Machine learning is transforming...", "max_keywords": 10}'
```

## Output

```json
{
  "keywords": [
    {"word": "machine", "relevance": 0.95},
    {"word": "learning", "relevance": 0.92},
    {"word": "AI", "relevance": 0.88}
  ],
  "phrases": [
    "machine learning",
    "artificial intelligence",
    "neural networks"
  ],
  "topics": [
    "Technology",
    "Artificial Intelligence"
  ],
  "keyword_count": 3,
  "metadata": {...}
}
```

## Use Cases

- SEO keyword research
- Content tagging
- Document indexing
- Topic modeling
- Article summarization
