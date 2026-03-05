---
name: siphonclaw
description: Document intelligence pipeline with visual search, OCR, and field capture
version: 1.2.0
metadata:
  siphonclaw:
    emoji: "\U0001F50D"
    requires:
      plugins: []
---

# SiphonClaw

Domain-agnostic document intelligence pipeline. Ingest PDFs, images, and spreadsheets into a searchable knowledge base with dual-track retrieval (text + visual), OCR, confidence scoring, and field capture.

Built for field service engineers, researchers, mechanics, and anyone who needs fast answers from large document collections.

## What SiphonClaw Does

- **Ingest** documents (PDF, Excel, images, screenshots) into a local vector database with text and visual embeddings
- **Search** using triple hybrid retrieval: BM25 keyword matching + semantic text vectors + visual page embeddings, fused with RRF and reranked with a cross-encoder
- **Identify** equipment, parts, or components from photos using vision models, then search the local knowledge base
- **Capture** field fixes and repair notes as first-class knowledge base entries for future retrieval
- **Score** every response with composite confidence (retrieval + faithfulness + relevance + coverage) and footnote-style source citations

## MCP Tools

SiphonClaw exposes five tools via MCP for integration with agents and other MCP-compatible clients.

---

### siphonclaw_search

Search the knowledge base using triple hybrid retrieval (text + visual + keyword).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | yes | Natural language search query or exact part number / error code |
| `top_k` | integer | no | Number of results to return (default: 5, max: 20) |
| `filters` | object | no | Metadata filters (e.g., `{"source_type": "service_manual", "model": "ModelA"}`) |
| `mode` | string | no | Search mode: `"hybrid"` (default), `"text"`, `"visual"`, `"keyword"` |

**Returns:**

```json
{
  "results": [
    {
      "content": "Extracted text from the matching chunk or page",
      "source": "ServiceManual_ModelA.pdf",
      "page": 42,
      "section": "4.3 Transformer Replacement",
      "score": 0.92,
      "match_type": "hybrid"
    }
  ],
  "confidence": 0.87,
  "confidence_tier": "Confident - verify part number",
  "keywords_used": ["low voltage supply", "assembly mount", "ModelA"],
  "citations": ["[1] ServiceManual_ModelA, page 42", "[2] Parts Catalog PC-1102, page 15"]
}
```

---

### siphonclaw_ingest

Add a document or photo to the knowledge base. Supports PDF, Excel, images (JPG/PNG), and screenshots.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `file_path` | string | yes | Absolute path to the file to ingest |
| `source_type` | string | no | Document type hint: `"manual"`, `"parts_catalog"`, `"field_note"`, `"photo"`, `"other"` (default: auto-detect) |
| `metadata` | object | no | Additional metadata to attach (e.g., `{"model": "ModelA", "domain": "industrial"}`) |

**Returns:**

```json
{
  "status": "ingested",
  "file": "ServiceManual_ModelA.pdf",
  "pages_processed": 127,
  "chunks_created": 843,
  "visual_pages_indexed": 127,
  "ocr_pages": 12,
  "duration_seconds": 45.2
}
```

---

### siphonclaw_field_note

Save a field fix or repair note as a first-class knowledge base entry. These are indexed and retrievable in future searches, forming a learning loop.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `note` | string | yes | Free-text description of the fix, procedure, or observation |
| `model` | string | no | Equipment model or identifier (e.g., `"ModelA"`) |
| `parts` | array[string] | no | Part numbers used in the repair (e.g., `["12345", "67890"]`) |
| `procedure_ref` | string | no | Reference to a manual procedure (e.g., `"ServiceManual_ModelA section 4.3"`) |
| `tags` | array[string] | no | Free-form tags for categorization (e.g., `["hv_transformer", "calibration"]`) |

**Returns:**

```json
{
  "status": "saved",
  "field_note_id": "fn-2026-02-09-001",
  "indexed": true,
  "model": "ModelA",
  "parts_cross_referenced": ["12345"],
  "retrievable": true
}
```

---

### siphonclaw_identify

Send a photo of equipment, a part, a label, or an error screen. SiphonClaw uses vision models to identify what it sees, then searches the local knowledge base for relevant documentation. Falls back to web search if local confidence is low.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image_path` | string | yes | Absolute path to the image file (JPG, PNG, HEIC) |
| `context` | string | no | Additional context about the image (e.g., `"circuit board inside equipment housing"`) |
| `search_after` | boolean | no | Automatically search the KB after identification (default: `true`) |

**Returns:**

```json
{
  "identification": "Industrial power supply board, Model PSU-200",
  "visual_features": ["green PCB", "3 large capacitors", "manufacturer logo visible", "part label partially obscured"],
  "ocr_text": "PSU-200 REV C  SN: 4829103",
  "search_results": [
    {
      "content": "PSU-200 replacement procedure...",
      "source": "ServiceManual_ModelA.pdf",
      "page": 67,
      "score": 0.94
    }
  ],
  "confidence": 0.91,
  "web_search_used": false
}
```

---

### siphonclaw_status

Get pipeline health, ingestion statistics, model availability, and cost tracking.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `detail` | string | no | Level of detail: `"summary"` (default), `"full"`, `"costs"`, `"models"` |

**Returns:**

```json
{
  "status": "healthy",
  "knowledge_base": {
    "total_documents": 3164,
    "total_chunks": 656000,
    "visual_pages_indexed": 31200,
    "last_ingestion": "2026-02-09T14:30:00Z"
  },
  "models": {
    "ocr": {"model": "qwen3-vl:latest", "provider": "ollama", "available": true},
    "text_embedding": {"model": "bge-m3:latest", "provider": "ollama", "available": true},
    "visual_embedding": {"model": "qwen3-vl-embed:2b", "provider": "ollama", "available": true},
    "generation": {"model": "MiniMax-M2.5", "provider": "openrouter", "available": true},
    "reasoning": {"model": "kimi-k2.5", "provider": "openrouter", "available": true},
    "fallback": {"model": "glm-4.7-flash:latest", "provider": "ollama", "available": true}
  },
  "costs": {
    "today": "$0.12",
    "this_month": "$2.45",
    "daily_budget": "$5.00",
    "budget_remaining": "$4.88"
  },
  "dead_letter_queue": {
    "pending_retry": 2,
    "permanently_failed": 1
  }
}
```

## MCP Server

SiphonClaw runs as an MCP server that any MCP-compatible client (OpenClaw agents, Claude Desktop, etc.) can connect to.

```bash
# Start the MCP server (stdio transport - default for OpenClaw)
python mcp_server.py

