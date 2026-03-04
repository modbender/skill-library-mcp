```skill
---
name: prezentit
description: Generate beautiful AI-powered presentations instantly. Create professional slides with custom themes, visual designs, and speaker notes—all through natural language commands.
homepage: https://prezentit.net
emoji: "👽"
metadata:
  clawdbot:
    emoji: "👽"
    skillKey: prezentit
    homepage: https://prezentit.net
    requires:
      config:
        - PREZENTIT_API_KEY
    config:
      requiredEnv:
        - name: PREZENTIT_API_KEY
          description: Your Prezentit API key (starts with pk_). Get one free at https://prezentit.net/api-keys
      example: |
        export PREZENTIT_API_KEY=pk_your_api_key_here
    permissions:
      network:
        - https://prezentit.net/api/v1/*
      fileSystem: none
      env:
        reads:
          - PREZENTIT_API_KEY
        writes: none
---

# Prezentit - AI Presentation Generator

**Base URL**: `https://prezentit.net/api/v1`
**Auth Header**: `Authorization: Bearer {PREZENTIT_API_KEY}`

> **This skill requires a `PREZENTIT_API_KEY` environment variable.** Get a free API key at https://prezentit.net/api-keys — new accounts include 100 free credits.

## ⚠️ CRITICAL FOR AI AGENTS

**ALWAYS use `"stream": false`** in generation requests! Without this, you get streaming responses that cause issues.

---

## Complete Workflow (FOLLOW THIS ORDER)

### Step 1: Check Credits First

```http
GET /api/v1/me/credits
Authorization: Bearer {PREZENTIT_API_KEY}
```

**Response:**
```json
{
  "credits": 100,
  "pricing": {
    "outlinePerSlide": 5,
    "designPerSlide": 10,
    "estimatedCostPerSlide": 15
  },
  "_ai": {
    "canGenerate": true,
    "maxSlidesAffordable": 6,
    "nextSteps": ["..."]
  }
}
```

→ If `_ai.canGenerate` is false, direct user to https://prezentit.net/buy-credits
→ Use `_ai.maxSlidesAffordable` to know the limit

### Step 2: Choose a Theme

**Option A — Browse all available themes and pick by ID:**

```http
GET /api/v1/themes
Authorization: Bearer {PREZENTIT_API_KEY}
```

**Response:**
```json
{
  "themes": [
    { "id": "corporate_blue", "name": "Corporate Blue", "category": "Corporate & Professional" },
    { "id": "nature_earth", "name": "Nature Earth", "category": "Nature & Organic" }
  ],
  "categories": ["Corporate & Professional", "Creative & Visual", "Data & Analytics", ...],
  "_ai": {
    "totalThemes": 20,
    "popularThemes": ["corporate_blue", "midnight_tech", "nature_earth", "storyteller", "data_dashboard"]
  }
}
```

→ Use the exact `id` value in your generation request

**Option B — Search for a theme by keyword:**

```http
GET /api/v1/themes?search=minimalist
Authorization: Bearer {PREZENTIT_API_KEY}
```

→ Returns best matches ranked by relevance. Use the `id` from `bestMatch`.

**Option C — Describe a custom style (no theme ID needed):**

Use the `customDesignPrompt` parameter instead. See the Custom Design Prompt section below.

### Step 3: Generate Presentation

```http
POST /api/v1/presentations/generate
Authorization: Bearer {PREZENTIT_API_KEY}
Content-Type: application/json

{
  "topic": "User's topic here",
  "slideCount": 5,
  "theme": "corporate_blue",
  "stream": false
}
```

**⏱️ IMPORTANT: Generation takes 1-3 minutes. The API will return when complete.**

**Full Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | Yes* | Presentation topic (2-500 chars). Required if no `outline`. `prompt` is also accepted as an alias. |
| `outline` | object | No | Pre-built outline (saves ~33% credits). See Outline section below. |
| `slideCount` | number | No | Number of slides (3-50, default: 5). Ignored if outline provided. |
| `theme` | string | No | Theme ID from `GET /api/v1/themes`. Use the exact `id` value. |
| `customDesignPrompt` | string | No | Custom visual style description (see below). Overrides theme ID. |
| `details` | string | No | Additional context about the presentation content. |
| `confirmPartial` | boolean | No | Set `true` to confirm partial generation when credits are limited. |
| `stream` | boolean | **ALWAYS false** | **AI agents must always set `stream: false`**. |

