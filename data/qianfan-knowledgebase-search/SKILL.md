---
name: qianfan-knowledgebase-search
description: Search knowledge from Qianfan Knowledgebase. Use this when you need to retrieve information from user's private knowledge bases on Baidu Qianfan platform.
metadata: { "openclaw": { "emoji": "📚",  "requires": { "bins": ["python3"], "env":["BAIDU_API_KEY", "QIANFAN_KNOWLEDGEBASE_IDS"]},"primaryEnv":"BAIDU_API_KEY" } }
---

# Qianfan Knowledgebase Search Skill

Search and retrieve knowledge from Baidu Qianfan platform knowledge bases. Supports semantic search, fulltext search, hybrid search, and reranking.

## Workflow

1. The skill executes the Python script located at `search.py`
2. The script makes a POST request to the Qianfan Knowledgebase Search API
3. The API returns structured search results with chunks, scores, and metadata

## Environment Variables

| env | required | description |
|-----|----------|-------------|
| BAIDU_API_KEY | yes | Qianfan platform API Key |
| QIANFAN_KNOWLEDGEBASE_IDS | no | Knowledgebase IDs, comma-separated (used if not specified in request) |

## Parameters

#### request body structure
| param | type | required | default | description |
|-------|------|----------|---------|-------------|
| query | str | yes | | Search query content |
| knowledgebase_ids | list[str] | no | | Knowledgebase ID list (uses env var if not specified) |
| top_k | int | no | 6 | Number of chunks to return, range [1, 40] |
| score_threshold | float | no | 0.4 | Score threshold for filtering, range [0, 1] |
| enable_graph | bool | no | false | Enable knowledge graph |
| enable_expansion | bool | no | false | Return expanded chunks |
| recall | obj | no | | Recall strategy configuration |
| +recall.type | str | no | hybrid | Recall type: fulltext/semantic/hybrid |
| +recall.top_k | int | no | 100 | Recall phase top_k, range [1, 400] |
| +recall.vec_weight | float | no | 0.75 | Vector weight when type=hybrid, range [0, 1] |
| rerank | obj | no | | Rerank configuration |
| +rerank.enable | bool | no | true | Enable reranking |
| +rerank.top_n | int | no | 20 | Rerank top_n, range [1, 40] |

> Note: Use flattened parameter names in input (e.g., `recall_type`, `recall_top_k`), the script will convert to nested structure automatically.

## Example Usage

```bash
# Configure knowledgebase IDs via environment variable
export BAIDU_API_KEY="your_api_key"
export QIANFAN_KNOWLEDGEBASE_IDS="kb_id_1,kb_id_2"
python3 skills/qianfan-knowledgebase-search/search.py '{"query":"请介绍下千帆大模型知识库"}'
```

```bash
# Or specify knowledgebase IDs in request parameters
python3 skills/qianfan-knowledgebase-search/search.py '{"query":"如何使用API","knowledgebase_ids":["kb_id_1","kb_id_2"],"top_k":10,"recall_type":"hybrid","rerank_enable":true}'
```

## Response Structure

Response contains the following fields:

- **id**: Request unique identifier
- **created_at**: Request timestamp
- **total_count**: Total number of chunks returned
- **chunks**: Chunk list
  - **chunk_id**: Chunk unique identifier
  - **content**: Chunk content (supports text/figure/table/graph types)
  - **rerank**: Rerank score and position
  - **recall**: Recall score and position
  - **meta**: Metadata (chunk_type, tokens, word_count, doc_info, etc.)
  - **neighbors**: Related chunks

## Current Status

The Qianfan Knowledgebase Search skill is fully functional and can be used to retrieve knowledge from private knowledge bases on the Baidu Qianfan platform.