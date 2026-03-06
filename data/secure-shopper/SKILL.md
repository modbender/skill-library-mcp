---
name: secure-shopper
description: Asynchronous shopping research + checkout using secure-autofill (1Password-backed browser filling) with results recorded to workspace artifacts.
metadata:
  openclaw:
    emoji: "🛒"
---

# secure-shopper 🛒

Find items across one or more shopping sites, summarize candidates, and (optionally) place the order using **secure-autofill**.

This skill is **asynchronous**: spawn a sub-agent for browsing so the main chat stays responsive.

## Prerequisites

### Required skills / plugin

- The **secure-autofill** skill exists at: `~/.openclaw/skills/secure-autofill/`
- The secure-autofill plugin tools are available:
  - `vault_suggest`
  - `vault_fill`

### Inherit secure-autofill prerequisites

- A working non-headless Chrome (many shops block headless)
- Gateway environment has required env vars (per secure-autofill)

Concrete check:

```bash
command -v google-chrome || command -v google-chrome-stable
```

## Configuration (portable)

Skill-local config files:

- Example (shareable, do not edit): `~/.openclaw/skills/secure-shopper/config.json.example`
- Real (machine-specific, written by onboarding): `~/.openclaw/skills/secure-shopper/config.json`

Config keys:

- `goToSites[]`: list of default shopping sites (e.g. Amazon, Walmart)
- `location.zip` or `location.address`: used for shipping/availability context
- `preferences.priority`: one of:
  - `relevancy`
  - `cheaper`
  - `faster`
  - `reviews`
- `preferences.maxCandidatesPerSite`: cap per site (default 5)
- `preferences.safeBrowsing`: guardrails to avoid oversized pages / context overflow (applies to all sites)
  - `startFromSearch`: `true|false` (default true) — prefer a site’s search results page over the homepage/product pages
  - `maxCandidatesPerPass`: number (default 3) — extract a few items at a time (then paginate/scroll)
  - `snapshot`: limits for `browser.snapshot`
    - `compact`: boolean (default true)
    - `depth`: number (default 6)
    - `maxChars`: number (default 12000)
  - `fallback`: what to do on `context_length_exceeded`
    - `retryWithTighterSnapshot`: boolean (default true)
    - `switchToSearchUrl`: boolean (default true)

## Initialization / installation / onboarding

### Preferred (chat-first)

Ask Boss and then write `config.json`:

1) Go-to shopping website(s)
   - Examples: Amazon, Walmart, Target
   - Store into `goToSites[]`

2) Zip code OR proximity address
   - Store into `location.zip` and/or `location.address`

3) Preferences
   - Ask for priority: relevancy vs cheaper vs faster delivery vs higher review scores
   - Store into `preferences.priority` (+ optional notes)

After collecting answers, update the real config file.

Optional helper (terminal):

```bash
node ~/.openclaw/skills/secure-shopper/scripts/onboard.mjs \
  --sites 'Amazon=https://www.amazon.com|Walmart=https://www.walmart.com' \
  --zip 46202 \
  --priority cheaper
```

## How it works (agent behavior contract)

### 0) Require a shopping description

The user must provide a description of their shopping task.

- If they didn’t: **stop and ask for it**.

### 1) Honor runtime user prompts

Runtime user instructions (the user’s message for this run) override stored config.

Examples of runtime overrides:

- “Use Target instead of Amazon.”
- “Only show Prime-eligible.”
- “Budget under $50.”

### 2) Login via secure-autofill (skip if already logged in)

- Use the configured go-to sites, unless the runtime prompt specifies a site.
- If the site session appears already authenticated: skip login.
- Otherwise, use secure-autofill login flow:
  - `browser.snapshot` to get refs
  - `vault_suggest`/`vault_fill` to fill credentials

### 3) Make the browsing asynchronous

Immediately after accepting the task, respond with something like:

> I’m en route to the stores. I’ll notify you when I find the best matches.

Then spawn a sub-agent so the main session is not interrupted.

Implementation note:

- Use `sessions_spawn` with a task that includes the shopping description and any runtime overrides.

