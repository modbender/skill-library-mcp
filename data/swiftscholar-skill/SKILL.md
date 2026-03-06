---
name: swiftscholar-skill
description: Integrates the SwiftScholar HTTP API for searching, submitting, and analyzing academic papers. Use when the user wants to search literature, submit PDFs/URLs for parsing, retrieve analyses, manage favorites, or inspect SwiftScholar account usage programmatically.
---

# SwiftScholar Skill (`swiftscholar-skill`)

This skill enables the agent to use the **SwiftScholar HTTP API** to search, submit, analyze, and manage academic papers.  
Prefer the JSON-first `/api/tools/*` endpoints instead of deprecated `/api/mcp/tools/*` endpoints.

Basic information:

- **Base URL**: `https://www.swiftscholar.net`
- **Auth**: `Authorization: Bearer <API_KEY>`
- **Spec version**: OpenAPI 3.1.0 (`SwiftScholar HTTP API 1.0.0`)

> Never expose the API key in natural language responses; only include it in actual HTTP headers.

---

## 1. When to use this skill

Use the SwiftScholar API in these situations:

- The user wants to:  
  - **search academic papers** (keyword or semantic/vector search)  
  - **submit paper URLs / PDFs** for parsing  
  - **retrieve structured markdown analysis** or raw markdown  
  - **manage / inspect favorites and favorite folders**  
  - **inspect parse quotas, usage, and available analysis models**

Typical trigger phrases (examples):

- “literature search”, “keyword search paper”, “semantic search paper”
- “parse this paper PDF/URL”, “analyze this paper”
- “get detailed analysis / markdown for this paper”
- “SwiftScholar favorites / favorite folders”
- “SwiftScholar account usage / quota / parse history”

---

## 2. Authentication and calling conventions

### 2.1 Authentication

- All `/api/tools/*` endpoints use **Bearer tokens**:
  - Header: `Authorization: Bearer <SWIFTSCHOLAR_API_KEY>`
- The agent must not reveal or infer the key in natural language responses.

### 2.2 General request conventions

- **HTTP method**: all tool endpoints are `POST`.
- **Content-Type**:
  - JSON requests: `application/json`
  - PDF upload: `multipart/form-data` with `file` as binary PDF
- **Error handling**:
  - JSON responses follow the `ToolApiResponse` structure:
    - `ok: boolean` (always present)
    - `data: object` (present on success)
    - `error: string` (may be present on failure)
  - After a call:
    - If `ok == false` or `error` is present, briefly explain the failure to the user and suggest next steps (e.g., adjust parameters, narrow filters).

---

## 3. Core capabilities and endpoints

This section is organized by **capability**, not by URL, to help the agent choose appropriate tools.  
All listed endpoints live under `paths./api/tools/...`.

### 3.1 Paper tags and basic browsing

1. **List all paper tags (with IDs and usage counts)**

   - Endpoint: `POST /api/tools/paper_tags_list`
   - Body: `{}` (no parameters)
   - Purpose:
     - When recommending tag filters or constructing complex queries, first list available tags and their IDs.

2. **Paginate accessible papers**

   - Endpoint: `POST /api/tools/papers_paginate`
   - Body fields (partial):
     - `page: integer >= 1` (default 1)
     - `pageSize: integer 1–50` (default 10)
     - `licenses: string[]` (may include `'none'`)
     - `publishedFrom: string (YYYY-MM-DD)`
     - `publishedTo: string (YYYY-MM-DD)`
   - Purpose:
     - Browse paper lists by time or license as a base for search results or user-library browsing.

### 3.2 Search: keyword search vs vector (semantic) search

1. **Keyword search (literal string matching)**

   - Endpoint: `POST /api/tools/papers_search_keyword`
   - Key body fields:
     - `query: string` (required; search string)
     - `page, pageSize` (same semantics as `papers_paginate`)
     - `tags: string[]` / `tagNames: string[]` (tag filters)
     - `tagMode: "and" | "or"` (default `"or"`)
     - `licenses, publishedFrom, publishedTo` (same as above)
   - Usage guidance:
     - Prefer this when the user provides explicit keywords, title fragments, or phrases.
     - Explain that this is **literal matching**, ideal for precise lookup.

