---
name: postnitro-carousel
description: >
  Generate professional social media carousel posts using the PostNitro.ai Embed API.
  Supports AI-powered content generation and manual content import for LinkedIn, Instagram,
  TikTok, and X (Twitter) carousels. Use this skill whenever the user wants to create a
  carousel, social media post, slide deck for social media, multi-slide content, or
  mentions PostNitro. Also trigger when the user asks to turn text, articles, blog posts,
  or topics into carousel posts, or wants to automate social media content creation.
  Outputs PNG images or PDF files. Requires a PostNitro API key.
metadata:
  openclaw:
    emoji: "🎠"
    requires:
      envs:
        - POSTNITRO_API_KEY
        - POSTNITRO_TEMPLATE_ID
        - POSTNITRO_BRAND_ID
        - POSTNITRO_PRESET_ID
---

# PostNitro Carousel Generator

Create social media carousel posts via the PostNitro.ai Embed API. Two workflows:

- **AI Generation** — provide a topic, article, or text and let AI create the carousel
- **Content Import** — provide your own slide content with full control, including infographics

## Prerequisites

Set the following environment variables:

1. `POSTNITRO_API_KEY` — Obtained from PostNitro.ai account settings under "Embed".
2. `POSTNITRO_TEMPLATE_ID` — ID of a carousel template from the user's PostNitro account.
3. `POSTNITRO_BRAND_ID` — ID of a brand profile from the user's PostNitro account.
4. `POSTNITRO_PRESET_ID` — (Required for AI generation) An AI preset ID from the user's PostNitro account.

If the user doesn't have these, direct them to https://postnitro.ai to sign up (free plan: 5 credits/month).

## API Overview

**Base URL**: `https://embed-api.postnitro.ai`

**Authentication**: All requests require the header `embed-api-key: $POSTNITRO_API_KEY`.

**Content-Type**: `application/json` (for POST requests).

### Async Workflow

All carousel creation is asynchronous:

1. **Initiate** — `POST /post/initiate/generate` or `POST /post/initiate/import` → returns `embedPostId`
2. **Poll Status** — `GET /post/status/{embedPostId}` → poll until `status` is `"COMPLETED"`
3. **Get Output** — `GET /post/output/{embedPostId}` → download the finished carousel

---

## Endpoint 1: AI-Powered Generation

`POST /post/initiate/generate`

Use when the user provides a topic, article URL, or text and wants AI to generate carousel content.

### Request Body

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `postType` | string | Yes | Type of post | `"CAROUSEL"` |
| `requestorId` | string | No | Custom tracking identifier | Any string |
| `templateId` | string | Yes | Template ID | Valid template ID |
| `brandId` | string | Yes | Brand configuration ID | Valid brand ID |
| `presetId` | string | Yes | AI configuration preset ID | Valid preset ID |
| `responseType` | string | No | Output format (default: `"PDF"`) | `"PDF"`, `"PNG"` |
| `aiGeneration` | object | Yes | AI generation config | See below |

### aiGeneration Object

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `type` | string | Yes | Type of AI generation | `"text"`, `"article"`, `"x"` |
| `context` | string | Yes | For `"text"`: the text content. For `"article"`: an article URL. For `"x"`: an X post/thread URL. | Any string |
| `instructions` | string | No | Additional style/tone instructions | Any string |

**`aiGeneration.type` values:**
- `"text"` — Generate from user-provided text content
- `"article"` — Generate from an article URL (pass the URL as `context`)
- `"x"` — Generate from an X (Twitter) post or thread URL

### Example (from text)

```bash
curl -X POST 'https://embed-api.postnitro.ai/post/initiate/generate' \
  -H 'Content-Type: application/json' \
  -H "embed-api-key: $POSTNITRO_API_KEY" \
  -d '{
    "postType": "CAROUSEL",
    "requestorId": "user123",
    "templateId": "'"$POSTNITRO_TEMPLATE_ID"'",
    "brandId": "'"$POSTNITRO_BRAND_ID"'",
    "presetId": "'"$POSTNITRO_PRESET_ID"'",
    "responseType": "PNG",
    "aiGeneration": {
      "type": "text",
      "context": "Digital marketing tips for small businesses: 1. Focus on local SEO 2. Use social proof 3. Start email marketing early",
      "instructions": "Focus on actionable tips that can be implemented immediately"
    }
  }'
```