*`topic` is required even when providing an `outline` (used for presentation metadata).

### Step 4: Get the Result

**Success Response:**
```json
{
  "presentationId": "uuid-here",
  "viewUrl": "https://prezentit.net/view/abc123",
  "creditsUsed": 75,
  "remainingCredits": 25
}
```

→ Share the `viewUrl` with the user. That's their presentation!

### Step 5: Download (Optional)

```http
GET /api/v1/presentations/{presentationId}/download?format=pptx
Authorization: Bearer {PREZENTIT_API_KEY}
```

**Formats:** `pptx` (PowerPoint), `pdf`, `json` (raw data)

---

## Pricing

| Scenario | Cost per Slide | Example (5 slides) |
|----------|----------------|-------------------|
| Auto-generate outline | 15 credits | 75 credits |
| Provide your own outline | 10 credits | 50 credits (~33% savings!) |

- New accounts get **100 free credits**
- Buy more at: https://prezentit.net/buy-credits

---

## Theme Selection

### How to Pick a Theme

1. **Fetch the theme list**: `GET /api/v1/themes` — returns all available themes with `id`, `name`, and `category`
2. **Pick the best match** for the user's topic and style preference
3. **Pass the `id`** in the generation request as the `theme` parameter

You can also search: `GET /api/v1/themes?search=KEYWORD` or filter by category: `GET /api/v1/themes?category=CATEGORY_NAME`

### Custom Design Prompt (Skip the Theme List)

If no existing theme fits, use `customDesignPrompt` to describe a fully custom visual style. **This must be a detailed, structured description** — not just a color palette.

**REQUIRED structure for customDesignPrompt** (include ALL of these sections):

```
COLOR SYSTEM: Primary [hex], secondary [hex], accent [hex], background [hex/gradient], text colors for headings and body.

TYPOGRAPHY: Heading font style [e.g., bold geometric sans-serif like Montserrat], body font style [e.g., clean humanist sans-serif like Open Sans], size hierarchy [large/medium/small], weight contrast.

LAYOUT SYSTEM: Slide structure [e.g., asymmetric split with 60/40 content-to-visual ratio], alignment [left-aligned text with right visual panel], spacing philosophy [generous whitespace vs. dense information], grid approach.

VISUAL ELEMENTS: Background treatment [solid/gradient/textured/patterned], decorative motifs [geometric shapes, organic curves, line art, etc.], image style [photography with overlay, illustrations, icons, data visualizations], border/frame treatments.

MOOD & TONE: Overall aesthetic [e.g., corporate authority, playful creativity, academic rigor, tech-forward], energy level [calm/dynamic/bold], intended audience impression.
```

**Example — Good customDesignPrompt:**

```json
{
  "topic": "AI in Healthcare",
  "customDesignPrompt": "COLOR SYSTEM: Primary deep medical blue (#1B3A5C), secondary teal (#2A9D8F), accent warm coral (#E76F51) for callouts, backgrounds alternate between clean white (#FAFAFA) and very subtle blue-gray (#F0F4F8), heading text dark navy, body text #333333. TYPOGRAPHY: Headings in bold geometric sans-serif (Montserrat style), body in clean humanist sans (Source Sans style), strong size hierarchy with 48pt titles, 24pt subtitles, 16pt body. LAYOUT SYSTEM: Asymmetric layouts with 60/40 content-to-visual split, left-aligned text blocks with right-side data visualizations or medical imagery, generous padding (60px margins), clean grid structure. VISUAL ELEMENTS: Subtle DNA helix watermark in corners at 5% opacity, thin teal accent lines as section dividers, medical iconography (stethoscope, heartbeat, molecular structures) as small decorative elements, photography with blue-tinted overlay for full-bleed backgrounds. MOOD & TONE: Professional medical authority balanced with approachable warmth, calm and trustworthy, designed for hospital executives and medical professionals.",
  "stream": false
}
```

**Example — Bad customDesignPrompt (TOO VAGUE, will produce generic results):**

