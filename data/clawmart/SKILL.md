---
name: clawmart
description: Create, manage, and publish ClawMart personas and skills directly from OpenClaw chat. Use when creating listings on ClawMart, uploading skill/persona packages, updating existing listings, or managing a ClawMart creator account.
---

# ClawMart Creator

## Prerequisites
- ClawMart creator account with active subscription
- `CLAWMART_API_KEY` env var set (format: `cm_live_...`)

## Commands
- "Create a skill on ClawMart for [description]"
- "Create a persona on ClawMart for [description]"
- "Update my [listing name] on ClawMart"
- "Upload a new version of [listing name]"
- "Show my ClawMart listings"

## Workflow
1. Brainstorm listing ideas with user before writing metadata.
2. **⚠️ DUPLICATE CHECK (mandatory):** Before creating ANY new listing, search your existing listings first:
   - `GET /listings` — fetch all your current listings
   - Compare the proposed listing name, description, and category against existing ones
   - If a matching or very similar listing already exists, UPDATE it (`PATCH /listings/{id}` + new version) instead of creating a new one
   - Only proceed to `POST /listings` if no existing listing covers the same functionality
3. Draft and confirm required fields: name, tagline, about, category, capabilities, price, product type.
4. `GET /me` — validate creator access and subscription.
5. `POST /listings` — create draft listing.
6. Generate package files:
   - **Persona**: SOUL.md, MEMORY.md, supporting docs.
   - **Skill**: complete SKILL.md (follow skill-creator conventions).
7. `POST /listings/{id}/versions` — upload package (multipart or base64 JSON).
8. **Ask for explicit user confirmation before publishing.**
9. Summarize: dashboard URL + public URL.

## API Reference
- **Base URL:** `https://www.shopclawmart.com/api/v1/`
- **Auth:** `Authorization: Bearer ${CLAWMART_API_KEY}`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /me | Creator profile & subscription |
| GET | /listings | List creator's listings |
| POST | /listings | Create listing metadata |
| PATCH | /listings/{id} | Update listing metadata |
| DELETE | /listings/{id} | Unpublish/delete listing |
| POST | /listings/{id}/versions | Upload package version |

## Price Field

⚠️ **CRITICAL: The `price` field is in DOLLARS, not cents.**

- `"price": 14.99` → $14.99 ✅
- `"price": 1499` → $1,499.00 ❌ (this is NOT cents!)
- `"price": 0` → Free listing ✅
- Minimum paid price: $3.00

When a user says "set price to $14.99", send `"price": 14.99`. Do NOT multiply by 100. The API stores cents internally but accepts and returns dollar values.

## Guardrails
- Never expose raw API keys in chat output.
- Require user confirmation before publishing.
- Validate payloads before each API call.
- Return clear errors with suggested fixes on failure.