### Example (from article URL)

```bash
curl -X POST 'https://embed-api.postnitro.ai/post/initiate/generate' \
  -H 'Content-Type: application/json' \
  -H "embed-api-key: $POSTNITRO_API_KEY" \
  -d '{
    "postType": "CAROUSEL",
    "requestorId": "user123",
    "templateId": "'"$POSTNITRO_TEMPLATE_ID"'",
    "brandId": "'"$POSTNITRO_BRAND_ID"'",
    "presetId": "'"$POSTNITRO_PRESET_ID"'",
    "responseType": "PNG",
    "aiGeneration": {
      "type": "article",
      "context": "https://example.com/blog/digital-marketing-tips",
      "instructions": "Focus on actionable tips for small businesses"
    }
  }'
```

### Response

```json
{
  "success": true,
  "message": "CAROUSEL generation initiated",
  "data": {
    "embedPostId": "post123",
    "status": "PENDING"
  }
}
```

**Credit cost**: 2 credits per slide.

---

## Endpoint 2: Content Import

`POST /post/initiate/import`

Use when the user provides their own slide content.

### Request Body

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `postType` | string | Yes | Type of post | `"CAROUSEL"` |
| `requestorId` | string | No | Custom tracking identifier | Any string |
| `templateId` | string | Yes | Template ID | Valid template ID |
| `brandId` | string | Yes | Brand configuration ID | Valid brand ID |
| `responseType` | string | No | Output format (default: `"PDF"`) | `"PDF"`, `"PNG"` |
| `slides` | array | Yes | Array of slide objects | See below |

### Slide Structure

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `type` | string | Yes | Slide type | `"starting_slide"`, `"body_slide"`, `"ending_slide"` |
| `heading` | string | Yes | Main heading text | Any string |
| `sub_heading` | string | No | Subtitle text | Any string |
| `description` | string | No | Description text | Any string |
| `image` | string | No | Foreground image URL | Valid URL |
| `background_image` | string | No | Background image URL | Valid URL |
| `cta_button` | string | No | Call-to-action button text | Any string |
| `layoutType` | string | No | Slide layout type | `"default"`, `"infographics"` |
| `layoutConfig` | object | No | Infographics configuration | See below |

### Slide Rules

- **Exactly 1** `starting_slide` (required)
- **At least 1** `body_slide` (required)
- **Exactly 1** `ending_slide` (required)

### Infographics Layout

Set `layoutType` to `"infographic"` on a `body_slide` to replace the image area with structured data.

**layoutConfig object:**

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `columnCount` | number | Yes | Number of columns | `1`, `2`, `3` |
| `columnDisplay` | string | Yes | Layout mode | `"cycle"`, `"grid"` |
| `displayCounterAs` | string | Yes | Counter display | `"none"`, `"counter"` |
| `hasHeader` | boolean | Yes | Show column headers | `true`, `false` |
| `columnData` | array | No | Column content | See below |

**columnData items:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `header` | string | Yes | Column header text |
| `content` | array | Yes | Array of `{"title": "...", "description": "..."}` objects |

**Infographics notes:**
- `layoutType: "infographic"` replaces the slide image with the infographic
- Column count must not exceed 3
- Cyclical display (`"cycle"`) only uses data from the first column
- Grid display (`"grid"`) uses data from all columns

### Example (Default Slides)

```bash
curl -X POST 'https://embed-api.postnitro.ai/post/initiate/import' \
  -H 'Content-Type: application/json' \
  -H "embed-api-key: $POSTNITRO_API_KEY" \
  -d '{
    "postType": "CAROUSEL",
    "templateId": "'"$POSTNITRO_TEMPLATE_ID"'",
    "brandId": "'"$POSTNITRO_BRAND_ID"'",
    "responseType": "PNG",
    "slides": [
      {
        "type": "starting_slide",
        "sub_heading": "My Awesome Subtitle",
        "heading": "Welcome to the Carousel!",
        "description": "This is how you start with a bang.",
        "cta_button": "Swipe to learn more"
      },
      {
        "type": "body_slide",
        "heading": "Section 1: The Core Idea",
        "description": "Explain your first key point here."
      },
      {
        "type": "body_slide",
        "heading": "Section 2: Deeper Dive",
        "description": "More details for the second point."
      },
      {
        "type": "ending_slide",
        "heading": "Get Started Today!",
        "sub_heading": "Ready to Act?",
        "description": "A final encouraging message.",
        "cta_button": "Visit Our Website"
      }
    ]
  }'
```