```
"blue and white medical theme"
```

---

## Creating Outlines (Save ~33% Credits)

Providing your own outline saves credits and gives you full control over content.

### Outline Structure

The outline is an object with a `slides` array. Each slide has these fields:

```json
{
  "topic": "Your Presentation Topic",
  "outline": {
    "slides": [
      {
        "title": "Slide Title Here",
        "mainIdea": "A clear sentence explaining the core message of this slide and what the audience should take away from it.",
        "talkingPoints": [
          "First key point with enough detail to be meaningful (at least 10 characters)",
          "Second key point expanding on the main idea",
          "Third key point providing supporting evidence or examples"
        ],
        "visualGuide": "Detailed description of the visual layout: background style, image placement, icon suggestions, chart types, color emphasis areas, and decorative elements for this specific slide."
      }
    ]
  },
  "stream": false
}
```

### Slide Field Reference

| Field | Required | Constraints | Description |
|-------|----------|-------------|-------------|
| `title` | Yes | 3-100 chars, 1-15 words | Slide heading |
| `mainIdea` | Yes | 10-500 chars, 3-75 words | Core message of the slide |
| `talkingPoints` | Yes | 2-7 items, each 10-300 chars (3-50 words) | Key points to cover |
| `visualGuide` | Yes | 20-500 chars, 5-75 words | Visual design instructions for this slide |

### Validation Rules

**Overall:**
- Minimum **3 slides**, maximum **50 slides**
- `topic` is still required (used for presentation metadata)
- All four fields (`title`, `mainIdea`, `talkingPoints`, `visualGuide`) are required per slide

**The API returns detailed error messages with `fix` suggestions if validation fails.**

### Complete Example

```json
{
  "topic": "Introduction to Machine Learning",
  "outline": {
    "slides": [
      {
        "title": "Introduction to Machine Learning",
        "mainIdea": "Machine learning is transforming how businesses operate by enabling systems to learn from data and improve automatically without explicit programming.",
        "talkingPoints": [
          "Machine learning is a subset of artificial intelligence focused on pattern recognition",
          "ML systems improve through experience rather than manual rule-writing",
          "Global ML market projected to reach $209 billion by 2029"
        ],
        "visualGuide": "Bold title slide with futuristic tech aesthetic. Dark gradient background transitioning from deep navy to midnight blue. Large bold title text centered with a subtle neural network node pattern behind it. Accent glow in electric blue."
      },
      {
        "title": "How Machine Learning Works",
        "mainIdea": "Machine learning algorithms are categorized into supervised, unsupervised, and reinforcement learning based on how they learn from data.",
        "talkingPoints": [
          "Supervised learning uses labeled data for classification and regression tasks",
          "Unsupervised learning discovers hidden patterns in unlabeled data through clustering",
          "Reinforcement learning optimizes decisions through trial, error, and reward signals"
        ],
        "visualGuide": "Three distinct visual sections showing each ML type with representative icons: labeled data pairs for supervised, clustered groups for unsupervised, and a game-like reward loop for reinforcement. Use consistent color coding with blue, green, and purple."
      },
      {
        "title": "Business Applications",
        "mainIdea": "Companies across industries are leveraging machine learning for competitive advantage in customer experience, operations, and decision-making.",
        "talkingPoints": [
          "Customer churn prediction reduces revenue loss by identifying at-risk accounts early",
          "Fraud detection systems process millions of transactions in real-time",
          "Personalized recommendation engines drive significant increases in engagement and sales"
        ],
        "visualGuide": "Clean content layout with left-aligned text and right-side icons or mini-charts for each application. Use a white background with subtle grid lines. Each talking point gets a small illustrative icon (shield for fraud, chart for prediction, user icon for personalization)."
      },
      {
        "title": "Getting Started with ML",
        "mainIdea": "Successful ML adoption requires starting with clear use cases, quality data, and the right team rather than jumping straight to complex algorithms.",
        "talkingPoints": [
          "Identify high-impact use cases where prediction or automation adds clear value",
          "Invest in clean, well-structured data before selecting algorithms",
          "Build or partner with ML expertise and start with proven frameworks"
        ],
        "visualGuide": "Conclusion slide with a numbered roadmap or step layout. Three large numbered circles (1, 2, 3) each containing a step. Background with subtle upward-pointing arrows suggesting progress. Call-to-action feel with bold accent color on the final step."
      }
    ]
  },
  "theme": "midnight_tech",
  "stream": false
}
```

