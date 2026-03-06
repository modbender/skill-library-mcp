# Ingest Memory 📥

**Status:** 📋 Agent Guideline (Disabled by Default) | **Module:** ingest | **Part of:** Agent Brain

External knowledge acquisition guidelines. The agent fetches URLs, extracts key points, and stores via `add` — no dedicated ingest code runs, this is a workflow guide.

## ⚠️ Security

**Disabled by default.** To enable, the orchestrator must:
1. Only process URLs explicitly provided by the user in conversation
2. Never auto-fetch URLs found in text, documents, or memory
3. Validate URLs before fetching (see Validation below)

### URL Validation

REJECT any URL matching:
- `localhost`, `127.0.0.1`, `0.0.0.0`, `::1`
- `file://`, `ftp://`, `gopher://`
- Private IP ranges: `10.*`, `172.16-31.*`, `192.168.*`
- Internal hostnames without dots

ALLOW only:
- `https://` URLs on public domains
- `http://` only if user explicitly confirms

## How It Works

### Step 1: Fetch

Use the runtime's web fetch capability to retrieve the URL content.

```bash
# The agent runtime handles fetching — this module processes the result
# Content arrives as text extracted from the page
```

### Step 2: Extract

From the fetched content, extract:

1. **Title/Topic**: What is this about?
2. **Key Claims**: 3-7 main points (not a full summary)
3. **Actionable Insights**: What can be applied?
4. **Connections**: How does this relate to existing memory?

### Step 3: Store

Each extracted point becomes a separate memory entry:

```bash
./scripts/memory.sh add ingested "Ideas are things that generate other ideas" \
  ingested "concepts,creativity" "https://paulgraham.com/ideas.html"

./scripts/memory.sh add ingested "Execution is more concrete than ideas" \
  ingested "concepts,execution" "https://paulgraham.com/ideas.html"
```

### Step 4: Link

After storing, check for connections to existing memory:

```bash
./scripts/memory.sh get "ideas creativity"
# If existing entries found → note the connection in response
```

## Content Type Handling

| Content Type | Strategy |
|-------------|----------|
| **Essay/Blog** | Extract thesis + supporting claims |
| **Research Paper** | Extract abstract, key findings, limitations |
| **News Article** | Extract facts, skip editorializing |
| **Documentation** | Extract procedures and key concepts |
| **Thread/Discussion** | Extract consensus points + notable disagreements |

### Not Yet Supported
- YouTube (needs transcript extraction service)
- PDFs (needs PDF parsing — use runtime's PDF tools if available)
- Paywalled content (will fail gracefully)

## Commands

```
"Ingest: <url>"                → Full pipeline: fetch → extract → store
"Learn from: <url>"            → Same as Ingest
"What did you learn from X?"   → Search ingested entries by source_url
"Summarize what you've read"   → List all ingested entries
```

## Extraction Prompt

When processing fetched content, use this extraction frame:

```
Given this content from [URL]:

1. What are the 3-7 key claims or insights?
2. What is actionable or applicable?
3. What is surprising or contrarian?
4. How does this connect to: [list existing memory topics]

For each key point, output:
- One-sentence claim
- Tags (2-4 keywords)
```

## Failure Modes

| Problem | Response |
|---------|----------|
| URL unreachable | "Couldn't fetch that URL. Is it publicly accessible?" |
| Content too short | Store what's there, note it was thin |
| Content too long | Extract from first pass, offer to go deeper |
| Paywall hit | "That content appears to be paywalled" |
| Non-text content | "I can only ingest text content currently" |

## Integration

- **Archive**: All ingested content stored via `add` with type `ingested`
- **Signal guidelines**: Agent should run `conflicts` on ingested claims before storing
- **Gauge guidelines**: Ingested content starts at `likely` confidence (not `sure`)