### 4) Browse + identify candidates

The sub-agent browses each chosen site, searches, filters, and identifies candidates that fit the user description.

#### Context-safe browsing (ALL shopping sites)

Many shopping sites can produce extremely large pages/snapshots. To avoid `context_length_exceeded` failures:

- Prefer starting from a **search results URL** (or the site’s search box) rather than the homepage.
- Use **small snapshots**:
  - `browser.snapshot(..., compact=true)`
  - keep `depth` modest (e.g., 4–8)
  - set `maxChars` and/or target a **specific container** when possible
- Extract **incrementally**:
  - grab top ~3 candidates, record them, then paginate/scroll and repeat until `maxCandidatesPerSite` is met
- If a snapshot still overflows:
  - retry with a tighter snapshot (smaller depth / smaller region)
  - switch to a search URL (`/search?q=...`) and re-extract
- Do not “reason through” massive dumps. If the page is huge, **reduce the page slice** first.

Record results to:

`/home/miles/.openclaw/workspace/artifacts/secure_shopping/{timestamp}_shopping_task.json`

JSON requirements:

- Record:
  - `userPrompt` (shopping description)
  - `startTime`
  - `endTime`
  - `phase` (required):
    - `candidates_found` | `awaiting_accept_deny` | `awaiting_checkout_confirm` | `ordered`
  - `candidates[]`
- Candidates for the same request must live under the same parent task.
- Each candidate must include:
  - `price` (string)
  - `reviewScore` (string/number)
  - `url`
  - `verdict` (short)
  - `status`: `pending` | `accepted` | `denied` | `shopped`

Suggested candidate shape:

```json
{
  "site": "Amazon",
  "title": "...",
  "price": "$39.99",
  "reviewScore": "4.6 (12,345)",
  "url": "https://...",
  "verdict": "Best value under $50; good reviews; ships tomorrow",
  "status": "pending"
}
```

Helper module (optional): `scripts/task_io.mjs`.

### 5) Notify user + REQUIRE accept/deny (hard gate)

When browsing is done, you must:

1) Set JSON `phase = "awaiting_accept_deny"`.
2) Translate the JSON into a human-friendly summary.
3) **In the same message, require an ACCEPT/DENY decision. Do not end the turn without the prompt.**

Mandatory message template (copy this structure):

- **Recommended pick:** <title> — <price> — <reviewScore> — <1-line why>
- **Other options:** (optional, 1–5 bullets)
- **Choose:** Reply with `A=accept/deny, B=accept/deny, ...` (or “Accept A” / “Deny B”).
- **Next step:** “If you accept one: do you want me to checkout, or stop at ready-to-buy?”

Hard rule:
- If you listed candidates/links but did not include an explicit **Choose (ACCEPT/DENY)** line, the output is invalid and must be rewritten before sending.

### 6) Apply accept/deny updates

Once the user replies:

- Update each candidate `status` to `accepted` or `denied`.
- Confirm the accepted candidate(s).
- Set JSON `phase`:
  - `awaiting_checkout_confirm` if at least one is accepted and checkout is not yet confirmed
  - keep `awaiting_accept_deny` if the user’s response is ambiguous / incomplete

### 7) Checkout (only after explicit confirmation)

Before you click any “Place order” / “Submit” equivalent:

- Ask for a clear confirmation like: **“Confirm checkout for A? (yes/no)”**
- Set JSON `phase = "awaiting_checkout_confirm"` until confirmed.

If the user confirms checkout:

- Navigate to the accepted candidate’s URL
- Add to cart / proceed to checkout
- Use **secure-autofill** to input payment/shipping info and submit

If secure-autofill reports an error:

- Do not guess.
- Pass the error back to the user.

### 8) Mark as shopped

If the order is successfully placed:

- update that candidate’s `status` to `shopped`
- set JSON `phase = "ordered"`

## Notes / guardrails

- Never paste secrets.
- Checkout flows often require MFA / SMS verification; ask the user when needed.
- Prefer fewer high-quality candidates over a long list.