### Get Schema Programmatically

```http
GET /api/v1/docs/outline-format
Authorization: Bearer {PREZENTIT_API_KEY}
```

Returns the full JSON schema with all constraints and example slides.

---

## Error Handling

### Error Response Format

```json
{
  "error": "Human readable message",
  "code": "ERROR_CODE",
  "fix": "Guidance on how to resolve this"
}
```

### Common Errors & Solutions

| HTTP | Code | Message | Solution |
|------|------|---------|----------|
| 400 | `MISSING_TOPIC` | Topic or prompt is required | Provide a `topic` or `prompt` field |
| 400 | `INVALID_OUTLINE` | Outline validation failed | Check outline structure — response includes detailed `validationErrors` with `fix` per field |
| 400 | `INVALID_SLIDE_COUNT` | Slide count must be 3-50 | Adjust `slideCount` to be between 3 and 50 |
| 401 | `UNAUTHORIZED` | Invalid or missing API key | Check `Authorization: Bearer pk_...` header |
| 402 | `INSUFFICIENT_CREDITS` | Not enough credits | Response includes `required`, `available`, and `purchaseUrl` |
| 404 | `PRESENTATION_NOT_FOUND` | Presentation doesn't exist | Verify presentation ID |
| 409 | `DUPLICATE_REQUEST` | Same request within cooldown | Wait and retry — don't resend identical requests |
| 409 | `GENERATION_IN_PROGRESS` | Already generating | Check status at `GET /api/v1/me/generation/status` or cancel at `POST /api/v1/me/generation/cancel` |
| 429 | `RATE_LIMITED` | Too many requests | Wait `retryAfter` seconds before retrying |
| 500 | `GENERATION_FAILED` | Internal error | Retry once, then contact support |
| 503 | `SERVICE_UNAVAILABLE` | System overloaded | Retry after `retryAfter` seconds |

### Handling Insufficient Credits

```json
{
  "error": "Insufficient credits",
  "code": "INSUFFICIENT_CREDITS",
  "required": 75,
  "available": 50,
  "purchaseUrl": "https://prezentit.net/buy-credits"
}
```

**AI Agent Response:** "You need 75 credits but only have 50. Purchase more at https://prezentit.net/buy-credits"

### Handling Partial Generation

If the user has some credits but not enough for full generation, the API returns a `confirmation_required` response with options. Read the `_ai.options` array and present them to the user. To proceed with partial generation, resend the request with `"confirmPartial": true`.

### Handling Rate Limits

```json
{
  "error": "Too many requests",
  "code": "RATE_LIMITED",
  "retryAfter": 30
}
```

**AI Agent Action:** Wait `retryAfter` seconds before retrying.

---

## Additional Endpoints

### Check Generation Status

```http
GET /api/v1/me/generation/status
Authorization: Bearer {PREZENTIT_API_KEY}
```

Returns current progress if a generation is running: stage, percentage, designs completed.

### Cancel Active Generation

```http
POST /api/v1/me/generation/cancel
Authorization: Bearer {PREZENTIT_API_KEY}
```

Cancels the current generation in progress.

### Get Presentation Details

```http
GET /api/v1/presentations/{presentationId}
Authorization: Bearer {PREZENTIT_API_KEY}
```

### List User's Presentations

```http
GET /api/v1/me/presentations
Authorization: Bearer {PREZENTIT_API_KEY}
```

Optional: `?limit=20&offset=0`

### List All Themes

```http
GET /api/v1/themes
Authorization: Bearer {PREZENTIT_API_KEY}
```

Optional query params:
- `?search=keyword` — Filter by name
- `?category=corporate` — Filter by category

---

## Anti-Spam Rules

| Rule | Limit | What Happens |
|------|-------|--------------|
| Duplicate detection | ~30 seconds | 409 error for identical requests |
| Rate limit | Varies by key | 429 error with `retryAfter` |
| One generation at a time | 1 concurrent | 409 `GENERATION_IN_PROGRESS` error |