2. **Vector search (semantic search)**

   - Endpoint: `POST /api/tools/papers_search_vector`
   - Key body fields:
     - `query: string` (required; natural-language query)
     - `limit: integer 1–30` (default 10)
     - Other filters as in `papers_search_keyword`
   - Usage guidance:
     - Use when the user describes **fuzzy concepts**, research themes, or questions (e.g., “recent progress of LLMs in medical imaging”).
     - Clarify that this is **semantic search**, better for “finding related papers” without exact title matches.

### 3.3 Submitting papers: URL / PDF / batch URLs

1. **Submit a paper by URL**

   - Endpoint: `POST /api/tools/paper_submit_url`
   - Body fields:
     - `url: string` (required; paper source page or PDF URL)
     - `modelId: string` (optional; PDF analysis model)
     - `force: boolean` (force re-parse)
     - `favoriteFolderId: string | null` (favorites folder, `null` for root)
     - `favoriteNote: string` (favorites note)
   - Usage guidance:
     - Use when the user provides a paper page URL or direct PDF URL and wants parsing, analysis, or saving to favorites.
     - Mention that parsing may take time and suggest how to check results later if needed.

2. **Submit or link a PDF file**

   There are two main modes:

   - JSON API:
     - Endpoint: `POST /api/tools/paper_submit_pdf`
     - JSON body:
       - `pdfUrl: string` OR `pdfBase64: string` (one of them is required)
       - `fileName: string` (optional)
       - Other fields as in `paper_submit_url` (`modelId`, `force`, `favoriteFolderId`, `favoriteNote`)
     - Note: the spec explicitly says “provide either `pdfUrl` or `pdfBase64`.”

   - Multipart upload:
     - Same endpoint with `multipart/form-data`:
       - `file: binary` (required; PDF file content)
       - Optional: `modelId`, `force`, `favoriteFolderId`, `favoriteNote`
   - Usage guidance:
     - Use this when the user has a local PDF or remote PDF URL and wants it parsed.

3. **Batch submit URLs**

   - Endpoint: `POST /api/tools/papers_submit_urls`
   - Body fields:
     - `urls: string[] | string` (array or newline-separated string)
     - `modelId: string` (optional; applied to all URLs)
     - `notifyOnComplete: boolean` (default false)
     - `force: boolean` (default false)
     - `favoriteFolderId: string | null`
     - `favoriteNote: string`
   - Usage guidance:
     - Use when the user provides many paper URLs and wants them parsed, saved, or both in batch.

### 3.4 Reading and analysis: markdown analysis / raw markdown / PDF link

1. **Get markdown-formatted paper analysis**

   - Endpoint: `POST /api/tools/paper_analysis_markdown`
   - Body fields:
     - `paperId: string` (required)
     - `language: "auto" | "zh" | "en" | "both"` (default `"auto"`)
     - `scope: "public" | "me" | "auto"` (default `"public"`)
   - Usage guidance:
     - Use when the user wants **structured, readable analysis** (summary, structure, key points).
     - Set `language` according to the user’s preference:
       - For Chinese users, prefer `"zh"` or `"both"`;
       - If unsure, use `"auto"`.

2. **Get the raw markdown source for a paper**

   - Endpoint: `POST /api/tools/paper_markdown_raw`
   - Body fields:
     - `paperId: string` (required)
     - `maxChars: integer (500–120000)` (optional; truncation)
   - Usage guidance:
     - Prefer this when the user wants to do custom processing, re-summarization, or extraction of formulas/tables.
     - For very long papers, set a reasonable `maxChars` and inform the user if the content was truncated.

3. **Get a guarded PDF download link**

   - Endpoint: `POST /api/tools/paper_pdf_link`
   - Body fields:
     - `paperId: string` (required)
   - Usage guidance:
     - Use when the user wants to download or locally open the PDF.
     - Respect copyright and visibility rules; only guide the user to links the API has authorized.

---

### 3.5 Favorite folders and favorite papers

1. **List favorite folders**

   - Endpoint: `POST /api/tools/paper_favorite_folders`
   - Body: `{}`
   - Purpose:
     - Get folder IDs, parent/child relationships, and paths to help the user organize and target save locations.

