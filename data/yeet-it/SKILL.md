---
name: yeetit-publish
description: Publish HTML as a live website instantly. POST HTML, get a shareable URL. No account needed. Always asks the user for confirmation before publishing.
version: 1.0.2
metadata:
  openclaw:
    requires:
      bins:
        - curl
    homepage: https://yeetit.site
    emoji: 🚀
---

# YeetIt — Instant Web Publishing

Publish any HTML content as a live, shareable website in one API call. No account, no authentication, no setup required.

**IMPORTANT: Always ask the user for explicit confirmation before publishing.** Publishing creates a publicly accessible URL. Never publish silently or autonomously — always confirm first.

## When to Use This Skill

Use this skill when the user wants to:
- Share HTML, a report, dashboard, or document as a live website
- Deploy a landing page, portfolio, or event page instantly
- Publish any web content and get a shareable URL
- Create a temporary or permanent website from generated content

## How to Publish

Make a POST request to the YeetIt API:

```bash
curl -X POST https://yeetit.site/v1/publish \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello World</h1></body></html>",
    "title": "My Page"
  }'
```

The response includes:
- `url` — the live, shareable URL (e.g. https://yeetit.site/hello-world-k3m)
- `edit_key` — key for future updates (save this)
- `claim_url` — link for the user to claim permanent ownership

## Updating a Published Site

```bash
curl -X PUT https://yeetit.site/v1/sites/{slug} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {edit_key}" \
  -d '{"html": "<html><body><h1>Updated</h1></body></html>"}'
```

## Including Assets (CSS, JS, images)

Pass an `assets` map alongside the HTML:

```json
{
  "html": "<html><head><link rel='stylesheet' href='./style.css'></head><body>Hello</body></html>",
  "assets": {
    "style.css": "body { font-family: sans-serif; color: #333; }"
  }
}
```

## Limits (Free Tier)

- Max site size: 5 MB (HTML + assets)
- Max assets: 10 per site
- Expiry: 24 hours (claim via email to extend to 7 days; Pro plan for permanent)
- Max active sites: 5

## Confirmation Requirement

**You MUST ask the user for explicit confirmation before every publish or update.** This is mandatory because publishing creates a publicly accessible URL that anyone can visit.

Before calling the API, always tell the user:
1. What will be published (a brief summary of the content)
2. That it will be publicly accessible to anyone with the link
3. Ask: "Should I publish this?"

Only proceed after receiving an affirmative response. Never publish automatically, silently, or as part of a larger workflow without pausing for confirmation.

## Security — Sensitive Data Warning

**Published sites are publicly accessible.** Before publishing, you MUST review the HTML content and ensure it does not contain:

- API keys, tokens, or secrets
- Passwords or credentials
- Private personal information (SSNs, medical records, financial account numbers)
- Internal/proprietary data not intended for public sharing
- Environment variables or configuration values from the local system

**Do not read local files, environment variables, or credentials and embed them in published HTML.** Only publish content the user has explicitly provided or asked you to generate.

## Important Notes

- Always confirm with the user before publishing — never publish autonomously
- Always show the user the published URL after publishing
- Save the `edit_key` from the response if the user may want to update the site later
- Suggest the user visit the `claim_url` to take permanent ownership
- For sites that need to persist, suggest the Pro plan ($8/mo)
