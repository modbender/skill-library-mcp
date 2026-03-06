---
name: moss-docs
description: Documentation and capabilities reference for Moss semantic search.
  Use for understanding Moss APIs, SDKs, and integration patterns.
metadata:
  author: usemoss
  version: "1.0"
  docs-url: https://docs.usemoss.dev
  mintlify-proj: moss
---

# Moss Agent Skills

## Capabilities

Moss is the real-time semantic search runtime for conversational AI. It delivers sub-10ms lookups and instant index updates that run in the browser, on-device, or in the cloud - wherever your agent lives. Agents can create indexes, embed documents, perform semantic/hybrid searches, and manage document lifecycles without managing infrastructure. The platform handles embedding generation, index persistence, and optional cloud sync - allowing agents to focus on retrieval logic rather than infrastructure.

## Skills

### Index Management

- **Create Index**: Build a new semantic index with documents and embedding model selection
- **Load Index**: Load an existing index from persistent storage for querying
- **Get Index**: Retrieve metadata about a specific index (document count, model, etc.)
- **List Indexes**: Enumerate all indexes under a project
- **Delete Index**: Remove an index and all associated data

### Document Operations

- **Add Documents**: Insert or upsert documents into an existing index with optional metadata
- **Get Documents**: Retrieve stored documents by ID or fetch all documents
- **Delete Documents**: Remove specific documents from an index by their IDs

### Search & Retrieval

- **Semantic Search**: Query using natural language with vector similarity matching
- **Keyword Search**: Use BM25-based keyword matching for exact term lookups
- **Hybrid Search**: Blend semantic and keyword search with configurable alpha weighting
- **Metadata Filtering**: Constrain results by document metadata (category, language, tags)
- **Top-K Results**: Return configurable number of best-matching documents with scores

### Embedding Models

- **moss-minilm**: Fast, lightweight model optimized for edge/offline use (default)
- **moss-mediumlm**: Higher accuracy model with reasonable performance for precision-critical use cases

### SDK Methods

| JavaScript      | Python           | Description                 |
| --------------- | ---------------- | --------------------------- |
| `createIndex()` | `create_index()` | Create index with documents |
| `loadIndex()`   | `load_index()`   | Load index from storage     |
| `getIndex()`    | `get_index()`    | Get index metadata          |
| `listIndexes()` | `list_indexes()` | List all indexes            |
| `deleteIndex()` | `delete_index()` | Delete an index             |
| `addDocs()`     | `add_docs()`     | Add/upsert documents        |
| `getDocs()`     | `get_docs()`     | Retrieve documents          |
| `deleteDocs()`  | `delete_docs()`  | Remove documents            |
| `query()`       | `query()`        | Semantic search             |

### API Actions

All REST API operations go through `POST /manage` with an `action` field:

- `createIndex` - Create index with seed documents
- `getIndex` - Get metadata for single index
- `listIndexes` - List all project indexes
- `deleteIndex` - Remove index and assets
- `addDocs` - Upsert documents into index
- `getDocs` - Retrieve stored documents
- `deleteDocs` - Remove documents by ID

## Workflows

### Basic Semantic Search Workflow

1. Initialize MossClient with project credentials
2. Call `createIndex()` with documents and model (`moss-minilm` or `moss-mediumlm`)
3. Call `loadIndex()` to prepare index for queries
4. Call `query()` with search text and top_k parameter
5. Process returned documents with scores

### Hybrid Search Workflow

1. Create and load index as above
2. Call `query()` with alpha parameter to blend semantic and keyword
3. `alpha: 1.0` = pure semantic, `alpha: 0.0` = pure keyword, `alpha: 0.6` = 60/40 blend
4. Default is semantic-heavy (\~0.8) for conversational use cases

### Document Update Workflow

1. Initialize client and ensure index exists
2. Call `addDocs()` with new documents and `upsert: true` option
3. Existing documents with matching IDs are updated; new IDs are inserted
4. Call `deleteDocs()` to remove outdated documents by ID

