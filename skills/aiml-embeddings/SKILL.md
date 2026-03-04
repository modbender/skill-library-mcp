---
name: aimlapi-embeddings
description: Generate text embeddings via AIMLAPI. Use for semantic search, clustering, or high-dimensional text representations with text-embedding-3-large and other models.
env:
  - AIMLAPI_API_KEY
primaryEnv: AIMLAPI_API_KEY
---

# AIMLAPI Embeddings

## Overview

Converts text into high-dimensional numerical representations (vectors) using AIMLAPI's embedding models like `text-embedding-3-large`.

## Quick start

```bash
export AIMLAPI_API_KEY="sk-aimlapi-..."
python3 {baseDir}/scripts/gen_embeddings.py --input "Laura is a DJ."
```

## Tasks

### Generate embeddings

Use `scripts/gen_embeddings.py` to get vector representations of text.

```bash
python3 {baseDir}/scripts/gen_embeddings.py \
  --input "Knowledge is power." \
  --model text-embedding-3-large \
  --dimensions 1024 \
  --out-dir ./out/embeddings
```

## References

- `references/endpoints.md`: API schema and parameter details.
