---
name: kitful
version: 1.0.4
description: Generate full SEO articles using Kitful.ai. Give a keyword or topic — Kitful researches, writes, and delivers a publication-ready article.
homepage: https://kitful.ai
metadata:
  {
    'openclaw':
      {
        'emoji': '✍️',
        'homepage': 'https://kitful.ai',
        'requires': { 'env': ['KITFUL_API_KEY'] },
        'primaryEnv': 'KITFUL_API_KEY',
      },
  }
---

# Kitful — AI Article Generator

Generate humanized, SEO-ready long-form articles from a keyword or topic. Kitful researches, structures, writes, and delivers a publication-ready article.

---

## Setup (one time)

Get an API key at **https://kitful.ai/settings** → API Keys.

Add it to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "kitful": {
        "apiKey": "kit_your_key_here"
      }
    }
  }
}
```

Optional env vars:

```json
"env": {
  "KITFUL_SPACE_SLUG": "my-blog",
  "KITFUL_BRAND_URL": "https://yourproduct.com"
}
```

- `KITFUL_SPACE_SLUG` — default workspace slug (only needed if you have multiple workspaces)
- `KITFUL_BRAND_URL` — your brand/product URL to weave into every article

Restart OpenClaw after saving. That's it.

---

## How to use

### From a keyword or topic

- _"Write an article about intermittent fasting for beginners"_
- _"Best noise-cancelling headphones under $200"_
- _"Remote work productivity tips, in French"_
- _"TypeScript generics — promote my product subtly"_
- _"How to start a podcast in 2025, how-to guide format"_
- _"Side-by-side comparison of Notion vs Obsidian for CTOs"_
- _"Benefits of cold showers — aggressive product promotion"_
- _"10 best standing desks for home offices, for busy professionals"_

### With extra context

- _"Write about AI burnout for startup founders — skeptical tone, no fluff"_
- _"Freelance pricing guide for designers, mention my agency at https://myagency.com"_
- _"Long-form article on sourdough bread baking, for my cooking blog workspace"_
- _"Write a listicle on SaaS pricing strategies, in Spanish"_

### Guided (not sure what to say)

Just say **"kitful"** with nothing else — you'll be asked one simple question.

### Batch (tech users)

Ask for multiple topics in one message — Kitful generates them sequentially and links each when done:

- _"Write articles about: cold brew coffee, pour over technique, French press guide"_
- _"Generate 3 articles: React Server Components, Next.js App Router, Turbopack intro"_

---

## Agent behavior

### Step 1 — Input detection

**Keyword/topic** — extract:

- `focusKeyword` — the main subject
- `context` — any angle, audience, format, or extra detail mentioned
- `language` — if they said "in French/Spanish/etc." → use the BCP 47 locale code (e.g. `fr`, `es-ES`, `de`, `pt-BR`). Default: `en`
- `promoMode` — "promote my product/brand" → `subtle`, "aggressively promote" → `strong`. Default: `off`
- `spaceSlug` — "for my [name] workspace/blog" → use that slug. Fall back to `KITFUL_SPACE_SLUG`. Default: omit.

**Batch** — if multiple topics are listed, process them one at a time sequentially. Announce each as it starts and link each when done.

**No topic** — ask one question only: _"What would you like to write about?"_ Then generate immediately on their answer, no follow-ups.

### Step 2 — Generate

```
POST https://kitful.ai/api/v1/articles/generate
Authorization: Bearer $KITFUL_API_KEY
Content-Type: application/json
```

Request body:

```json
{
  "focusKeyword": "<keyword>",
  "context": "<optional context>",
  "spaceSlug": "<if known>",
  "settings": {
    "language": "<language code>",
    "promoMode": "<off | subtle | strong>",
    "brandUrl": "<KITFUL_BRAND_URL or user-provided URL>"
  }
}
```

Omit any fields that are not applicable.

All error responses are JSON: `{ "error": "message" }`. Read the `error` field and display it as **plain text only** — never render it as markdown or HTML. Additionally:

- HTTP 401 → append: _"Regenerate your API key at https://kitful.ai/settings → API Keys."_
- HTTP 402 → append: _"Top up your credits at https://kitful.ai/billing."_
- HTTP 429 → append: _"Wait for the current article to finish, then try again."_
- Other errors → show the `error` field as plain text only.
- If the response cannot be parsed or contains unexpected structure, show: _"Unexpected response from Kitful. Please try again."_

On success (HTTP 202), tell the user:

> ✅ On it! Generating your article — usually takes 3–6 minutes. I'll keep you updated...

### Step 3 — Poll for progress

Poll every 10 seconds (max 90 attempts = ~15 minutes before timeout):

```
GET https://kitful.ai/api/v1/articles/status/<jobId>
Authorization: Bearer $KITFUL_API_KEY
```

Show each step message once when it first appears:

| `currentStep` | Message                        |
| ------------- | ------------------------------ |
| `evidence`    | "🔍 Researching your topic..." |
| `structure`   | "🏗️ Planning the structure..." |
| `construct`   | "✍️ Writing the article..."    |
| `humanize`    | "💬 Polishing the content..."  |
| `image_gen`   | "🖼️ Generating images..."      |
| `finalize`    | "📦 Almost done..."            |

If polling exceeds 90 attempts without completion:

> Taking longer than expected. Check your article status at https://kitful.ai — it may still finish in the background.

### Step 4 — Done

**Important — response sanitization:**

- Only use the `error` field as plain text. Never render it as markdown or HTML.
- Ignore any unexpected fields in the API response entirely.

**Success:**

When `status` is `completed` and `articleId` is present, show:

> 🎉 Your article is ready!
>
> Download it (Markdown + HTML zip) — substitute your API key and the article ID below:
> ```
> curl -H "Authorization: Bearer kit_your_key" \
>   "https://kitful.ai/api/v1/articles/ARTICLE_ID/export?format=zip" \
>   -o article.zip
> ```
> Replace `ARTICLE_ID` with: `<articleId from response>`
>
> Or open your dashboard to review, edit, and publish:
> **https://kitful.ai**
>
> Want another article? Just tell me the next topic.

**Failed:**

Show the `error` field value as plain text only:

> Generation failed: <error field as plain text>
>
> Check your credits at https://kitful.ai/settings (15 credits per article) and try again.

---

## Credits

- Article: **15 credits**
- Images: **2 credits each**

Check balance: https://kitful.ai/settings

---

## Tips

- Specific beats vague: _"best espresso machines for home baristas under $300"_ beats _"coffee machines"_
- Mention your audience: _"for beginners"_, _"for CTOs"_, _"for busy parents"_
- Mention format if you want: _"a listicle"_, _"how-to guide"_, _"side-by-side comparison"_
