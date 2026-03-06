# 🧠 Data Pods

**Modular portable database pods — your AI memory, your rules.**

Data Pods are SQLite-based knowledge bases you own. Zip them up, move them anywhere, share selectively. No vendor lock-in. No cloud dependencies. Just your data, portable.

---

## Why Data Pods?

- **Portable** — Zip a pod, move to another machine, keep working
- **Owned** — SQLite file, no proprietary formats
- **Consented** — Agents only access what you permit
- **Composable** — Multiple pods (scholar, health, projects) work together
- **GDPR-friendly** — Data stays local, export anytime

---

## What's Inside a Pod?

```
my-pod/
├── data.sqlite       # Your data (notes, embeddings, custom tables)
├── metadata.json     # Pod info (name, type, created, version)
├── embeddings/      # Vector store (future)
└── manifest.yaml    # Access rules
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/init-v/data-pods
cd data-pods
```

### 2. Run

```bash
# List pods
python3 pod.py list

# Create a pod
python3 pod.py create my-research --type scholar

# Add a note
python3 pod.py add my-research \
  --title "Transformer Architecture" \
  --content "The transformer uses self-attention..." \
  --tags "ai,machine-learning"

# Search
python3 pod.py query my-research --text "transformer"

# Export for sharing
python3 pod.py export my-research --output my-research.zip
```

---

## v0.2 — Document Ingestion with Embeddings

```bash
# Install dependencies
pip install PyPDF2 python-docx pillow pytesseract sentence-transformers

# Ingest a folder of documents
python3 ingest.py ingest research ./documents/

# Semantic search across all documents
python3 ingest.py search research "what did I read about transformers?"

# List ingested documents
python3 ingest.py list research
```

### Supported Formats
- PDF (via PyPDF2)
- TXT, MD, Markdown
- DOCX (via python-docx)
- Images: PNG, JPG (OCR via pytesseract)

### Features
- Auto-chunks large documents for better retrieval
- Embeddings for semantic search
- File hash prevents duplicate ingestion
- Citations with source filename

---

## Commands

| Command | Description |
|---------|-------------|
| `pod.py list` | Show all pods |
| `pod.py create <name> --type <type>` | Create new pod |
| `pod.py add <pod> --title "..." --content "..."` | Add note |
| `pod.py query <pod> --text "..."` | Search notes |
| `pod.py query <pod> --sql "SELECT *..."` | Raw SQL |
| `pod.py export <pod> --output <file>` | Export as ZIP |

---

## 🔐 Consent Layer

**Agents only access what you permit.**

Data Pods include a built-in consent layer. Before any agent can query your pods, you must grant explicit permission.

### Consent Commands

```bash
# Grant an agent access to a pod
python3 consent.py grant --pod my-research --agent openclaw

# Grant with expiration (30 days)
python3 consent.py grant --pod my-research --agent openclaw --expires 30

# List all grants
python3 consent.py list

# Check if agent has access (returns 0 if yes, 1 if no)
python3 consent.py check --pod my-research --agent openclaw

# Revoke access
python3 consent.py revoke --pod my-research --agent openclaw
```

### How It Works

1. Agent requests data from a pod
2. Consent layer checks for active grant
3. If no grant → access denied
4. If expired grant → access denied
5. All queries logged for audit

### Storage

Grants stored in `~/.config/data-pods/consents/grants.json`

---

## Pod Types

- **scholar** — Research papers, papers, embeddings
- **health** — Wearable data, biometrics (consent-only)
- **projects** — Workspace knowledge
- **shared** — Family/group data with permissions

---

## The Vision

AI agents need memory. But cloud APIs = dependence.

Data Pods give you:
1. **Sovereignty** — Your data, your machine
2. **Portability** — Move pods between devices
3. **Composability** — Multiple pods, one access layer
4. **Consent** — You control what agents see

We're building v0.1. Follow along.

---

## Roadmap

- [x] v0.1 — SQLite + notes + export
- [ ] v0.2 — Embeddings + vector search
- [ ] v0.3 — Natural language query interface
- [ ] v0.4 — OpenClaw skill integration
- [ ] v1.0 — Sync + multi-device

---

## Contributing

Open source. MIT License.

Issues welcome. PRs welcome.

---

## Contact

- X: @vinicius_init
- Discord: VR Global Enterprises (see bio)
