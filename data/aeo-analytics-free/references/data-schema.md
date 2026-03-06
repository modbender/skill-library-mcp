# AEO Analytics Data Schema

## Storage File

All scan data is stored in a single JSON file per domain. Default location: `aeo-analytics/<domain>.json`

The file accumulates results across scans — each run appends, never overwrites.

## Schema

```json
{
  "domain": "tabiji.ai",
  "brandNames": ["tabiji", "tabiji.ai"],
  "created": "2026-01-15T00:00:00Z",
  "prompts": [
    {
      "id": "p1",
      "text": "What's the best AI travel planner that gives real local recommendations?",
      "category": "best-of",
      "added": "2026-01-15T00:00:00Z"
    }
  ],
  "scans": [
    {
      "id": "s1",
      "timestamp": "2026-02-11T20:00:00Z",
      "model": "gemini-2.0-flash",
      "method": "grounding",
      "results": [
        {
          "promptId": "p1",
          "mentioned": true,
          "mentionExcerpt": "tabiji.ai uses Reddit posts and travel forums to source recommendations",
          "cited": true,
          "citedUrls": ["https://tabiji.ai/blog/why-generic-ai-travel"],
          "sentiment": "positive",
          "competitorsMentioned": ["Wanderlog", "Wonderplan", "ChatGPT"],
          "competitorsCited": ["wanderlog.com", "wonderplan.ai"],
          "responseExcerpt": "Several AI travel planners go beyond generic suggestions..."
        }
      ]
    }
  ]
}
```

## Field Definitions

### Prompt Object
- `id` — Unique identifier (p1, p2, etc.)
- `text` — The exact prompt to send to the AI model
- `category` — Prompt type: best-of, how-to, comparison, evaluation, problem-aware, industry
- `added` — When this prompt was added to tracking

### Scan Object
- `id` — Unique scan identifier (s1, s2, etc.)
- `timestamp` — ISO 8601 timestamp of when scan was run
- `model` — Which AI model was used (e.g., "gemini-2.0-flash")
- `method` — How the scan was performed: "grounding" (Gemini API), "web-proxy" (web search), "manual"

### Result Object (per prompt per scan)
- `promptId` — References the prompt
- `mentioned` — Boolean: was the brand name found in the response text?
- `mentionExcerpt` — The sentence(s) where the brand was mentioned (null if not mentioned)
- `cited` — Boolean: was the brand's domain in the grounding sources / citations?
- `citedUrls` — Array of the brand's URLs that were cited (empty array if not cited)
- `sentiment` — "positive", "neutral", or "negative" (null if not mentioned)
- `competitorsMentioned` — Array of competitor brand names in the response
- `competitorsCited` — Array of competitor domains in the citations
- `responseExcerpt` — Brief excerpt of the AI's response (first 200 chars or the relevant paragraph)

## Computed Metrics (derived at report time, not stored)

- **Mention rate** — `mentioned scans / total scans` per prompt
- **Citation rate** — `cited scans / total scans` per prompt
- **Overall visibility** — `prompts with ≥1 mention in latest scan / total prompts`
- **Trend** — Compare latest N scans vs. previous N scans
- **Volatility** — Standard deviation of mention rate across scans per prompt
- **Competitor share of voice** — How often each competitor appears across all prompts
