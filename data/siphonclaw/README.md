# SiphonClaw

**Document intelligence pipeline with triple hybrid search, visual retrieval, and a learning loop.**

You are a mobile worker. Your documentation lives in a thousand-page PDF on a shared drive somewhere. The fix that saved you four hours last month is trapped in your head -- or worse, in someone else's. There is no system that connects what you know to what you need, when you need it. SiphonClaw is that system.

## What It Does

- **Ingest any document collection** -- PDFs, spreadsheets, images, scanned pages, URLs -- into a searchable knowledge base with zero manual tagging
- **Ask questions in natural language**, get cited answers with confidence scores and source attribution
- **Capture field fixes and resolutions** that feed back into the knowledge base, making every solved problem improve future answers
- **Identify parts and equipment from photos** using vision AI with automatic OCR extraction
- **Access from anywhere** -- Telegram bot, email pipeline, CLI, or Python API
- **Five-tier model routing** with automatic failover and budget protection -- runs on a $0.50/month budget or fully local for free

## The Pipeline

```
Documents (PDFs, images, spreadsheets, URLs)
                    |
          +-------------------+
          |   INGESTION       |
          |   OCR (Qwen3-VL)  |
          |   Chunking        |
          |   Metadata detect |
          +-------------------+
                    |
              ChromaDB + BM25
              (indexed + stored)
                    |
                    v
              USER QUERY
                    |
          +---------+---------+
          |   Query Expander  |
          +---------+---------+
                    |
    +---------------+---------------+
    |               |               |
+---+-----+   +----+----+   +------+------+
| BM25    |   | BGE-M3  |   | Visual      |
| Keyword |   | Vector  |   | Page Search |
+---------+   +---------+   +-------------+
    |               |               |
    +-------+-------+-------+-------+
            |  RRF Fusion (k=60)  |
            +---------+-----------+
                      |
            +---------+---------+
            | Cross-Encoder     |
            | Reranker          |
            +---------+---------+
                      |
            +---------+---------+
            | Model Router      |
            | (5-tier fallback) |
            +---------+---------+
                      |
            +---------+---------+
            | Citation Engine + |
            | Confidence Scorer |
            +---------+---------+
                      |
               CITED ANSWER
          with [1] source refs
          + confidence score
                      |
            +---------+---------+
            | Learning Loop     |
            | (captures fixes,  |
            |  re-ranks results)|
            +---------+---------+
```

**Triple hybrid search** means every query hits three independent retrieval paths -- keyword matching (BM25), semantic vector search (BGE-M3 dense + sparse embeddings), and visual page retrieval (for diagrams, tables, and scanned content). Results are fused with Reciprocal Rank Fusion, then reranked by a cross-encoder before the LLM ever sees them.

**The learning loop** is what makes SiphonClaw different from a static RAG system. When you capture a fix -- "replaced the control board, recalibrated per manual section 4.3" -- that resolution becomes a first-class document in the knowledge base. The next person who hits the same problem gets your fix surfaced alongside the OEM documentation, ranked by verified effectiveness.

## Why It Was Built

This project was built by a field service engineer who repairs complex equipment at customer sites. The job means standing in a basement with a phone, searching through a 1,200-page service manual for a calibration procedure that might be on page 847 or might be in a completely different document. The existing tools for this are a PDF viewer and hope.

The deeper problem is institutional knowledge. When a technician figures out that a specific failure mode requires a specific sequence of steps not documented anywhere, that knowledge lives in their head. When they leave, it walks out the door. There is no capture mechanism. There is no feedback loop. Every new technician starts from scratch on the same problems.

The friction is not just technical -- it is organizational. Who is the regional contact for a specific product line? What is the procedure for ordering a part that is backordered? Where is the contact list that was emailed six months ago? This information exists, scattered across emails, shared drives, and tribal knowledge. It is never where you need it, when you need it.

SiphonClaw is the work companion that should exist for anyone who works away from a desk: ingest everything, search anything, capture what you learn, and make the next person's job easier.

## Use Cases

### Field Service and Maintenance
Equipment manuals, parts catalogs, repair logs. Paste a dispatch description, get potential root causes with parts needed and procedure references. Log what actually fixed it. Build institutional knowledge that survives employee turnover.

### Legal and Compliance
Case law, contracts, regulations, policy documents. Search across thousands of documents with cited sources and confidence scores. Track which interpretations have been verified.

### Automotive and Aviation Mechanics
Service bulletins, wiring diagrams, parts cross-reference databases. Photo identification for unknown components. Search across technical service bulletins by symptom description.

### IT Operations and DevOps
Runbooks, incident postmortems, knowledge base articles. When a new incident matches the pattern of a resolved one, surface the resolution automatically. Build a searchable history of what broke and how it was fixed.

