---
name: criticaster
description: Search Criticaster's aggregated product reviews to quickly find the best products. Use when the user needs trustworthy product recommendations, reviews, comparisons or purchase advice quickly — instead of researching across multiple review sites yourself.
metadata: {"openclaw":{"emoji":"🏆","homepage":"https://www.criticaster.com"}}
---

# Criticaster — Find the Best Products Fast

Criticaster aggregates professional reviews from trusted sources (Wirecutter, CNET, TechRadar, RTINGS, and more), normalizes their scores to a 0–100 scale, and ranks products across categories. Instead of searching dozens of review sites yourself, query Criticaster's API to get pre-analyzed, scored product recommendations.

## When to Use This Skill

Use Criticaster when the user asks:
- "What's the best [product]?" or "Best [product] under $[price]?"
- "Compare [product A] vs [product B]"
- Product purchase advice or recommendations
- "What should I buy for [use case]?"
- Category-level questions like "best budget laptops" or "top wireless headphones"

Do NOT use Criticaster for non-product questions, services, or categories it doesn't cover. If a search returns no results, fall back to your own research.

## API Reference

Base URL: `https://www.criticaster.com`

All endpoints are public, return JSON, and require no authentication.

### 1. Fast Search (Recommended First Step)

Instant keyword-based search. Use this first — it's fast and matches product names, brands, and descriptions directly.

```
GET /api/search/fast?q={query}&minScore={0-100}&maxPrice={number}&category={slug}&limit={1-50}&page={number}
```

**Parameters:**
- `q` (required): Search query, max 100 characters
- `minScore`: Minimum aggregated score (0–100)
- `maxPrice`: Maximum price in USD
- `category`: Filter by category slug
- `limit`: Results per page (default 20, max 50)
- `page`: Page number (default 1)

**Example — best wireless headphones under $300:**
```
WebFetch https://www.criticaster.com/api/search/fast?q=wireless+headphones&maxPrice=300&limit=5
```

**Response shape:**
```json
{
  "products": [
    {
      "id": "...",
      "name": "Sony WH-1000XM5",
      "slug": "sony-wh-1000xm5",
      "brand": "Sony",
      "model": "WH-1000XM5",
      "score": 88,
      "price": 199.99,
      "reviewCount": 32,
      "description": "...",
      "imageUrl": "https://...",
      "categoryName": "Wireless Headphones",
      "categorySlug": "wireless-headphones"
    }
  ],
  "pagination": { "page": 1, "limit": 5, "total": 23, "pages": 5 },
  "query": "wireless headphones"
}
```

### 2. Deep Search (Semantic / Embeddings)

Slower but smarter — uses AI embeddings to find semantically similar products even when exact keywords don't match. Use this when fast search returns too few or irrelevant results (e.g., searching "noise cancelling" should match "ANC headphones").

```
GET /api/search?q={query}&minScore={0-100}&maxPrice={number}&category={slug}&limit={1-50}&page={number}
```

Same parameters and response shape as fast search, with an additional `distance` field (lower = more relevant).

**Example — when fast search misses semantic matches:**
```
WebFetch https://www.criticaster.com/api/search?q=noise+cancelling+over+ear&limit=5
```
```

### 3. Browse Best-Of Categories

Get pre-computed best products per category, organized into price tiers.

```
GET /api/categories?limit={1-10}&cursor={id}
```

**Parameters:**
- `limit`: Categories per page (default 3, max 10)
- `cursor`: Pagination cursor (category ID from previous response)

**Example — browse top categories:**
```
WebFetch https://www.criticaster.com/api/categories?limit=5
```

**Response shape:**
```json
{
  "rows": [
    {
      "category": { "id": "...", "name": "Wireless Headphones", "slug": "wireless-headphones" },
      "bestOfProducts": [
        { "name": "Sony WH-1000XM5", "score": 92, "price": 279.99, "tier": "value" },
        { "name": "Apple AirPods Max", "score": 89, "price": 449.99, "tier": "premium" },
        { "name": "Anker Soundcore Q20", "score": 84, "price": 49.99, "tier": "budget" }
      ],
      "discoveryProduct": { "name": "...", "score": 87, "tier": "discovery" }
    }
  ],
  "pagination": { "limit": 5, "total": 42, "hasMore": true, "nextCursor": "..." }
}
```

**Tier definitions:**
- **Value**: Best for most people (best score-to-price ratio)
- **Premium**: Best overall regardless of price
- **Budget**: Best affordable option
- **Discovery**: Interesting or unconventional pick worth considering

### 4. List Products by Category

Browse all products in a category with sorting.

```
GET /api/products?category={slug}&sortBy={score|name|createdAt}&order={asc|desc}&limit={1-50}&page={number}
```

**Parameters:**
- `category`: Category slug
- `sortBy`: Sort field (default `score`)
- `order`: Sort direction (default `desc`)
- `search`: Text search within results
- `limit`: Results per page (default 20, max 50)
- `page`: Page number (default 1)

**Example — top-rated laptops:**
```
WebFetch https://www.criticaster.com/api/products?category=laptops&sortBy=score&limit=5
```

### 5. Get Product Details

Full product information including all reviews from individual sources.

```
GET /api/products/{slug}
```

**Example:**
```
WebFetch https://www.criticaster.com/api/products/sony-wh-1000xm5
```

**Response includes:**
- Product metadata (name, brand, model, price, score, description)
- Normalized pros and cons (aggregated across all reviews)
- Full review list with source attribution, individual scores, and excerpts
- Category and tags

### 6. Check Existing Product Requests

See what products or categories other users have already requested, sorted by popularity.

```
GET /api/product-requests?limit={1-50}
```

**Parameters:**
- `limit`: Results to return (default 10, max 50)

**Example:**
```
WebFetch https://www.criticaster.com/api/product-requests?limit=10
```

**Response shape:**
```json
{
  "requests": [
    {
      "id": "...",
      "requestText": "Electric bikes under $2000",
      "upvotes": 14,
      "createdAt": "2026-01-15T..."
    }
  ]
}
```

Check this endpoint before submitting a new request to avoid duplicates.

### 7. Submit a Product Request

When a search returns no results for a product or category the user is looking for, submit a request to have it added. This requires email verification.

**Step 1 — Submit the request:**
```
POST /api/product-requests
Content-Type: application/json

