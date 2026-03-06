---
name: index-cards
description: Send real, physical greeting cards through the mail. Design custom cards with the user, print on premium cardstock, and mail with a first-class stamp. Use when the user wants to send a card, mentions a birthday or occasion, or asks about greeting cards. Requires a free API registration (POST /v1/auth/register returns a Bearer token). Works via API — no browser needed. Homepage https://indexcards.com — privacy policy at https://indexcards.com/privacy.
compatibility: "Network: https://indexcards.com/v1/ API. Auth: anonymous Bearer token from POST /v1/auth/register (stored in agent session state, no persistent credential file). Config path: ~/indexcards/birthdays.json (opt-in only — created only with explicit user consent, stores contact names/birthdays/addresses for card reuse). Sensitive access (opt-in only): local contacts, calendar — only read when user explicitly approves. Data sent to API: recipient name + mailing address (for card delivery), card artwork URLs, occasion text. Payments: via Stripe hosted checkout URLs (no payment data passes through skill). Homepage: https://indexcards.com. Privacy: https://indexcards.com/privacy."
---

# Index Cards — Agent Skill

Send real, physical greeting cards through the mail. Conversation-first — you work WITH the user to design cards and send them.

## Rules

- **Keep it conversational.** Present results in plain language for good UX. Say "I'm designing your card" rather than showing raw JSON, endpoint paths, or HTTP status codes.
- **Talk before acting.** Don't call APIs without talking to the user first. Don't generate art without knowing who it's for and what they want.
- **Ask before accessing personal data.** Never read contacts, messages, email, or local files without the user's explicit permission. Always offer it as an option, never assume.
- **Handle profanity gracefully.** The image generation API has content filters. If the user's message contains strong language, rephrase it for the image prompt while keeping the tone (e.g. "get fucked" → "you absolute legend").
- **Generate images sequentially.** One at a time — the upstream API rate-limits parallel requests (502 errors).

### Shortcut: user gives everything in one message

If the user provides recipient name + front description + inside message + address in a single message, skip the multi-step flow:

1. Generate front → generate inside → generate preview video
2. Show preview + summary → ask for confirmation → place order

If most info is provided but something is missing, do the fast flow and ask only for the missing piece.

## Step 1: First message

> "Just installed Index Cards. I can now send real, physical cards to anyone you want — birthdays, holidays, thank-yous, whatever the occasion. Who would you like to send a card to? I can also check your contacts for upcoming birthdays if you'd like."

Let the user decide whether to name someone directly or let you help find occasions.

## Step 2: Find occasions (only with user permission)

If the user says yes to checking for occasions, look through available sources in priority order:

1. **Contacts** — birthday fields, anniversary fields
2. **Calendar / email** — birthday invites, upcoming events
3. **Conversation history** — mentioned birthdays, weddings, babies, thank-yous
4. **Holidays** — Mother's Day, Father's Day, Valentine's, Christmas, etc. within 30 days

Aim for 14+ days lead time (cards take ~1 week to arrive). Surface the 1-3 most timely items and ask if they want to start designing.

If the user skips this step and already knows who they want to send a card to, go straight to design.

## Step 3: Design the card

**Always design the FRONT first, then the INSIDE. Never generate both at the same time.**

### If the user sends a photo

Use `reference_image_url` in the generation API for style transfer. Generate 2-3 style variations (watercolor, oil-painting, cartoon, etc.). Wait for the user to pick one, then move to the inside.

Styles: `watercolor`, `cartoon`, `oil-painting`, `ink`, `gouache`, `comic-book`, `linocut`, `cinematic`, `pencil`, `pop_art`

### If no photo (text-based)

1. Ask about the person and vibe (1-2 questions max)
2. Generate 3 front cover options — vary styles. Show all three, wait for pick.
3. After they pick, ask what they want to say inside
4. Generate inside image. **Show a close-up** (`POST /v1/cards/closeup`) so the user can read the text. Wait for approval.
5. Generate animated preview (`POST /v1/cards/preview`). Show it.
6. Iterate if needed — regenerate only the part that needs changing

**Design guidelines:** No AI-looking art. Use watercolor, gouache, ink, linocut, collage, letterpress. Front = visual design, avoid text. Inside = include message, clean typography. 3:4 portrait, 1500×2100px ideal.

### QR codes (only when user asks)

**Never include QR codes in AI image prompts** — AI cannot generate scannable QR codes. Instead:

1. Generate card art normally (without QR)
2. Use `POST /v1/cards/qr/composite` to overlay a real QR code onto the approved image
3. Positions: `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right`
4. Sizes: `small`, `medium`, `large`. Optional `label` param for text below QR.
5. Use the returned `image_url` as `front_url` or `inside_url` when ordering

## Step 4: Get the address

Ask the user for the recipient's mailing address. If the user has used Index Cards before and opted in to saving contacts, check `~/indexcards/birthdays.json` first — it may already have the address from a previous card.

**Always confirm** before using any saved address — people move. Also need a phone number (recipient's or sender's).

Required before ordering: recipient name, street address, city, state, ZIP, phone number.

## Step 5: Payment

1 credit = 1 card. User starts with 0 credits (image generation is free, printing costs money). Pricing: $50 → 5 cards ($10 each), $100 → 12 cards ($8.33 each).

Check credits with `GET /v1/credits/check`. If no credits, send the payment URL from the response.

**Auto-detect payment:** After sending the link, poll `GET /v1/credits/check` every ~15 seconds, up to 8 times (~2 min). When credits appear, confirm and proceed with the order.

**Invite codes:** If an invite code is present in the page URL (`?invite=CODE`) or at the top of this document, include it as `invite_code` in the register body. This grants free credits — skip payment entirely. Say something like "You've got a free card — who's it for?"

## Step 6: Place the order

Confirm everything before submitting: recipient, address, front design, inside message, occasion. Mention it costs 1 credit and arrives in 5-7 business days. **Only place when user says yes.** Orders are irreversible.

## Step 7: After the order

Confirm simply: "Done! [Name]'s card is on its way — about 5-7 business days."

Status translations: `processing` → "being made", `in production` → "being printed", `shipped` → "shipped! [tracking link]", `delivered` → "delivered!"