2. **List favorite papers**

   - Endpoint: `POST /api/tools/paper_favorites_list`
   - Body fields:
     - `page, pageSize` (pagination; 1–50)
     - `folderId: string | null` (`null` for root; omit for all folders)
     - `includeDescendants: boolean` (default false)
     - `search: string` (search in notes and titles)
   - Purpose:
     - Browse the user’s personal library or filter by notes and titles.

3. **Save or update a favorite entry**

   - Endpoint: `POST /api/tools/paper_favorite_save`
   - Body fields:
     - `paperId: string` (required)
     - `folderId: string | null` (target folder; `null` for root; omit to reuse existing folder if present)
     - `note: string` (optional note)
   - Usage guidance:
     - After identifying important papers, suggest saving them to an appropriate folder with a short descriptive note.

---

### 3.6 Analysis models and account usage

1. **List available PDF analysis models**

   - Endpoint: `POST /api/tools/paper_analysis_models`
   - Body: `{}`
   - Purpose:
     - Show available models under the current plan (including `consumeUnits` and per-parse extra price) to help choose `modelId`.
     - Use when the user is concerned about cost or model quality; list models and give recommendations.

2. **Summarize account quota and points**

   - Endpoint: `POST /api/tools/account_usage_summary`
   - Body: `{}`
   - Purpose:
     - Summarize current parse quota and points so the user knows how many more papers can be parsed.

3. **List parse history**

   - Endpoint: `POST /api/tools/parse_history_list`
   - Body fields:
     - `page, pageSize` (1–100)
     - `chargeMode: string` (optional, e.g., `FREE` or `BALANCE`)
   - Purpose:
     - Show parse usage records for the last 30 days (which papers, when parsed, potential charges).

---

## 4. Recommended workflows

### 4.1 From research question to paper recommendations (search workflow)

1. Clarify the user’s research question or topic in natural language.
2. If the description is conceptual or fuzzy:
   - First call **vector search** `/api/tools/papers_search_vector` to focus on conceptual relevance.
3. If the user provides concrete keywords or title fragments:
   - Use **keyword search** `/api/tools/papers_search_keyword`.
4. Organize results by relevance or recency:
   - Present titles, years, and short descriptions of main contributions, plus `paperId` for follow-up.
5. For selected papers:
   - Call `/api/tools/paper_analysis_markdown` for detailed analysis; or
   - Call `/api/tools/paper_markdown_raw` for fine-grained custom processing.

### 4.2 Submit a new paper and obtain analysis (submission + analysis workflow)

1. When the user provides a URL or PDF:
   - URL: use `/api/tools/paper_submit_url`
   - Local or remote PDF: use `/api/tools/paper_submit_pdf`
2. If the user specifies a folder or note:
   - Include `favoriteFolderId` and `favoriteNote` in the request.
3. Wait for parsing to complete (if the API is asynchronous, rely on history or documented IDs):
   - Once a `paperId` is available, call `/api/tools/paper_analysis_markdown`.
4. Summarize the analysis in terms of:
   - Core contributions, methods, datasets, conclusions, and how they relate to the user’s research question.

### 4.3 Manage personal literature library (favorites workflow)

1. When the user needs an overview of their favorites structure:
   - Call `/api/tools/paper_favorite_folders` to list all folders.
2. To view favorites by folder or search string:
   - Call `/api/tools/paper_favorites_list` with appropriate `folderId` and `search`.
3. When important long-term papers are identified:
   - Call `/api/tools/paper_favorite_save` to create or update favorite records.
4. In summaries:
   - Suggest organizing folders by topic or project to simplify future retrieval.

---

## 5. Practical tips

- **Prefer `/api/tools/*`:**  
  `/api/mcp/tools/*` endpoints are marked `deprecated` in the OpenAPI spec; avoid relying on them for new integrations.
- **Validate parameters:**  
  Respect OpenAPI constraints (pagination limits, required fields) to avoid unnecessary retries.
- **Post-process responses:**  
  After each call, convert raw JSON into user-friendly output:
  - Concise paper lists (title + year + short description);
  - Clear bullet-point summaries (methods, results, limitations);
  - Direct conclusions and recommendations relevant to the user’s question (not just raw data dumps).