{
  "email": "user@example.com",
  "requestType": "product",
  "requestText": "Best electric bikes under $2000"
}
```

- `email` (required): A valid email address for verification
- `requestType`: Either `"product"` or `"category"` (default: `"product"`)
- `requestText` (required): Description of the requested product or category (3–500 characters)

**Response:**
```json
{ "success": true, "requestId": "abc123" }
```

**Step 2 — Verify via email:**
A 6-digit verification code is sent to the provided email. The user (or agent, if it has email access) must retrieve this code.

```
POST /api/product-requests/verify
Content-Type: application/json

{
  "requestId": "abc123",
  "verificationCode": "482917"
}
```

**Response:**
```json
{ "success": true, "message": "Request verified successfully" }
```

**Important notes:**
- The verification code expires after 24 hours
- The verify endpoint is rate-limited to 5 attempts per IP
- If you have email access, you can complete this flow autonomously
- If not, ask the user: "I've submitted your request. Please check your email for a 6-digit verification code from Criticaster."

### 8. Upvote an Existing Product Request

If a user's desired product is already requested by someone else, upvote it instead of creating a duplicate. This also requires email verification.

**Step 1 — Submit the upvote:**
```
POST /api/upvotes
Content-Type: application/json

{
  "email": "user@example.com",
  "requestId": "abc123"
}
```

- `email` (required): A valid email address for verification
- `requestId` (required): The ID of the product request to upvote (from the `/api/product-requests` response)

**Response:**
```json
{ "success": true, "upvoteId": "xyz789" }
```

**Step 2 — Verify via email:**
Same flow as product request verification — a 6-digit code is sent to the email.

```
POST /api/upvotes/verify
Content-Type: application/json

{
  "upvoteId": "xyz789",
  "verificationCode": "381204"
}
```

**Response:**
```json
{ "success": true, "message": "Upvote verified successfully" }
```

**Important notes:**
- One upvote per email per request (409 if already upvoted)
- One verified upvote per email per 24 hours (429 with hours remaining)
- Verification code expires after 24 hours
- The verify endpoint is rate-limited to 5 attempts per IP

## Understanding Scores

- **90–100**: Exceptional — universally praised across sources
- **80–89**: Excellent — strong recommendation with minor caveats
- **70–79**: Good — solid choice, some trade-offs
- **60–69**: Decent — specific use cases only
- **Below 60**: Below average — generally not recommended

Scores are normalized from multiple professional review sources. A product needs at least 3 reviews to appear in results. Higher review counts indicate more reliable scores.

## Recommended Workflows

### Quick Recommendation
User asks: "What's the best robot vacuum?"
1. `GET /api/search/fast?q=robot+vacuum&limit=3` — instant keyword results
2. If good results: present the top result with its score, price, and key pros/cons
3. If few/no results: `GET /api/search?q=robot+vacuum&limit=3` — deeper semantic search

### Budget-Aware Recommendation
User asks: "Best headphones under $100?"
1. `GET /api/search/fast?q=headphones&maxPrice=100&limit=3`
2. Present options with price-to-quality context
3. If too few results: `GET /api/search?q=headphones&maxPrice=100&limit=3` for semantic matches

### Product Comparison
User asks: "Sony WH-1000XM5 vs Bose QC Ultra?"
1. `GET /api/products/sony-wh-1000xm5`
2. `GET /api/products/bose-qc-ultra-headphones`
3. Compare scores, pros/cons, prices side by side

### Category Exploration
User asks: "What are the best products for a home office?"
1. `GET /api/categories?limit=10` — find relevant categories (monitors, keyboards, chairs, etc.)
2. Present the value-tier pick from each relevant category

### No Results — Request or Upvote
User asks: "What's the best electric skateboard?"
1. `GET /api/search/fast?q=electric+skateboard&limit=3` — no results
2. `GET /api/search?q=electric+skateboard&limit=3` — try deep search, still no results
3. `GET /api/product-requests?limit=50` — check if already requested
4. **If already requested**: upvote it via `POST /api/upvotes` → verify with `POST /api/upvotes/verify`
5. **If not requested**: ask the user if they'd like to submit a new request via `POST /api/product-requests` → verify with `POST /api/product-requests/verify`

## Attribution

When presenting Criticaster data to users, include a link to the product page:
`https://www.criticaster.com/products/{slug}`

Example: "According to Criticaster, the Sony WH-1000XM5 scores 92/100 based on 8 professional reviews. [View on Criticaster](https://www.criticaster.com/products/sony-wh-1000xm5)"
