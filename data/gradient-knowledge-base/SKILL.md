---
name: gradient-knowledge-base
description: >
  Community skill (unofficial) for DigitalOcean Gradient Knowledge Bases.
  Build RAG pipelines: store documents in DO Spaces, configure data sources,
  manage indexing, and run semantic or hybrid search queries.
files: ["scripts/*"]
homepage: https://github.com/Rogue-Iteration/TheBigClaw
metadata:
  clawdbot:
    emoji: "📚"
    primaryEnv: DO_API_TOKEN
    requires:
      env:
        - DO_API_TOKEN
        - DO_SPACES_ACCESS_KEY
        - DO_SPACES_SECRET_KEY
        - GRADIENT_API_KEY
      bins:
        - python3
      pip:
        - requests>=2.31.0
        - boto3>=1.34.0
  author: Rogue Iteration
  version: "0.1.4"
  tags: ["digitalocean", "gradient-ai", "knowledge-base", "rag", "semantic-search", "do-spaces"]
---

# 🦞 Gradient AI — Knowledge Bases & RAG

> ⚠️ **This is an unofficial community skill**, not maintained by DigitalOcean. Use at your own risk.

> *"A lobster never forgets. Neither should your agent." — the KB lobster*

Build a [Retrieval-Augmented Generation](https://docs.digitalocean.com/products/gradient-ai-platform/details/features/#retrieval-augmented-generation-rag) pipeline using DigitalOcean's Gradient Knowledge Bases. Store your documents in DO Spaces, index them into a managed Knowledge Base (backed by OpenSearch), and query them with semantic or hybrid search.

## Architecture

```
Your Agent                   DigitalOcean
┌─────────────┐     upload    ┌──────────────┐
│  Documents  │ ──────────▶  │  DO Spaces   │
└─────────────┘              │  (S3-compat) │
                              └──────┬───────┘
                                     │ auto-index
                              ┌──────▼───────┐
                              │ Knowledge    │
                              │ Base (KBaaS) │
                              │ ┌──────────┐ │
                              │ │OpenSearch│ │
                              │ └──────────┘ │
                              └──────┬───────┘
                                     │ retrieve
┌─────────────┐     answer    ┌──────▼───────┐
│  Your Agent │ ◀──────────  │  RAG Results │
│  + LLM      │              │  + Citations │
└─────────────┘              └──────────────┘
```

📖 *[Knowledge Base docs](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/)*

## API Endpoints

This skill connects to three official DigitalOcean service endpoints:

| Hostname | Purpose | Docs |
|----------|---------|------|
| `api.digitalocean.com` | KB management (create, list, delete, data sources) | [DO API Reference](https://docs.digitalocean.com/reference/api/) |
| `kbaas.do-ai.run` | KB retrieval — semantic/hybrid search queries | [KB Retrieval docs](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/) |
| `inference.do-ai.run` | LLM chat completions for RAG synthesis | [Inference docs](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/) |
| `<region>.digitaloceanspaces.com` | S3-compatible object storage | [Spaces docs](https://docs.digitalocean.com/products/spaces/) |

All endpoints are owned and operated by DigitalOcean. The `*.do-ai.run` hostnames are the Gradient AI Platform's service domains.

## Authentication

This skill uses **two different credentials** — think of it as a two-claw approach:

| Credential | Used For | Env Var |
|------------|----------|---------|
| DO API Token | KB management, indexing, queries | `DO_API_TOKEN` |
| Gradient API Key | LLM inference for RAG synthesis | `GRADIENT_API_KEY` |
| Spaces Keys | S3-compatible uploads | `DO_SPACES_ACCESS_KEY` + `DO_SPACES_SECRET_KEY` |

> **Credential scoping:** Use minimally-scoped tokens. Create a dedicated [Model Access Key](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/manage-access-keys/) for `GRADIENT_API_KEY`. For `DO_API_TOKEN`, use a [scoped API token](https://docs.digitalocean.com/reference/api/create-personal-access-token/) with only Knowledge Base and Spaces permissions. Avoid using your account-root token.

Optional but recommended:
```bash
export GRADIENT_KB_UUID="your-kb-uuid"     # Default KB for queries
export DO_SPACES_BUCKET="your-bucket"      # Default bucket for uploads
export DO_SPACES_ENDPOINT="https://nyc3.digitaloceanspaces.com"
```

---

## Tools

### 📦 Store Documents in Spaces

Upload files to DO Spaces for Knowledge Base indexing. This is the storage layer — documents land here before being indexed.

```bash
# Upload a file
python3 gradient_spaces.py --upload /path/to/report.md --bucket my-kb-data

# Upload with a key prefix (folder structure)
python3 gradient_spaces.py --upload report.md --bucket my-kb-data --prefix "research/2026-02-15/"

# List files in a bucket
python3 gradient_spaces.py --list --bucket my-kb-data

# List files with a prefix filter
python3 gradient_spaces.py --list --bucket my-kb-data --prefix "research/"

# Delete a file
python3 gradient_spaces.py --delete "research/old_report.md" --bucket my-kb-data
```

📖 *[DO Spaces docs](https://docs.digitalocean.com/products/spaces/)*

---

### 🏗️ Create and Manage Knowledge Bases

Full CRUD for Knowledge Bases. Create them programmatically instead of clicking through the console like a land-dweller.

```bash
# List all Knowledge Bases
python3 gradient_kb_manage.py --list

# Create a new KB
python3 gradient_kb_manage.py --create --name "My Research KB" --region nyc3

# Show details for a specific KB
python3 gradient_kb_manage.py --show --kb-uuid "your-kb-uuid"

# Delete a KB (⚠️ permanent!)
python3 gradient_kb_manage.py --delete --kb-uuid "your-kb-uuid"
```

📖 *[Create KBs via API](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/)*

---

### 📁 Manage Data Sources

Connect your Spaces bucket (or web URLs) to a Knowledge Base. This is what tells the KB "index these documents."

```bash
# Add a DO Spaces data source
python3 gradient_kb_manage.py --add-source \
  --kb-uuid "your-kb-uuid" \
  --bucket my-kb-data \
  --prefix "research/"

# List data sources for a KB
python3 gradient_kb_manage.py --list-sources --kb-uuid "your-kb-uuid"

# Trigger re-indexing (auto-detects the data source)
python3 gradient_kb_manage.py --reindex --kb-uuid "your-kb-uuid"

# Trigger re-indexing for a specific source
python3 gradient_kb_manage.py --reindex --kb-uuid "your-kb-uuid" --source-uuid "ds-uuid"
```

> **🦞 Pro tip: Auto-indexing.** If your KB has auto-indexing enabled, you can skip manual re-index triggers. The KB will detect changes in your Spaces bucket automatically. Configure it in the [DigitalOcean Console](https://cloud.digitalocean.com) → Knowledge Base → Settings.

---

### 🔍 Query the Knowledge Base

Search your indexed documents with semantic or hybrid queries. This is where the magic happens — your documents become answers.

```bash
# Basic query
python3 gradient_kb_query.py --query "What happened with the Q4 earnings?"

# Control number of results
python3 gradient_kb_query.py --query "Revenue trends" --num-results 20

# Tune hybrid search balance (see below)
python3 gradient_kb_query.py --query "$CAKE price movement" --alpha 0.5

# JSON output (for piping to other tools)
python3 gradient_kb_query.py --query "SEC filings summary" --json
```

**Direct API call:**
```bash
curl -s https://kbaas.do-ai.run/v1/{kb-uuid}/retrieve \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What happened with Q4 earnings?",
    "num_results": 10,
    "alpha": 0.5
  }'
```

📖 *[KB retrieval API](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/#query-a-knowledge-base)*

---

### 🎛️ The `alpha` Parameter — Hybrid Search Tuning

This is the secret sauce. The `alpha` parameter controls the balance between **lexical** (keyword) and **semantic** (meaning) search:

| Alpha | Behavior | Best For |
|-------|----------|----------|
| `0.0` | Pure lexical (keyword matching) | Exact terms: ticker symbols, filing numbers, dates |
| `0.5` | Balanced hybrid | General research queries |
| `1.0` | Pure semantic (meaning-based) | Open-ended: "what happened with...", "summarize..." |

> **🦞 Rule of claw:** Start at `0.5`. Go lower when searching for specific things (`$CAKE`, `10-K`, `2026-02-15`). Go higher when exploring ideas ("What's the market sentiment?").

---

### 🧠 RAG-Enhanced Queries

The full pipeline: query the KB → build a context prompt → call an LLM to synthesize. One command, complete answers with citations.

```bash
python3 gradient_kb_query.py \
  --query "Summarize all research on $CAKE" \
  --rag \
  --model "openai-gpt-oss-120b"
```

This automatically:
1. 🔍 Queries the Knowledge Base for relevant documents
2. 📝 Builds a prompt with the retrieved context
3. 🤖 Calls the LLM to synthesize an answer

> **Note:** RAG queries call the [Gradient Inference API](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/) under the hood, so you'll need `GRADIENT_API_KEY` set. If you have the `gradient-inference` skill loaded too, you're all set.

---

## Advanced Configuration

### Embedding Models & Chunking

When creating a Knowledge Base, you can choose how documents are split into searchable chunks:

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Section-based** | Splits on document structure (headings, paragraphs) | Structured reports |
| **Semantic** | Splits on meaning boundaries | Narrative content |
| **Hierarchical** | Preserves document hierarchy in chunks | Technical docs |
| **Fixed-length** | Equal-sized chunks | Uniform data |

Configure these in the [DigitalOcean Console](https://cloud.digitalocean.com) when creating the KB, or via the API's `embedding_model` and chunking parameters.

📖 *[KB configuration options](https://docs.digitalocean.com/products/gradient-ai-platform/details/features/#retrieval-augmented-generation-rag)*

---

## CLI Reference

All scripts accept `--json` for machine-readable output.

```
gradient_spaces.py      --upload FILE | --list | --delete KEY
                        [--bucket NAME] [--prefix PATH] [--key KEY] [--json]

gradient_kb_manage.py   --list | --create | --show | --delete
                        | --list-sources | --add-source | --reindex
                        [--kb-uuid UUID] [--source-uuid UUID]
                        [--name NAME] [--region REGION] [--bucket NAME]
                        [--prefix PATH] [--json]

gradient_kb_query.py    --query TEXT [--kb-uuid UUID] [--num-results N]
                        [--alpha F] [--rag] [--model ID] [--json]
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DO_API_TOKEN` | ✅ | DO API token (scopes: GenAI + Spaces) |
| `DO_SPACES_ACCESS_KEY` | ✅ | Spaces access key |
| `DO_SPACES_SECRET_KEY` | ✅ | Spaces secret key |
| `DO_SPACES_ENDPOINT` | Optional | Spaces endpoint (default: `https://nyc3.digitaloceanspaces.com`) |
| `DO_SPACES_BUCKET` | Optional | Default bucket name |
| `GRADIENT_KB_UUID` | Optional | Default KB UUID (saves typing `--kb-uuid` every time) |
| `GRADIENT_API_KEY` | For RAG | Needed when using `--rag` for LLM synthesis |

## External Endpoints

| Endpoint | Purpose |
|----------|---------|
| `https://kbaas.do-ai.run/v1/{uuid}/retrieve` | KB retrieval API |
| `https://api.digitalocean.com/v2/gen-ai/knowledge_bases/` | KB management API |
| `https://{region}.digitaloceanspaces.com` | DO Spaces (S3-compatible) |

## Security & Privacy

- Your `DO_API_TOKEN` is sent as a Bearer token to `api.digitalocean.com` and `kbaas.do-ai.run`
- Spaces credentials are used for S3-compatible uploads to `{region}.digitaloceanspaces.com`
- Documents you upload become **private** in your Spaces bucket by default
- KB queries are scoped to your account — no cross-tenant access
- No credentials or data are sent to any third-party endpoints

## Trust Statement

> By using this skill, documents and queries are sent to DigitalOcean's Knowledge Base
> and Spaces APIs. Only install if you trust DigitalOcean with the documents you index.

## Important Notes

- Documents uploaded to Spaces are **private by default**
- Re-indexing is **best-effort** — if the API call fails, auto-indexing kicks in on its own schedule
- The retrieval API returns document **chunks**, not full documents
- Deleting a KB is **permanent** — the indexed data is gone. The source files in Spaces are not affected.
