# exa-search-rust

An [OpenClaw](https://openclaw.ai) skill for [Exa AI](https://exa.ai) search, written in Rust. A port of the [official Exa Python SDK](https://github.com/exa-labs/exa-py) to a self-contained native binary — full core API coverage (neural search, find similar, page contents), hardened input validation, and blazingly fast 300ms searches.

> **Looking for the OpenClaw plugin version?** → [openclaw-exa-plugin](https://github.com/Prompt-Surfer/openclaw-exa-plugin) (registers `web_search_exa` as a native tool, no Bash required)

---

## Install

```bash
bash install.sh
```

Builds the Rust binary from [openclaw-exa-plugin](https://github.com/Prompt-Surfer/openclaw-exa-plugin) (local source or auto-cloned) and installs to `~/.openclaw/workspace/skills/exa-search/`.

Then add your API key to `~/.openclaw/workspace/.env`:

```bash
echo "EXA_API_KEY=your_key_here" >> ~/.openclaw/workspace/.env
```

---

## Usage

Agents read `SKILL.md` for full instructions. Quick reference:

```bash
# Search
echo '{"query":"rust async programming","num_results":5,"livecrawl":"never"}' \
  | EXA_API_KEY=$(grep -E "^EXA_API_KEY=" ~/.openclaw/workspace/.env | cut -d= -f2 | tr -d '"') \
  ~/.openclaw/workspace/skills/exa-search/bin/exa-search | jq .

# Find similar pages
echo '{"action":"find_similar","url":"https://doc.rust-lang.org","num_results":3}' \
  | EXA_API_KEY=... ~/.openclaw/workspace/skills/exa-search/bin/exa-search | jq .

# Fetch page contents
echo '{"action":"get_contents","urls":["https://example.com"]}' \
  | EXA_API_KEY=... ~/.openclaw/workspace/skills/exa-search/bin/exa-search | jq .
```

---

## Defaults & Configuration Reference

All fields are optional unless marked **required**. Omitting a field uses the default shown.

### Action routing

| Field | Type | Default | Description |
|---|---|---|---|
| `action` | `string` | `"search"` | `"search"` · `"find_similar"` · `"get_contents"` |

---

### Search (`action: "search"`)

| Field | Type | Default | Description |
|---|---|---|---|
| `query` | `string` | — | **Required.** What to search for |
| `num_results` | `integer` | `10` | Number of results (max `50`) |
| `type` | `string` | `"auto"` | `"auto"` · `"neural"` · `"keyword"` · `"fast"` · `"deep"` · `"instant"` |
| `use_autoprompt` | `bool` | `false` | Let Exa rewrite query for better neural results |
| `category` | `string` | none | `"research paper"` · `"news"` · `"tweet"` · `"github"` · etc. |
| `include_domains` | `string[]` | none | Restrict to these domains |
| `exclude_domains` | `string[]` | none | Block these domains |
| `start_published_date` | `string` | none | ISO 8601 — only results published after |
| `end_published_date` | `string` | none | ISO 8601 — only results published before |
| `start_crawl_date` | `string` | none | Filter by crawl date (not publish date) |
| `end_crawl_date` | `string` | none | Filter by crawl date |
| `include_text` | `string[]` | none | Results must contain these strings |
| `exclude_text` | `string[]` | none | Results must not contain these strings |
| `user_location` | `string` | none | ISO country code for localised results (e.g. `"AU"`) |
| `moderation` | `bool` | `false` | Enable Exa content moderation filter |
| `additional_queries` | `string[]` | none | Extra queries merged into the search |

---

### Find Similar (`action: "find_similar"`)

| Field | Type | Default | Description |
|---|---|---|---|
| `url` | `string` | — | **Required.** Seed URL to find similar pages for |
| `num_results` | `integer` | `10` | Number of results (max `50`) |
| `exclude_source_domain` | `bool` | `false` | Exclude results from the seed URL's domain |
| `category` | `string` | none | Same options as Search |
| `include_domains` | `string[]` | none | Same as Search |
| `exclude_domains` | `string[]` | none | Same as Search |
| `start_published_date` | `string` | none | Same as Search |
| `end_published_date` | `string` | none | Same as Search |

---

### Get Contents (`action: "get_contents"`)

| Field | Type | Default | Description |
|---|---|---|---|
| `urls` | `string[]` | — | **Required.** One or more URLs to fetch |

---

### Contents options (Search, Find Similar, Get Contents)

Control what content is returned with each result. Pass as a `contents` object, or use the top-level shorthands below.

#### `contents` object

| Field | Type | Default | Description |
|---|---|---|---|
| `text` | `object \| bool` | `{max_characters: 10000}` | Full page text. Set `false` to disable, or pass `{max_characters: N}` |
| `highlights` | `object \| bool` | off | Relevant excerpts. `{num_sentences: 3, highlights_per_url: 2}` |
| `summary` | `object \| bool` | off | AI summary. `{query: "key takeaways"}` or `true` for auto |
| `livecrawl` | `string` | `"never"` | `"never"` · `"fallback"` · `"preferred"` · `"always"` · `"auto"` |
| `livecrawl_timeout` | `integer` | none | Timeout in ms for live crawl requests |
| `filter_empty_results` | `bool` | `false` | Drop results with no text content |
| `subpages` | `integer` | none | Also fetch N subpages per URL |
| `subpage_target` | `string \| string[]` | none | Restrict subpage fetch to this path pattern |
| `extras.links` | `integer` | none | Return up to N extracted links per result |
| `max_age_hours` | `integer` | none | Skip cached content older than N hours |

#### `livecrawl` guidance

| Value | Speed | Use when |
|---|---|---|
| `"never"` | ~300–600ms ⚡ | Docs, reference material, anything stable |
| `"fallback"` | ~800–1200ms | Good general default — cache first, crawl if missing |
| `"preferred"` | ~1–2s | You want fresh content but cache is acceptable fallback |
| `"always"` | ~1–3s | Breaking news, rapidly-changing pages |

#### Top-level shorthands (alternative to `contents` object)

| Field | Type | Notes |
|---|---|---|
| `max_chars` | `integer` | Shorthand for `contents.text.max_characters` |
| `filter_empty_results` | `bool` | Same as `contents.filter_empty_results` |
| `extras` | `object` | Same as `contents.extras` |
| `max_age_hours` | `integer` | Same as `contents.max_age_hours` |

---

### Limits & validation

| Constraint | Value |
|---|---|
| Max `num_results` | 50 |
| Max stdin size | 1 MB |
| Max response body | 10 MB |
| API key format | UUID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) |

---

### Output

On success, stdout receives a JSON object with `ok: true`. On error, stderr receives `{"ok": false, "error": "..."}` and exit code is `1`.

**Search / find\_similar:**
```json
{
  "ok": true,
  "action": "search",
  "results": [...],
  "resolved_search_type": "neural",
  "search_time_ms": 412,
  "cost_dollars": "...",
  "formatted": "## [Title](url)\n\ntext\n\n---"
}
```

**Get contents:**
```json
{
  "ok": true,
  "action": "get_contents",
  "results": [...],
  "cost_dollars": "..."
}
```

---

## Benchmark

| Mode | Avg | Peak |
|---|---|---|
| Instant (`livecrawl: "never"`) | ~440ms | **308ms** |
| Default | ~927ms | 629ms |
| Exa MCP (`npx` cached) | ~5,747ms | — |

**Peak 308ms — 18.7× faster than MCP.** See [openclaw-exa-plugin](https://github.com/Prompt-Surfer/openclaw-exa-plugin#benchmark) for full benchmark table.

---

## Structure

```
.
├── SKILL.md          # Agent instructions — actions, params, output format
├── install.sh        # Build binary from bundled source + install to workspace
├── Cargo.toml        # Rust crate
├── src/              # Rust source — self-contained, no external repo needed
│   ├── main.rs
│   ├── client.rs
│   ├── protocol.rs
│   └── types/
└── bin/
    └── exa-search    # Pre-built Linux x86_64 binary (also buildable via install.sh)
```

---

## Roadmap

### ✅ Implemented (Python SDK parity)

| Feature | Python SDK | This repo |
|---|---|---|
| `search` | ✅ | ✅ |
| `find_similar` | ✅ | ✅ |
| `get_contents` | ✅ | ✅ |
| `text` contents | ✅ | ✅ |
| `highlights` contents | ✅ | ✅ |
| `summary` contents | ✅ | ✅ |
| `livecrawl` + `livecrawl_timeout` | ✅ | ✅ |
| `filter_empty_results` | ✅ | ✅ |
| `subpages` / `subpage_target` | ✅ | ✅ |
| `extras.links` | ✅ | ✅ |
| `max_age_hours` | ✅ | ✅ |
| Date filters (`start/end_published_date`, `start/end_crawl_date`) | ✅ | ✅ |
| Domain filters (`include/exclude_domains`) | ✅ | ✅ |
| Text filters (`include/exclude_text`) | ✅ | ✅ |
| `category` | ✅ | ✅ |
| `use_autoprompt` | ✅ | ✅ |
| `user_location` | ✅ | ✅ |
| `moderation` | ✅ | ✅ |
| `additional_queries` | ✅ | ✅ |
| `exclude_source_domain` (find\_similar) | ✅ | ✅ |

---

### 🗺️ Not Yet Implemented

| Feature | Notes |
|---|---|
| `answer` / `stream_answer` | Pay-per-use ($5/1k). Skipped — Claude + Perplexity already handle this. Could be added behind a flag. |
| `search_and_contents` / `find_similar_and_contents` | Convenience wrappers. Equivalent behaviour already available: pass a `contents` object to `search` or `find_similar`. |
| `image_links` | Excluded by design — adds noise in LLM contexts. |
| OpenAI-compatible wrapper (`wrap`) | Drop-in `openai.Client` replacement. Out of scope for an OpenClaw skill. |
| Websets client | Exa's structured data extraction product. Separate API surface. |
| Research client | Exa's deep research product. Separate API surface. |
| Entity types (`Company`, `Person`) for `find_similar` | Typed seed entities instead of URLs. Planned. |
| `context` contents | Deprecated in Exa Python SDK. Not planned. |

---

### 🔒 Added Beyond the Python SDK

These hardening features are not in the official Exa Python SDK:

| Feature | Description |
|---|---|
| **UUID API key validation** | Key is validated as lowercase hex UUID at startup — fails fast with a clear error, not a cryptic 401 |
| **1 MB stdin cap** | Prevents memory exhaustion from runaway input |
| **`num_results` hard cap (50)** | Mirrors Exa's server-side limit locally — rejects bad inputs before making a network call |
| **10 MB response body cap** | Prevents unbounded memory growth on large crawled pages |
| **Typed `SearchType` enum** | `auto·neural·keyword·fast·deep·instant` — invalid values rejected at parse time, not silently ignored |
| **Typed `LivecrawlOption` enum** | `never·fallback·preferred·always·auto` — same strict validation |
| **Errors to stderr + exit code 1** | Proper UNIX semantics — stdout is always clean JSON on success; errors never pollute the output stream |
