---
name: bigcommerce-content-optimizer
description: >
  Autonomous BigCommerce product content optimizer. Bulk-update, rewrite, optimize,
  or generate product titles and descriptions on a BigCommerce store. Triggers on
  "optimize my BigCommerce products", "rewrite product descriptions", "update product
  content", "improve my store listings", "bulk update BigCommerce", or when BigCommerce
  API credentials (store hash, API token) are provided for content work. Handles the
  full lifecycle: fetching products page-by-page, generating improved content, updating
  the store, and tracking progress — all autonomously without stopping.
metadata:
  openclaw:
    requires:
      bins:
        - python3
    emoji: "🛒"
---

# BigCommerce Content Optimizer

Autonomous skill that fetches products from a BigCommerce store, generates optimized
titles and descriptions, and updates them back — one page at a time with full progress tracking.

## Prerequisites

The user must provide:
1. **Store Hash** — the BigCommerce store identifier (e.g., `abc123def`)
2. **API Token** — a BigCommerce API v3 token with `Products` read+write scope

## Setup

Before first use, install the requests library:

```bash
pip install requests --break-system-packages
```

The helper script is at: `~/.openclaw/workspace/skills/bigcommerce-content-optimizer/scripts/bc_optimizer.py`

Set `SCRIPT` as the full path to `bc_optimizer.py` for all commands below.

## Workflow — Autonomous Loop

**CRITICAL: Do NOT stop between pages. Process ALL pages continuously until done.**

### Step 1: Initialize

```bash
python3 $SCRIPT init --store-hash "STORE_HASH" --token "API_TOKEN" --limit 10
```

This creates `progress.json` in the current working directory and returns total product/page counts.
If `progress.json` already exists with `status: in_progress`, it resumes from the last unprocessed page.

### Step 2: For EACH page (loop until all done)

#### 2a. Fetch the page

```bash
python3 $SCRIPT fetch --store-hash "STORE_HASH" --token "API_TOKEN" --page PAGE_NUMBER --limit 10
```

Outputs `page_N_products.json` with product data.

#### 2b. Read products and generate content

Read the fetched JSON. For EACH product, generate:

- **New Title**: SEO-friendly, concise, under 70 characters. Capture the product essence.
- **New Description**: Compelling HTML description, 100-300 words. Use `<p>`, `<ul>`, `<li>` tags.
  Focus on benefits, use cases, value proposition. No inline styles, no scripts.

Consider: existing name/description, SKU, price, categories, brand, images.
Apply SEO best practices (natural keywords, not stuffing) and persuasive copywriting.
If the user gave brand voice guidelines, follow them.

Write the output as `page_N_updates.json`:

```json
[
  {
    "id": 123,
    "name": "New Product Title",
    "description": "<p>New compelling description...</p>"
  }
]
```

#### 2c. Push updates

```bash
python3 $SCRIPT update --store-hash "STORE_HASH" --token "API_TOKEN" --updates-file page_N_updates.json
```

Updates each product and logs success/failure to `progress.json`.

#### 2d. Report and continue

After each page, briefly state:
- Page X of Y complete
- N products updated, N failed

Then **IMMEDIATELY** proceed to the next page. Do NOT wait for user input.

### Step 3: Completion

When all pages are done:

```bash
python3 $SCRIPT report
```

Print the final summary: total processed, successes, failures, time taken.

## Rules

1. **Never stop mid-run** — process all pages continuously unless an unrecoverable error occurs
2. **Always use progress.json** — if re-invoked, resume from where you left off
3. **Rate limiting** — the script handles BigCommerce rate limits with automatic retry
4. **Error handling** — if one product fails, log it and continue to the next
5. **Content quality** — every title and description must be meaningfully improved, not just rephrased
6. **HTML safety** — descriptions use clean simple HTML only (`<p>`, `<ul>`, `<li>`, `<strong>`, `<em>`)
7. **One page at a time** — fetch, generate, update, then move to next page

## Progress Tracker

`progress.json` tracks everything:

```json
{
  "store_hash": "abc123",
  "total_products": 150,
  "total_pages": 15,
  "products_per_page": 10,
  "started_at": "2025-01-01T00:00:00Z",
  "pages_completed": [1, 2, 3],
  "products_updated": [],
  "products_failed": [],
  "current_page": 4,
  "status": "in_progress"
}
```