### Research and Academic
Paper collections, lab notebooks, textbooks, reference materials. Ask questions across your entire library and get answers with specific citations to source documents and page numbers.

### Construction and Trades
Building codes, spec sheets, material safety data sheets, installation guides. Get answers to code questions on-site without flipping through binders.

### Sales and Account Management
Contact databases, meeting notes, proposals, contract histories. "Who handles procurement at Company Y?" with the source document and date.

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/curtisgc1/siphonclaw.git
cd siphonclaw
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys (see Configuration below)

# 3. Install local models (recommended - free, unlimited ingestion)
ollama pull qwen3-vl:latest      # 6.1 GB - OCR and vision
ollama pull bge-m3:latest         # 1.5 GB - text embeddings

# 4. Ingest your documents
siphonclaw ingest /path/to/your/docs

# 5. Search
siphonclaw search "calibration procedure for sensor module"
```

## MCP Server

SiphonClaw exposes all five tools via [Model Context Protocol](https://modelcontextprotocol.io/). Any MCP-compatible client can connect.

```bash
# Start the MCP server (stdio transport)
python mcp_server.py

# SSE transport for HTTP clients
python mcp_server.py --sse --port 8000
```

Add to your MCP client config (Claude Desktop, OpenClaw, etc.):

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

Tools available: `siphonclaw_search`, `siphonclaw_ingest`, `siphonclaw_field_note`, `siphonclaw_identify`, `siphonclaw_status`.

## CLI Reference

```bash
# Natural language search with optional filters
siphonclaw search "control board part number" --equipment ModelA --top-k 10

# Batch ingest a directory of documents
siphonclaw ingest /path/to/docs --batch-size 25

# Capture a field fix (feeds the learning loop)
siphonclaw fix --equipment "ModelA" --problem "HV failure" --fix "Replaced board #12345"

# System status, model health, and feedback stats
siphonclaw status
siphonclaw status --models
siphonclaw status --feedback
siphonclaw status --budget

# Interactive setup wizard
siphonclaw setup
```

## Python API

```python
from api import query, capture_field_fix, get_status

# Ask a question - get a cited answer
result = query("What is the part number for the compressor valve?")
print(result["answer"])         # Generated answer with inline [1] citations
print(result["confidence"])     # 0.0 - 1.0 composite confidence score
print(result["sources"])        # Source documents with relevance scores

# Capture a fix (builds institutional knowledge)
capture_field_fix(
    equipment="ModelA",
    problem="Control board failure after power surge",
    fix="Replaced control board, recalibrated per manual section 4.3",
    parts_used=["12345", "67890"],
    procedure_ref="SM-100 4.3",
)

# System health
status = get_status()
# {"collections": {"manuals": 45000, ...}, "total_chunks": 656000}
```

## Configuration

SiphonClaw supports two operating modes. All configuration is via environment variables in `.env`.

### Mode A: Hybrid (Recommended)

Local models handle ingestion (OCR + embeddings) at zero cost. Cloud APIs handle the intelligence layer (answering questions). This is the sweet spot for most deployments.

```bash
# Local ingestion (free, unlimited)
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_VISION_MODEL=qwen3-vl:latest

# Cloud intelligence (pick one)
OPENROUTER_API_KEY=sk-or-v1-xxxxx           # One key, all models
# -- or direct vendor keys --
MINIMAX_API_KEY=your-minimax-key             # Primary ($0.15/M input)
KIMI_API_KEY=your-moonshot-key               # Backup

# Budget protection
DAILY_BUDGET_CAP=5.0

# Optional channels
TELEGRAM_BOT_TOKEN=your-bot-token            # Telegram access
AGENTMAIL_API_KEY=your-agentmail-key         # Email pipeline
BRAVE_SEARCH_API_KEY=BSA-xxxxx              # Web fallback (2,000 free/mo)
```

### Mode B: Full Cloud

Everything runs through OpenRouter. Simpler setup, but ingestion costs money for the first run.

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=minimax/MiniMax-M2.5
```

### Domain Customization

SiphonClaw is domain-agnostic. Set a prefix to namespace your collections:

```bash
DOMAIN_NAME=my_company
DOMAIN_PREFIX=mc_
# Collections become: mc_manuals, mc_parts, mc_troubleshooting, etc.
```

### Cost Comparison

| Operation | Mode A (Hybrid) | Mode B (Full Cloud) |
|-----------|-----------------|---------------------|
| Ingest 3,000 PDFs | $0 (local Ollama) | ~$50-100 (cloud OCR + embeddings) |
| 100 searches/month | ~$0.50 (API generation) | ~$0.50 (same) |
| **Monthly total** | **~$0.50-5/mo** | **~$50-105 first month, then $0.50/mo** |

