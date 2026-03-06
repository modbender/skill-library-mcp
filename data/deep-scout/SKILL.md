---
name: deep-scout
description: "Multi-stage deep intelligence pipeline (Search → Filter → Fetch → Synthesize). Turns a query into a structured research report with full source citations."
metadata:
  {"openclaw": {"requires": {"bins": ["bash", "python3"], "anyBins": ["timeout", "gtimeout"]}}}
---

# Deep Scout: Multi-Stage Intelligence Pipeline

Search → Filter → Fetch → Synthesize. Turns a natural-language query into a structured research report with full source citations.

## 🚀 Usage

```
/deep-scout "Your research question" [--depth 5] [--freshness pw] [--country US] [--style report]
```

### Options
| Flag | Default | Description |
|------|---------|-------------|
| `--depth N` | 5 | Number of URLs to fully fetch (1–10) |
| `--freshness` | `pw` | `pd`=past day, `pw`=past week, `pm`=past month, `py`=past year |
| `--country` | `US` | 2-letter country code for Brave search |
| `--language` | `en` | 2-letter language code |
| `--search-count` | 8 | Total results to collect before filtering |
| `--min-score` | 4 | Minimum relevance score to keep (0–10) |
| `--style` | `report` | `report` \| `comparison` \| `bullets` \| `timeline` |
| `--dimensions` | `auto` | Comparison dimensions (comma-separated, for `--style comparison`) |
| `--output FILE` | stdout | Write report to file |
| `--no-browser` | — | Disable browser fallback |
| `--no-firecrawl` | — | Disable Firecrawl fallback |

---

## 🛠️ Pipeline — Agent Loop Instructions

When this skill is invoked, execute the following four-stage pipeline:

---

### Stage 1: SEARCH

Call `web_search` with:
```
query: <user query>
count: <search_count>
country: <country>
search_lang: <language>
freshness: <freshness>
```

Collect: title, url, snippet for each result.  
If fewer than 3 results returned, retry with `freshness: "py"` (relaxed).

---

### Stage 2: FILTER

Load `prompts/filter.txt`. Replace template vars:
- `{{query}}` → the user's query
- `{{freshness}}` → freshness param
- `{{min_score}}` → min_score param
- `{{results_json}}` → JSON array of search results

Call the LLM with this prompt. Parse the returned JSON array.  
Keep only results where `keep: true`. Sort by score descending.  
Take top `depth` URLs as the fetch list.

**Deduplication:** Max 2 results per root domain (already handled in filter prompt).

---

### Stage 3: FETCH (Tiered Escalation)

For each URL in the filtered list:

**Tier 1 — web_fetch (fast):**
```
Call web_fetch(url)
If content length >= 200 chars → accept, trim to max_chars_per_source
```

**Tier 2 — Firecrawl (deep/JS):**
```
If Tier 1 fails or returns < 200 chars:
  Run: scripts/firecrawl-wrap.sh <url> <max_chars>
  If output != "FIRECRAWL_UNAVAILABLE" and != "FIRECRAWL_EMPTY" → accept
```

**Tier 3 — Browser (last resort):**
```
If Tier 2 fails:
  Call browser(action="open", url=url)
  Call browser(action="snapshot")
  Load prompts/browser-extract.txt, substitute {{query}} and {{max_chars_per_source}}
  Call LLM with snapshot content + extraction prompt
  If output != "FETCH_FAILED:..." → accept
```

**If all tiers fail:** Use the original snippet from Stage 1 search results. Mark as `[snippet only]`.

Store: `{ url: extracted_content }` dict.

---

### Stage 4: SYNTHESIZE

Choose prompt template based on `--style`:
- `report` / `bullets` / `timeline` → `prompts/synthesize-report.txt`
- `comparison` → `prompts/synthesize-comparison.txt`

Replace template vars:
- `{{query}}` → user query
- `{{today}}` → current date (YYYY-MM-DD)
- `{{language}}` → language param
- `{{source_count}}` → number of successfully fetched sources
- `{{dimensions_or_auto}}` → dimensions param (or "auto")
- `{{fetched_content_blocks}}` → build as:
  ```
  [Source 1] (url1)
  <content>
  ---
  [Source 2] (url2)
  <content>
  ```

Call LLM with the filled prompt. The output is the final report.

If `--output FILE` is set, write the report to that file. Otherwise, print to the channel.

---

## ⚙️ Configuration

Defaults are in `config.yaml`. Override via CLI flags above.

---

## 📂 Project Structure

```
skills/deep-scout/
├── SKILL.md                     ← This file (agent instructions)
├── config.yaml                  ← Default parameter values
├── prompts/
│   ├── filter.txt               ← Stage 2: relevance scoring prompt
│   ├── synthesize-report.txt    ← Stage 4: report/bullets/timeline synthesis
│   ├── synthesize-comparison.txt← Stage 4: comparison table synthesis
│   └── browser-extract.txt      ← Stage 3: browser snapshot extraction
├── scripts/
│   ├── run.sh                   ← CLI entrypoint (emits pipeline actions)
│   └── firecrawl-wrap.sh        ← Firecrawl CLI wrapper with fallback handling
└── examples/
    └── openclaw-acquisition.md  ← Example output: OpenClaw M&A intelligence
```

---

## 🔧 Error Handling

| Scenario | Handling |
|----------|----------|
| All fetch attempts fail | Use snippet from Stage 1; mark `[snippet only]` |
| Search returns 0 results | Retry with `freshness: py`; error if still 0 |
| Firecrawl not installed | `firecrawl-wrap.sh` outputs `FIRECRAWL_UNAVAILABLE`, skip silently |
| Browser tool unavailable | Skip Tier 3; proceed with available content |
| LLM synthesis exceeds context | Trim sources proportionally, prioritize high-score sources |
| Rate limit on Brave API | Wait 2s, retry once |

---

## 📋 Example Outputs

See `examples/openclaw-acquisition.md` for a full sample report.

---

*Deep Scout v0.1.0 · OpenClaw Skills · clawhub: deep-scout*