# Start with SSE transport (for HTTP-based clients)
python mcp_server.py --sse --port 8000
```

**OpenClaw agent config (`~/.openclaw/openclaw.json`):**

```json
{
  "mcpServers": {
    "siphonclaw": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/siphonclaw"
    }
  }
}
```

**Claude Desktop config (`claude_desktop_config.json`):**

```json
{
  "mcpServers": {
    "siphonclaw": {
      "command": "python",
      "args": ["/path/to/siphonclaw/mcp_server.py"]
    }
  }
}
```

## Setup

### Mode A: Hybrid Local + Cloud (Recommended)

Local models handle ingestion (OCR + embeddings) for free. Cloud APIs handle intelligence (generation + reasoning) for pennies per query.

**Monthly cost: ~$0.50-5/mo for typical use.**

```bash
# 1. Install SiphonClaw
git clone https://github.com/curtisgc1/siphonclaw.git && cd siphonclaw
pip install -r requirements.txt

# 2. Install Ollama and pull local models (~10 GB total)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3-vl:latest          # 6.1 GB - OCR
ollama pull bge-m3:latest             # ~1.5 GB - text embeddings
ollama pull qwen3-vl-embed:2b        # ~2 GB - visual embeddings

# 3. Get OpenRouter API key (ONE key for all intelligence models)
#    Visit: https://openrouter.ai -> Sign up -> Copy API key
siphonclaw config set openrouter_key sk-or-v1-xxxxx

# 4. (Optional) Get Brave Search API key for web search fallback
#    Visit: https://brave.com/search/api -> Sign up -> Free tier: 2,000 queries/mo
siphonclaw config set brave_key BSA-xxxxx

# 5. Point to your documents and ingest
siphonclaw config set docs_path /path/to/my/docs
siphonclaw ingest

# 6. Search
siphonclaw search "part number for compressor valve"
```

### Mode B: Full Cloud

Everything runs via OpenRouter. Simpler setup (no Ollama needed), but ingestion of large document sets costs $50-100+ in API tokens.

**First month: ~$50-105. After that: ~$0.50/mo.**

```bash
# 1. Install SiphonClaw
pip install siphonclaw

# 2. Get OpenRouter API key
siphonclaw config set openrouter_key sk-or-v1-xxxxx

# 3. Set ingestion mode to cloud
siphonclaw config set ingestion_mode cloud

# 4. (Optional) Get Brave Search API key
siphonclaw config set brave_key BSA-xxxxx

# 5. Point to your documents and ingest
siphonclaw config set docs_path /path/to/my/docs
siphonclaw ingest

# 6. Search
siphonclaw search "part number for compressor valve"
```

### Cost Comparison

| Operation | Mode A (Hybrid) | Mode B (Full Cloud) |
|-----------|-----------------|---------------------|
| Ingest 3,000 PDFs | $0 (local) | ~$50-100 (OCR + embeddings) |
| 100 searches/month | ~$0.50 (API generation) | ~$0.50 (same) |
| Monthly total | **~$0.50-5/mo** | **~$50-105 first month, $0.50/mo after** |

## Configuration Reference

SiphonClaw reads configuration from `config/models.yaml` and environment variables.

**Environment variables (via `.env` or shell):**

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Mode A/B | OpenRouter API key for intelligence models |
| `BRAVE_SEARCH_API_KEY` | no | Brave Search API key for web search fallback |
| `OLLAMA_BASE_URL` | no | Ollama server URL (default: `http://127.0.0.1:11434`) |
| `SIPHONCLAW_BUDGET_DAILY` | no | Daily API spend cap in USD (default: `5.00`) |
| `SIPHONCLAW_DOCS_PATH` | no | Path to document directory for ingestion |

**Agent config example (`config.json`):**

```json
{
  "skills": {
    "entries": {
      "siphonclaw": {
        "openrouter_key": "sk-or-v1-xxxxx",
        "brave_key": "BSA-xxxxx",
        "docs_path": "/path/to/docs",
        "ingestion_mode": "local",
        "ollama_url": "http://127.0.0.1:11434"
      }
    }
  }
}
```

**Model configuration:** See `config/models.yaml` for full model tier configuration with ingestion and intelligence settings.
