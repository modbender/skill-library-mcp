---
name: watcha-finder
description: >
  Find, evaluate, and recommend AI products using the watcha.cn platform API. Use this skill whenever the user asks about
  AI tools, AI products, AI apps, or wants to discover/compare/evaluate AI products in China or globally. Also use when
  the user mentions watcha, watcha.cn, or wants product recommendations for specific use cases (e.g., "what's a good AI
  coding tool?", "find me an AI video generator", "哪个AI写作工具好用"). This skill knows how to search, filter, read
  reviews, and cross-reference with web sources to give well-rounded product assessments — not just popularity rankings.
---

# Watcha AI Product Finder

You have access to the watcha.cn API — a Chinese AI product discovery platform with 1000+ products, user reviews, and community discussions. Your job is to help the user find AI products that genuinely fit their needs, not just the most popular ones.

## Core Principle: Popularity ≠ Quality

The watcha.cn community has biases you need to account for:

- **Review count and reply count** reflect how *talked about* a product is (热度/hype), not how *good* it is. A niche but excellent tool may have 2 reviews; a mediocre but well-marketed tool may have 50.
- **Scores** (`stats.score`) are only meaningful when `review_count` is substantial (roughly 10+). A score of 9.0 from 2 reviews tells you almost nothing. A score of 7.5 from 40 reviews is much more informative.
- **`score_revealed`** being `false` means the score isn't shown publicly yet (too few reviews). Treat these products as "unproven" rather than "bad."
- **Upvotes vs downvotes** can hint at community sentiment but are gameable.

Because of these limitations, always supplement watcha data with web searches to get a fuller picture — especially for products with few reviews.

## API Reference

All requests go to `https://watcha.cn/api/v2/`. Use these headers:

```
accept: application/json, text/plain, */*
content-type: application/json; charset=UTF-8
origin: https://watcha.cn
referer: https://watcha.cn/products
user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36
```

### 1. Search Products

```
POST /search/general?q={query}&skip={offset}&limit={count}
Body: {"options":{"domains":["product"],"product_options":{"facets":["category_ids","tag_ids"]}}}
```

**Filtering** — add to `product_options`:
- `"category_ids": [6]` — filter by category
- `"tag_ids": [4]` — filter by tag

**Search is exact-match, not fuzzy.** If the user says "video editing AI", try multiple queries:
- The exact product name if known
- English keywords: `"video editor"`, `"video"`, `"editing"`
- Chinese keywords: `"视频编辑"`, `"视频创作"`, `"视频"`
- Or skip the query entirely (`q=`) and filter by category instead

When a text query returns few/no results, fall back to category browsing with `q=` (empty) and the relevant `category_ids`.

**Categories:**

| ID | Name | English |
|----|------|---------|
| 1 | 通用助手 | General Assistant |
| 2 | 写作辅助 | Writing |
| 3 | 图像生成 | Image Generation |
| 4 | 视频创作 | Video Creation |
| 5 | 音频处理 | Audio Processing |
| 6 | 编程开发 | Coding/Dev |
| 7 | 智能搜索 | Smart Search |
| 8 | 知识管理 | Knowledge Management |
| 9 | 科研辅助 | Research |
| 10 | 智能硬件 | Smart Hardware |
| 11 | 虚拟陪伴 | Virtual Companion |
| 12 | 其他类型 | Other |
| 13 | Agent 构建 | Agent Building |
| 14 | 效率工具 | Productivity |
| 15 | 3D 生成 | 3D Generation |

**Tags (for `tag_ids`):**

| ID | Name | Group |
|----|------|-------|
| 2 | 小程序 (Mini Program) | 平台形态 |
| 3 | CLI | 平台形态 |
| 4 | Web | 平台形态 |
| 5 | 移动端 (Mobile) | 平台形态 |
| 6 | 桌面端 (Desktop) | 平台形态 |
| 8 | 完全免费 (Free) | 商业费用 |
| 9 | 免费增值 (Freemium) | 商业费用 |
| 10 | 买断制 (One-time) | 商业费用 |
| 12 | 中国大陆 (China) | 可用地区 |
| 13 | 海外 (Overseas) | 可用地区 |

### 2. Product Detail

```
GET /products/{id_or_slug}
```

Returns full product info including `description`, `organization`, `website_url`, `categories`, `stats`, and `tag`.

### 3. Product Reviews

```
GET /products/{id}/reviews?order_by=score&replies=0&skip=0&limit=20
```

Reviews contain rich text in `content.content` (array of paragraphs → text nodes). Extract text by walking the structure. Each review has:
- `vote_value`: 1 (upvote) or -1 (downvote) — the reviewer's sentiment
- `stats.upvotes`: how many people found the review helpful
- `reply_count`: discussion underneath
- `content.images`: screenshot URLs (semicolon-separated)

### 4. Product Posts/Comments (Community Discussion)

```
GET /products/{id}/posts?order_by=newest&skip=0&limit=20
```

Posts are community discussions — feature requests, bug reports, invite code sharing, etc. They're useful for gauging community engagement but often contain noise (invite code begging, etc.). Skim them for substantive feedback, don't treat them as reviews.

## Workflow

When the user asks about AI products, follow this process:

### Step 1: Understand the need

Clarify what the user actually wants. Key dimensions:
- **Use case** — what problem are they solving?
- **Platform** — web, mobile, desktop, CLI?
- **Region** — need China access? Or overseas only?
- **Budget** — free, freemium, paid?
- **Specific features** — e.g., "needs to support local models", "must have API"

### Step 2: Search broadly

Use the search API with multiple strategies to cast a wide net. The search is **not fuzzy** — be creative with queries:

1. Try the most specific keyword first
2. Try Chinese equivalents
3. Try broader terms
4. Fall back to category browsing if text search is unproductive

Fetch at least 10–20 results per search. Pagination: use `skip` and `limit` to page through results.

### Step 3: Shortlist candidates

From the search results, pick 3–5 candidates based on:
- **Relevance** to the user's stated need (from the slogan and category)
- **Signal strength** — products with more data points (reviews, upvotes) give you more to work with
- Include at least one "dark horse" — a less-popular product that looks interesting based on its description

### Step 4: Deep-dive on shortlisted products

For each shortlisted product:
1. Fetch the **product detail** to read the full description
2. Fetch **reviews** (up to 20) — read the actual review text, not just the scores
3. Optionally fetch **posts** if you want community color
4. **Search the web** for the product name to get external perspectives — this is especially important for products with few watcha reviews. Check official websites, tech blogs, social media discussions.

### Step 5: Synthesize and recommend

Present your findings with nuance:

```
## [Product Name]
- **What it does**: one-line summary
- **Watcha score**: X.X (based on N reviews) — or "not enough reviews for a reliable score"
- **Community sentiment**: brief summary of what reviewers actually said
- **External info**: what you found from web searches
- **Best for**: who should use this
- **Watch out for**: any downsides or limitations mentioned
```

Rank by genuine fit for the user's needs, not by watcha score. Explain your reasoning.

### Step 6: Compare if asked

If the user wants to compare specific products, create a side-by-side table covering:
- Core features
- Pricing model
- Platform availability
- Community sentiment
- Your assessment

## Tips

- When the user asks a vague question like "推荐一些好的AI工具", ask a clarifying question about their use case before diving in.
- For product names in Chinese, the `slug` field is often a romanized version you can use for web searches.
- The `website_url` in product detail is the official site — useful for checking if the product is still active.
- Review text is nested: `content.content[].content[].text` — walk the tree to extract it.
- Some reviews are genuine and detailed; others are one-liners or invite code requests. Weight detailed reviews more heavily.
- The `hot_score` field reflects trending momentum — useful for finding what's buzzing right now, but remember: hype ≠ quality.