**Best Practice:** Always check for `retryAfter` in error responses and wait that duration.

---

## Quick Copy-Paste Examples

### Minimal Generation

```json
POST /api/v1/presentations/generate

{
  "topic": "Introduction to Climate Change",
  "stream": false
}
```

### With Theme (Fetch ID First)

```
1. GET /api/v1/themes → find the theme ID
2. POST /api/v1/presentations/generate
```

```json
{
  "topic": "Q4 Sales Report",
  "slideCount": 8,
  "theme": "corporate_blue",
  "stream": false
}
```

### With Custom Design Prompt

```json
{
  "topic": "Startup Pitch Deck",
  "slideCount": 10,
  "customDesignPrompt": "COLOR SYSTEM: Primary electric indigo (#4F46E5), secondary cyan (#06B6D4), accent hot pink (#EC4899), background dark charcoal (#111827) with subtle radial gradient to #1F2937, heading text white, body text #D1D5DB. TYPOGRAPHY: Headings in extra-bold wide-tracking sans-serif (Inter/Poppins style), body in medium-weight clean sans, dramatic size contrast with 56pt titles and 18pt body. LAYOUT SYSTEM: Full-bleed dark slides with asymmetric content placement, bold left-aligned headlines with supporting text below, large visual areas for mockups and charts, 80px margins. VISUAL ELEMENTS: Subtle dot grid pattern at 3% opacity on backgrounds, neon-glow accent lines, rounded corners on all containers, glassmorphism cards with frosted backgrounds for data callouts, gradient mesh blobs as decorative elements. MOOD & TONE: Bold tech-startup energy, confident and forward-looking, designed to impress venture capital investors.",
  "stream": false
}
```

### With Outline (~33% Savings)

```json
{
  "topic": "Weekly Team Sync",
  "outline": {
    "slides": [
      {
        "title": "Weekly Team Sync",
        "mainIdea": "Kickoff slide for the January 15, 2024 weekly team synchronization meeting covering accomplishments and upcoming goals.",
        "talkingPoints": [
          "Welcome the team and set the agenda for today's sync",
          "Cover last week's wins and this week's priorities"
        ],
        "visualGuide": "Clean title slide with company colors. Bold centered title, date as subtitle below. Simple professional background with subtle geometric pattern."
      },
      {
        "title": "Last Week's Accomplishments",
        "mainIdea": "The team delivered significant progress across feature development, bug resolution, and performance optimization last week.",
        "talkingPoints": [
          "Feature X completed and merged into the main branch ahead of schedule",
          "Resolved three critical production bugs affecting checkout flow",
          "Database query optimization improved page load times by twenty percent"
        ],
        "visualGuide": "Content slide with checkmark icons next to each accomplishment. Green accent color for completed items. Left-aligned text with small celebration graphic in the corner."
      },
      {
        "title": "This Week's Goals",
        "mainIdea": "This week focuses on the beta launch, initial user testing, and completing documentation before the public release.",
        "talkingPoints": [
          "Launch beta version to internal testers by Wednesday",
          "Conduct user testing sessions with five pilot customers",
          "Complete API documentation and developer onboarding guide"
        ],
        "visualGuide": "Forward-looking slide with numbered steps or timeline visual. Blue accent color for upcoming items. Arrow or roadmap graphic showing progression from current state to launch."
      },
      {
        "title": "Open Discussion",
        "mainIdea": "Time for team questions, blockers, and any items not covered in the structured agenda.",
        "talkingPoints": [
          "Open floor for questions and discussion of blockers",
          "Next sync meeting scheduled for Monday at ten AM"
        ],
        "visualGuide": "Simple closing slide with question mark icon or discussion bubble graphic. Calm colors, minimal text, large font for the key info. Meeting time prominently displayed."
      }
    ]
  },
  "theme": "corporate_blue",
  "stream": false
}
```

---

## Getting Help

- **Website**: https://prezentit.net
- **Buy Credits**: https://prezentit.net/buy-credits
- **Support**: https://prezentit.net/support
- **API Key Management**: https://prezentit.net/api-keys
```