## Model Router

The model router cascades through five tiers with automatic failover. If a provider fails three times consecutively, the circuit breaker opens and the router skips it for five minutes.

| Priority | Provider | Cost | Notes |
|----------|----------|------|-------|
| 1 | MiniMax M2.5 (API) | $0.15/M in | Primary engine, handles 80% of queries |
| 2 | Kimi K2.5 (API) | Free w/ subscription | Backup with deep reasoning |
| 3 | MiniMax M2.5 (local MLX) | $0 | Apple Silicon only, requires 128GB+ RAM |
| 4 | OpenRouter | Varies | Unified gateway, one API key |
| 5 | Ollama (local) | $0 | Always-available fallback |

Budget protection: when daily spend hits the cap (default $5), paid providers are skipped and the router falls through to free/local tiers automatically.

## Project Structure

```
siphonclaw/
├── api.py                          # Public API - import and call directly
├── cli.py                          # Command-line interface
├── config/
│   ├── settings.py                 # Domain-configurable settings (frozen dataclasses)
│   └── models.yaml                 # Model tier configuration
├── ingestion/
│   ├── batch_ingest.py             # Orchestrator with circuit breaker
│   ├── pdf_loader.py               # PDF extraction with adaptive timeout
│   ├── ocr_processor.py            # Qwen3-VL OCR via Ollama
│   ├── visual_embedder.py          # Page-level visual embeddings
│   ├── xlsx_loader.py              # Excel with encryption detection
│   ├── chunker.py                  # Table-aware semantic chunking
│   ├── metadata_extractor.py       # Equipment/doc-type detection
│   ├── url_loader.py               # Web page ingestion
│   ├── image_loader.py             # Photo/image ingestion with OCR
│   ├── text_loader.py              # Plain text and HTML
│   ├── pptx_loader.py              # PowerPoint extraction
│   ├── dead_letter.py              # Failed file tracking + retry
│   └── zip_extractor.py            # ZIP archive handling
├── db/
│   ├── client.py                   # ChromaDB singleton
│   ├── collections.py              # Domain-prefixed collection manager
│   ├── embedding_function.py       # BGE-M3 dense+sparse embeddings
│   └── models.py                   # Data structures
├── retrieval/
│   ├── search.py                   # Triple hybrid search + RRF fusion
│   ├── visual_search.py            # Visual page retrieval
│   ├── reranker.py                 # Cross-encoder reranker
│   ├── bm25.py                     # BM25 keyword scoring
│   ├── query_expander.py           # Multi-model query expansion
│   ├── query_router.py             # Route queries to collections
│   ├── corrections.py              # User correction store
│   ├── embeddings.py               # Embedding utilities
│   └── parts_xref.py              # Part number cross-reference
├── pipeline/
│   ├── query_engine.py             # Main orchestrator
│   ├── response_generator.py       # LLM response with citations
│   ├── model_router.py             # 5-tier provider fallback + budget
│   ├── citation_engine.py          # Footnote-style [1] citations
│   ├── confidence_scorer.py        # 4-signal composite confidence
│   ├── field_capture.py            # Photo/doc identify + ingest
│   ├── feedback_loop.py            # Field fix learning + re-ranking
│   ├── web_search.py               # Brave Search fallback
│   ├── email_handler.py            # Email pipeline (AgentMail)
│   └── telegram_handler.py         # Telegram bot integration
├── tests/                          # Full test suite (mocked, no GPU needed)
├── scripts/
│   ├── run_ingest.py               # Batch ingestion runner
│   ├── monitor_ingest.sh           # Ingestion monitoring
│   └── start-mlx-server.sh         # Local MLX model server
├── mcp_server.py                   # MCP server (stdio + SSE transport)
├── .env.example                    # Configuration template
├── requirements.txt
└── pyproject.toml
```

## Supported File Types

| Type | Extensions | Method |
|------|-----------|--------|
| PDF | `.pdf` | PyMuPDF text extraction + Qwen3-VL OCR for scanned pages |
| Spreadsheet | `.xlsx`, `.xls` | openpyxl / xlrd with encryption detection |
| Presentation | `.pptx`, `.ppt` | Slide text and notes extraction |
| Document | `.docx`, `.doc` | Full text extraction |
| Plain text | `.txt`, `.html`, `.htm` | Direct ingestion |
| Image | `.jpg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.heic` | Vision AI OCR |
| Archive | `.zip` | Recursive extraction and processing |
| URL | Any web page | Fetch, convert to markdown, chunk and index |

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) (recommended for local ingestion -- free)
- At least one LLM API key (OpenRouter, MiniMax, or Kimi) for cloud intelligence, **or** Ollama for fully local operation
- ChromaDB (installed automatically via pip)

## License

MIT
