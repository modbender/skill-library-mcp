# Elasticsearch Python Client 9.x (Read-Only Patterns)

**Note:** This reference covers read-only operations for querying and analytics.

## Install

```bash
pip install "elasticsearch>=9.0.0" python-dotenv
```

Latest stable: **9.1.3** (PyPI, Feb 2026). 9.3.0 released 2026-02-03 — check PyPI for availability.

## Connect

```python
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL"),
    api_key=os.getenv("ELASTICSEARCH_API_KEY")
)

info = es.info()
print(info["version"]["number"])  # "9.3.0"
```

## ⚠️ Breaking Change: No `body=` Parameter

The `body=` parameter was deprecated in 8.x and **removed in 9.x**.
Use keyword arguments directly instead.

```python
# ❌ Old (8.x) — raises TypeError in 9.x
es.search(index="my-index", body={"query": {"match_all": {}}})

# ✅ New (9.x) — keyword args
es.search(index="my-index", query={"match_all": {}})
es.search(index="my-index", query={"match": {"title": "broccoli"}}, size=20)
```

## Common Read-Only Operations — 9.x Syntax

### Search
```python
results = es.search(
    index="fresh-produce",
    query={"semantic": {"field": "semantic_text", "query": "healthy greens"}},
    size=10,
    source=["name", "category", "price"]
)

for hit in results["hits"]["hits"]:
    print(hit["_source"])
```

### Get Mapping (Inspect Index Structure)
```python
mapping = es.indices.get_mapping(index="fresh-produce")
print(mapping["fresh-produce"]["mappings"]["properties"])
```

### Aggregations
```python
results = es.search(
    index="fresh-produce",
    size=0,  # don't need hits, just aggs
    aggs={
        "by_category": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "avg_price": {"avg": {"field": "price"}}
            }
        }
    }
)

for bucket in results["aggregations"]["by_category"]["buckets"]:
    print(f"{bucket['key']}: avg ${bucket['avg_price']['value']:.2f}")
```

### Check if Inference Endpoint Exists
```python
from elasticsearch import NotFoundError

try:
    endpoint = es.inference.get(inference_id="jina-embeddings-v3")
    print(f"Endpoint exists: {endpoint['service']}")
except NotFoundError:
    print("Endpoint not found")
```

## Type Hints (9.x)

```python
from elasticsearch import Elasticsearch
from typing import Dict, Any

def connect() -> Elasticsearch:
    return Elasticsearch(ES_URL, api_key=API_KEY)

def search_products(es: Elasticsearch, query: str) -> Dict[str, Any]:
    return es.search(index="products", query={"match": {"name": query}})
```

## Error Handling

```python
from elasticsearch import NotFoundError, BadRequestError, AuthenticationException

try:
    es.indices.get(index="my-index")
except NotFoundError:
    print("Index doesn't exist")
except AuthenticationException:
    print("Invalid API key")
except BadRequestError as e:
    print(f"Bad request: {e.error}")
```

## Environment Pattern

**For OpenClaw workspace:** `~/.openclaw/workspace-[name]/.env`
```bash
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=base64encodedkey==
JINA_API_KEY=jina_xxxxxxxxxx
```

**For standalone Python projects:** Create `.env` in your project root:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # loads from .env in current directory

ES_URL    = os.getenv("ELASTICSEARCH_URL")
ES_APIKEY = os.getenv("ELASTICSEARCH_API_KEY")
JINA_KEY  = os.getenv("JINA_API_KEY")

# Validate before using
missing = [k for k, v in {"ES_URL": ES_URL, "ES_APIKEY": ES_APIKEY}.items() if not v]
if missing:
    raise ValueError(f"Missing env vars: {missing}")
```

Always add `.env` to `.gitignore`.

## Suppress SSL Warning (LibreSSL on macOS)

```python
import warnings
import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)
```

Common on macOS with system Python 3.9 — harmless but noisy.