### Example (With Infographics)

```bash
curl -X POST 'https://embed-api.postnitro.ai/post/initiate/import' \
  -H 'Content-Type: application/json' \
  -H "embed-api-key: $POSTNITRO_API_KEY" \
  -d '{
    "postType": "CAROUSEL",
    "templateId": "'"$POSTNITRO_TEMPLATE_ID"'",
    "brandId": "'"$POSTNITRO_BRAND_ID"'",
    "responseType": "PNG",
    "slides": [
      {
        "type": "starting_slide",
        "heading": "PostNitro Infographics",
        "sub_heading": "Import API Feature",
        "description": "Create stunning visual carousels with structured data."
      },
      {
        "type": "body_slide",
        "heading": "Grid Layout",
        "description": "Display data in an organized grid format.",
        "layoutType": "infographic",
        "layoutConfig": {
          "columnCount": 2,
          "columnDisplay": "grid",
          "displayCounterAs": "counter",
          "hasHeader": true,
          "columnData": [
            {
              "header": "Features",
              "content": [
                {"title": "Grid Display", "description": "Organized columns for comparison."},
                {"title": "Counter Support", "description": "Numbered items for sequence."}
              ]
            },
            {
              "header": "Options",
              "content": [
                {"title": "Column Headers", "description": "Enable/disable per column."},
                {"title": "Flexible Columns", "description": "Choose 1, 2, or 3 columns."}
              ]
            }
          ]
        }
      },
      {
        "type": "ending_slide",
        "heading": "Try PostNitro Infographics",
        "sub_heading": "Start Creating Today",
        "cta_button": "Get Your API Key"
      }
    ]
  }'
```

### Response

```json
{
  "success": true,
  "message": "CAROUSEL generation initiated",
  "data": {
    "embedPostId": "post123",
    "status": "PENDING"
  }
}
```

**Credit cost**: 1 credit per slide.

---

## Endpoint 3: Check Post Status

`GET /post/status/{embedPostId}`

No request body. Pass `embedPostId` as a path parameter.

**Headers:** `embed-api-key: $POSTNITRO_API_KEY` (required)

```bash
curl -X GET "https://embed-api.postnitro.ai/post/status/$EMBED_POST_ID" \
  -H "embed-api-key: $POSTNITRO_API_KEY"
```

### Response

```json
{
  "success": true,
  "data": {
    "embedPostId": "post123",
    "embedPost": {
      "id": "post123",
      "postType": "CAROUSEL",
      "status": "COMPLETED",
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T10:35:00Z"
    },
    "logs": [
      {
        "id": "log1",
        "embedPostId": "post123",
        "step": "INITIATED",
        "status": "SUCCESS",
        "message": "Post generation initiated",
        "timestamp": "2024-01-15T10:30:00Z"
      },
      {
        "id": "log2",
        "embedPostId": "post123",
        "step": "PROCESSING",
        "status": "SUCCESS",
        "message": "Content generated successfully",
        "timestamp": "2024-01-15T10:32:00Z"
      },
      {
        "id": "log3",
        "embedPostId": "post123",
        "step": "COMPLETED",
        "status": "SUCCESS",
        "message": "Post generation completed",
        "timestamp": "2024-01-15T10:35:00Z"
      }
    ]
  }
}
```

Poll every 3–5 seconds. Check `data.embedPost.status` for completion. The `logs` array provides step-by-step progress.

---

## Endpoint 4: Get Output

`GET /post/output/{embedPostId}`

No request body. Pass `embedPostId` as a path parameter.

**Headers:** `embed-api-key: $POSTNITRO_API_KEY` (required)

```bash
curl -X GET "https://embed-api.postnitro.ai/post/output/$EMBED_POST_ID" \
  -H "embed-api-key: $POSTNITRO_API_KEY"
```

### Response (PNG)

