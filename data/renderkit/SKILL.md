---
name: renderkit
version: "1.4.0"
description: Render structured data as beautiful hosted web pages, and create hosted forms for data collection, using the RenderKit API. Use this for visual pages, surveys, RSVPs, feedback forms, or any structured data.
metadata:
  openclaw:
    requires:
      env:
        - RENDERKIT_API_KEY
      bins:
        - curl
    primaryEnv: RENDERKIT_API_KEY
    homepage: https://renderkit.live
---

# RenderKit Skill

Render structured data as beautiful hosted web pages, and create hosted forms for data collection.

## Setup

1. Sign up at [https://renderkit.live](https://renderkit.live) to get your API key
2. Set your environment variable:

```bash
export RENDERKIT_API_KEY="your-api-key"
```

## Usage

All commands use curl to hit the RenderKit API. Pick the right endpoint:

- **Read-only pages** (results, summaries, comparisons, itineraries) → `POST /v1/render`
- **Data collection** (forms, surveys, RSVPs, signups, feedback) → `POST /v1/forms`

### Create a page

```bash
curl -s -X POST https://renderkit.live/v1/render \
  -H "Authorization: Bearer $RENDERKIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "freeform",
    "context": "brief description of what this content is",
    "data": {
      "title": "Page Title",
      "content": "your data here — markdown, structured objects, anything"
    }
  }'
```

Returns `url`, `slug`, and `render_id`. Templates: `freeform` (AI picks layout) or `travel_itinerary`.

### Update a page

```bash
curl -s -X PATCH https://renderkit.live/v1/render/{render_id} \
  -H "Authorization: Bearer $RENDERKIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "merge",
    "context": "updated description",
    "data": { "content": "new or additional data" }
  }'
```

Strategies: `merge` (add sections) or `replace` (full rewrite). The URL stays the same.

### Check page status

```bash
curl -s https://renderkit.live/v1/render/{render_id}/status \
  -H "Authorization: Bearer $RENDERKIT_API_KEY"
```

### Create a form

```bash
curl -s -X POST https://renderkit.live/v1/forms \
  -H "Authorization: Bearer $RENDERKIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Event RSVP",
    "prompt": "Create an RSVP form for a dinner party. Ask for name, email, dietary restrictions, and plus-one.",
    "multi_response": true,
    "expires_in": 604800
  }'
```

Returns a `url` to share with respondents. You can also provide explicit `fields` instead of a `prompt`.

### Get form responses

```bash
curl -s https://renderkit.live/v1/forms/{form_id}/responses \
  -H "Authorization: Bearer $RENDERKIT_API_KEY"
```

### Close a form

```bash
curl -s -X DELETE https://renderkit.live/v1/forms/{form_id} \
  -H "Authorization: Bearer $RENDERKIT_API_KEY"
```

## Notes

- Never use `/v1/render` to fake a form — it produces a static page that cannot collect responses
- Include URLs inline in your data — they are automatically enriched with images, ratings, and metadata
- Optionally pass a theme: `"theme": { "mode": "dark", "palette": ["#color1", "#color2"] }`
- Updates (PATCH) are free and don't count toward your quota
- If you rendered a page in this conversation, prefer PATCH over POST for follow-up changes
- Full API docs: [https://renderkit.live/docs.md](https://renderkit.live/docs.md)

## Examples

```bash
# Create a travel itinerary page
curl -s -X POST https://renderkit.live/v1/render \
  -H "Authorization: Bearer $RENDERKIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"template":"travel_itinerary","context":"3-day Paris trip","data":{"title":"Paris Weekend","content":"Day 1: Louvre, lunch at Loulou, Seine walk. Day 2: Montmartre, Sacré-Cœur."}}'

# Create a feedback survey
curl -s -X POST https://renderkit.live/v1/forms \
  -H "Authorization: Bearer $RENDERKIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Team Feedback","prompt":"Create a short feedback form with rating (1-5) and open comments","multi_response":true}'

# Check for new form submissions
curl -s https://renderkit.live/v1/forms/{form_id}/status \
  -H "Authorization: Bearer $RENDERKIT_API_KEY"
```