### Voice Agent Context Injection Workflow

1. Initialize MossClient and load index at agent startup
2. On each user message, automatically query Moss for relevant context
3. Inject search results into LLM context before generating response
4. Respond with knowledge-grounded answer (no tool-calling latency)

### Offline-First Search Workflow

1. Create index with documents using local embedding model
2. Load index from local storage
3. Query runs entirely on-device with sub-10ms latency
4. Optionally sync to cloud for backup and sharing

## Integration

### Voice Agent Frameworks

- **LiveKit**: Context injection into voice agent pipeline with `inferedge-moss` SDK
- **Pipecat**: Pipeline processor via `pipecat-moss` package that auto-injects retrieval results

## Context

### Authentication

SDK requires project credentials:

- `MOSS_PROJECT_ID`: Project identifier from Moss Portal
- `MOSS_PROJECT_KEY`: Project access key from Moss Portal

```bash theme={null}
export MOSS_PROJECT_ID=your_project_id
export MOSS_PROJECT_KEY=your_project_key
```

REST API requires headers:

- `x-project-key`: Project access key
- `x-service-version: v1`: API version header
- `projectId` in JSON body

### Package Installation

| Language              | Package           | Install Command               |
| --------------------- | ----------------- | ----------------------------- |
| JavaScript/TypeScript | `@inferedge/moss` | `npm install @inferedge/moss` |
| Python                | `inferedge-moss`  | `pip install inferedge-moss`  |
| Pipecat Integration   | `pipecat-moss`    | `pip install pipecat-moss`    |

### Document Schema

```typescript theme={null}
interface DocumentInfo {
  id: string; // Required: unique identifier
  text: string; // Required: content to embed and search
  metadata?: object; // Optional: key-value pairs for filtering
}
```

### Query Parameters

| Parameter        | Type   | Default | Description                                 |
| ---------------- | ------ | ------- | ------------------------------------------- |
| `indexName`      | string | -       | Target index name (required)                |
| `query`          | string | -       | Natural language search text (required)     |
| `top_k` / `topK` | number | 5       | Max results to return                       |
| `alpha`          | float  | \~0.8   | Hybrid weighting: 0.0=keyword, 1.0=semantic |
| `filters`        | object | -       | Metadata constraints                        |

### Model Selection

| Model           | Use Case                            | Tradeoff          |
| --------------- | ----------------------------------- | ----------------- |
| `moss-minilm`   | Edge, offline, browser, speed-first | Fast, lightweight |
| `moss-mediumlm` | Precision-critical, higher accuracy | Slightly slower   |

### Performance Expectations

- Sub-10ms local queries (hardware-dependent)
- Instant index updates without reindexing entire corpus
- Sync is optional; compute stays on-device
- No infrastructure to manage

### Chunking Best Practices

- Aim for \~200–500 tokens per chunk
- Overlap 10–20% to preserve context
- Normalize whitespace and strip boilerplate

### Common Errors

| Error                      | Cause               | Fix                                          |
| -------------------------- | ------------------- | -------------------------------------------- |
| Unauthorized               | Missing credentials | Set `MOSS_PROJECT_ID` and `MOSS_PROJECT_KEY` |
| Index not found            | Query before create | Call `createIndex()` first                   |
| Index not loaded           | Query before load   | Call `loadIndex()` before `query()`          |
| Missing embeddings runtime | Invalid model       | Use `moss-minilm` or `moss-mediumlm`         |

### Async Pattern

All SDK methods are async - always use `await`:

```typescript theme={null}
// JavaScript
await client.createIndex("faqs", docs, "moss-minilm");
await client.loadIndex("faqs");
const results = await client.query("faqs", "search text", 5);
```

```python theme={null}
# Python
await client.create_index("faqs", docs, "moss-minilm")
await client.load_index("faqs")
results = await client.query("faqs", "search text", top_k=5)
```

---

> For additional documentation and navigation, see: [https://docs.usemoss.dev/llms.txt](https://docs.usemoss.dev/llms.txt)