```json
{
  "success": true,
  "data": {
    "embedPost": {
      "id": "post123",
      "postType": "CAROUSEL",
      "responseType": "PNG",
      "status": "COMPLETED",
      "credits": 4,
      "createdAt": "2026-02-19T21:11:50.115Z",
      "updatedAt": "2026-02-19T21:12:08.333Z"
    },
    "result": {
      "id": "result123",
      "name": "Welcome to the Carousel!",
      "size": {
        "id": "4:5",
        "dimensions": { "width": 1080, "height": 1350 }
      },
      "type": "png",
      "mimeType": "image/png",
      "data": [
        "https://...supabase.co/.../slide_0.png",
        "https://...supabase.co/.../slide_1.png"
      ]
    }
  }
}
```

### Response (PDF)

```json
{
  "success": true,
  "data": {
    "embedPost": {
      "id": "post123",
      "postType": "CAROUSEL",
      "responseType": "PDF",
      "status": "COMPLETED",
      "credits": 10,
      "createdAt": "2026-02-19T21:11:50.115Z",
      "updatedAt": "2026-02-19T21:12:08.333Z"
    },
    "result": {
      "id": "result123",
      "name": "Welcome to the Carousel!",
      "size": {
        "id": "4:5",
        "dimensions": { "width": 1080, "height": 1350 }
      },
      "type": "pdf",
      "mimeType": "application/pdf",
      "data": "https://...supabase.co/.../output.pdf"
    }
  }
}
```

### Result Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique result identifier |
| `name` | string | Design name (from template or "Untitled") |
| `size` | object | `{ "id": "4:5", "dimensions": { "width": 1080, "height": 1350 } }` |
| `type` | string | File type (`"png"` or `"pdf"`) |
| `mimeType` | string | MIME type (`"image/png"` or `"application/pdf"`) |
| `data` | string or array | **PNG**: Array of URLs (one per slide). **PDF**: Single URL. |

Download the URLs directly to save the carousel files.

---

## Step-by-Step Usage

### AI-Generated Carousel

1. Confirm `POSTNITRO_API_KEY`, `POSTNITRO_TEMPLATE_ID`, `POSTNITRO_BRAND_ID`, and `POSTNITRO_PRESET_ID` are set.
2. Ask the user for their generation type (`text`, `article`, or `x`), the corresponding content (text, article URL, or X post URL), and any style instructions.
3. Send the generate request to `POST /post/initiate/generate`.
4. Extract `embedPostId` from the response.
5. Poll `GET /post/status/{embedPostId}` every 3–5 seconds until `status` is `"COMPLETED"`.
6. Call `GET /post/output/{embedPostId}` to get the result. Download the URL(s) from `data` to save files.

### Custom Content Carousel

1. Confirm `POSTNITRO_API_KEY`, `POSTNITRO_TEMPLATE_ID`, and `POSTNITRO_BRAND_ID` are set.
2. Gather slide content from the user. Structure as: 1 `starting_slide` → 1+ `body_slide` → 1 `ending_slide`.
3. For data-heavy slides, use `layoutType: "infographic"` with a `layoutConfig` object.
4. Send the import request to `POST /post/initiate/import`.
5. Follow the same poll → output flow.

## Content Strategy Tips

- **LinkedIn**: Professional tone, actionable insights, 6–10 slides, clear CTA.
- **Instagram**: Visual-first, concise text, 5–8 slides, storytelling arc.
- **TikTok**: Trendy, punchy, 4–7 slides, hook on slide 1.
- **X (Twitter)**: Data-driven, 3–6 slides, provocative opening.

## Error Handling

- If the API returns an authentication error, verify `POSTNITRO_API_KEY` is correct and the account is active.
- If credits are exhausted, inform the user. Free plan: 5 credits/month. Paid plan: 250+ credits/month ($10/month base).
- If the status poll indicates failure, retry the initiation once before reporting the error.
- All endpoints are rate-limited per API key — space requests appropriately.
- Default `responseType` is `"PDF"`. Always specify `"PNG"` explicitly if individual slide images are needed.

## Links

- Documentation: https://postnitro.ai/docs/embed/api
- Get API Key: https://postnitro.ai/app/embed
- Postman Collection: https://www.postman.com/postnitro/postnitro-embed-apis/overview
- Support: support@postnitro.ai