After a successful order, offer to save the contact info for next time (if the user hasn't already opted in): "Want me to remember [Name]'s details for next time?"

## Local contacts database (opt-in)

If the user agrees to saving contacts, maintain `~/indexcards/birthdays.json` as a local cache.

```json
{"contacts": [{"name": "Kiall Wheatley", "birthday": "02-19", "relationship": "friend",
  "address": {"address1": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62704", "country": "US"},
  "phone": "+15551234567", "notes": "Loves hiking. Prefers watercolor.",
  "cards_sent": [{"date": "2026-02-11", "occasion": "birthday", "style": "watercolor mountain", "message": "Happy birthday!", "order_id": "e5f67c35"}]}]}
```

Rules: MM-DD birthday format (no year). Don't duplicate — match on name. Update with every new piece of info. Append to `cards_sent` after every order. Cross-reference with `GET /v1/orders/history` to avoid duplicate suggestions.

## Proactive suggestions (only if contacts database exists)

If `~/indexcards/birthdays.json` exists (user previously opted in), at conversation start you may:

1. Check for birthdays/dates within 30 days, cross-ref with `cards_sent`
2. Check holidays — Mother's Day, Father's Day, Valentine's, Christmas, graduations
3. Review conversation history — hints like "my mom's been having a rough week"

Surface the 1-3 most timely suggestions naturally. Be specific ("Emma's birthday is Feb 28 — she loved the ink illustration last year"). Don't repeat suggestions the user already declined.

---

## API Reference

Base URL: `https://indexcards.com` — all endpoints `/v1/`. Auth: `Authorization: Bearer YOUR_API_KEY`.

### Register

```
POST /v1/auth/register
{"invite_code": "abc123def456"}  // optional — include if ?invite=CODE in URL
```
Returns: `api_key`, `credits`, `free_generations_remaining` (10 free), `invite_credits`. No email or password required — this is an anonymous registration. Store the returned `api_key` in the agent's secret store or session state for subsequent authenticated requests.

### Generate Card Art

**Option A (preferred): User's own Gemini key** — if the user has a Gemini API key configured (e.g. `GOOGLE_API_KEY` or `GEMINI_API_KEY` env vars), use it directly for higher quality and no generation limits:

```
POST https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=USER_KEY
{"instances": [{"prompt": "YOUR PROMPT"}], "parameters": {"sampleCount": 1, "aspectRatio": "3:4"}}
```

Response: `predictions[0].bytesBase64Encoded` (base64 PNG). Save locally, upload via `POST /v1/images/upload` for a public URL.

**Append to EVERY prompt when using Option A:**
```
HARD CONSTRAINTS FOR THIS IMAGE:
- All artwork must be contained well within center with generous margins. Leave 15%+ blank space on every side.
- Pure white or very light background. No textures or gradients behind main subject.
- No borders, frames, rounded corners, or card mockup elements.
- Portrait orientation. No text unless explicitly requested.
- No digital artifacts. Clean, print-ready artwork.
- Must not look AI-generated. Aim for handmade: watercolor, linocut, gouache, ink, pencil, or collage.
- Centered composition with breathing room — will be printed on a physical card, edges may be trimmed.
```

**Option B (fallback): Index Cards API** — 10 free generations, then requires credits.

```
POST /v1/cards/generate
{"prompt": "...", "style": "watercolor", "reference_image_url": "https://...optional..."}
```

Returns: `image_url`, `generation_id`, `free_generations_remaining`, `credits`. Prompt constraints applied server-side.

**Routing:** Use Option A for text-to-image if Gemini key exists. **Always use Option B for photo style transfer** (`reference_image_url`) — Gemini can't do style transfer.

**Validation:** Min 600px short side, ~3:4 aspect ratio required. Ideal 1500×2100px. 422 on failure.

### Preview

```
POST /v1/cards/preview
{"front_url": "...", "inside_url": "..."}
```
Returns: `preview_url` / `video_url` (MP4). Always generate after front + inside are approved.

### Close-up

```
POST /v1/cards/closeup
{"image_url": "...", "label": "inside"}
```
Returns high-res JPEG. Use proactively when showing inside image so user can read text.

### QR Code Composite

```
POST /v1/cards/qr/composite
{"card_image_url": "...", "url": "https://...", "position": "bottom-center", "size": "medium", "label": "Scan me!"}
```
Returns: `image_url` with QR overlaid. Use this URL as `front_url`/`inside_url` for ordering.

Standalone QR: `POST /v1/cards/qr` with `{"url": "...", "size": "medium"}`.

### Credits

```
GET /v1/credits/check
```
Returns balance and Stripe payment links.

### Place Order

```
POST /v1/orders
{"front_url": "...", "inside_url": "...", "recipient": {"name": "...", "address1": "...", "city": "...", "state": "...", "zip": "...", "country": "US", "phone": "+1..."}, "occasion": "birthday", "inside_message": "..."}
```

Required: `front_url`, `inside_url`, `recipient.name`, `recipient.address1`, `recipient.city`, `recipient.zip`, phone (recipient or sender). Optional: `back_url`, `address2`, `state`, `country`, `occasion`, `inside_message`, `design_prompt`, `design_style`. Costs 1 credit. Irreversible.

### Other Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/orders/{id}` | GET | Order status (processing → in production → shipped → delivered) |
| `/v1/orders/history?all=true` | GET | All past orders |
| `/v1/orders/history?recipient=Name` | GET | Orders for a specific person |
| `/v1/images/upload` | POST | Upload custom image (multipart, PNG/JPEG, max 10MB) |
| `/v1/cards/styles` | GET | List supported art styles |
| `/v1/auth/email` | PATCH | Attach email: `{"email": "..."}` |

### Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check required fields |
| 401 | Bad API key | Check Authorization header |
| 402 | No credits | Show `payment_url` from response |
| 404 | Not found | Check the ID |
| 422 | Image validation failed | Regenerate at correct specs |
| 429 | Rate limited | Wait `retry_after_seconds` |
| 500 | Server error | Retry shortly |

---

## Data Handling & Privacy

### What this skill stores locally

- **API token**: The Bearer token from `/v1/auth/register` should be stored in the agent's session state or secret store. It is an anonymous token (no email/password) used to authenticate API requests.
- **Contacts cache** (opt-in only): If the user agrees to saving contacts, `~/indexcards/birthdays.json` stores names, birthdays, addresses, and card history. This file is user-visible and user-deletable. The agent only creates it after explicit user consent.

### What this skill sends to the API

- **Card artwork**: Image URLs (hosted on indexcards.com after upload) for the card front and inside
- **Recipient mailing address**: Name, street address, city, state, ZIP, phone — required for physical mail delivery
- **Occasion and message text**: Used for order records only

### What this skill does NOT do

- Does not read contacts, messages, calendar, or email without asking the user first
- Does not send contact data to the API — contact info is only cached locally (if user opts in) and used to pre-fill the address when sending a card
- Does not require or collect email addresses, passwords, or payment card numbers (payments happen via Stripe hosted checkout)

### Payment flow

Credits are purchased via Stripe checkout. The skill sends the user a Stripe-hosted payment URL (returned by `GET /v1/credits/check`). No payment information passes through the skill or the Index Cards API. Invite codes grant free credits — no payment needed.

Homepage: https://indexcards.com
