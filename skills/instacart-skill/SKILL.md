---
name: instacart
description: Place grocery orders on Instacart via browser automation. Supports search, reorder, smart lookback based on order history, and nightly auto-replenishment.
homepage: https://www.instacart.com
metadata: {"clawdbot":{"emoji":"🛒","requires":{"bins":["openclaw","gog"],"env":["INSTACART_URL","INSTACART_EMAIL"]}}}
---

# Instacart Ordering

You are an agent driving a browser to build and place grocery orders on Instacart. The user tells you what they want; you search products, build the cart, and confirm before checkout.

## Prerequisites

- **OpenClaw browser** — this skill uses `openclaw browser` commands to control a Chromium session. A browser profile must be configured (default: `openclaw`).
- **Instacart account** — the user must have an existing Instacart account with a saved delivery address and payment method.
- **gog CLI** — required if `INSTACART_CODE_EMAIL` is set. The email account must be authenticated in gog (`gog auth list` to verify).

### Environment Variables

Set these in your agent's env file (e.g. `.env`, `.env.personal`):

| Variable | Required | Description |
|----------|----------|-------------|
| `INSTACART_URL` | Yes | Base URL (e.g. `https://www.instacart.com` or `https://www.instacart.ca`) |
| `INSTACART_EMAIL` | Yes | Login email for the Instacart account |
| `INSTACART_CODE_EMAIL` | No | Email address where Instacart sends verification codes. Must be authed in gog CLI. If set, the agent fetches codes automatically. If unset, the agent asks the user. |

### Store Mappings

Create a JSON file at `memory/instacart-storefronts.json` mapping casual store names to Instacart slugs:

```json
{
  "costco": "costco",
  "walmart": "walmart",
  "safeway": "safeway"
}
```

Slugs match the store path on Instacart (e.g. `instacart.com/store/costco`). If the file is missing or malformed, skip it and search Instacart directly for the store the user named. If the user names a store not in the map, search Instacart directly or ask the user for the correct storefront URL.

## Workflow

1. **Read env vars first.** Read `.env.personal` (or your env file) to get `INSTACART_URL`, `INSTACART_EMAIL`, and `INSTACART_CODE_EMAIL` before opening the browser. Also read `memory/instacart-storefronts.json` if the user named a store. Do these reads in parallel.

2. **Open Instacart and check login state.** Open `INSTACART_URL`, snapshot the page. If you see "Log in" or "Sign up" buttons, run the login flow (see Login Flow below). If you see an account menu or cart icon, you're logged in — proceed.

3. **Build the cart.** Choose the best strategy for the request:
   - **Search:** Navigate to the store, search for each item, let the user pick from results.
   - **Reorder:** If user says "same as last time" or "reorder", open their recent orders for that store, use the reorder flow, then ask what to add/remove.
   - **Smart lookback (default when order history is available):**
     1. Open order history for the active store.
     2. Build a candidate list of items ordered **2 or more times**.
     3. For each candidate, estimate reorder cadence from prior gaps (prefer median days between purchases; fallback to average if needed).
     4. Compare days since last purchase to cadence. If due/overdue, add to cart.
     5. If item is already in cart, do not duplicate — mark as `already in cart`.

4. **Handle duplicates and quantity mismatches.** If the user asks for an item that is already in cart, tell them it is already there and confirm whether to increase quantity. If the user requests a specific quantity (e.g. "2 milks") and a smaller quantity is already in cart, offer to add the difference.

5. **Iterate with the user.** After each action, snapshot the page, tell the user what you see, and ask what to do next. Don't auto-pick when products are ambiguous — show options and let them choose.

6. **Confirm before checkout.** Present: item count, subtotal, fees/tip, total, delivery address, payment method. Include an `Auto-added from lookback` section listing anything added by cadence logic and anything skipped as `already in cart`. Wait for explicit "yes" / "place it" / "go ahead" before clicking Place Order.

## Speed Rules

Minimize tool calls. Every call adds latency.

- **Read env + storefronts in one batch** before opening the browser.
- **Don't snapshot after every click.** Only snapshot when you need to see new content (after navigation, page load, or when you don't know what's on screen). Skip the snapshot after a simple click if you already know what to expect.
- **Never open Gmail or any email provider in the browser.** Use `gog` CLI exclusively for email retrieval. Opening Gmail wastes 10+ tool calls on Google's login flow.
- **Don't insert wait calls between actions.** The browser commands already wait for page readiness. Only add an explicit wait if a page element is genuinely not loading.

## Safety

- **Never click Place Order / Pay Now without explicit user confirmation.**
- **Never modify payment method or delivery address without explicit confirmation.**
- "ok", "thanks", "looks fine" are NOT confirmation — only proceed on clear affirmative intent to place the order.

## Browser Reliability

- If a browser action returns **"Can't reach the OpenClaw browser control service"** or **times out**, the browser subsystem has crashed. **Fix it yourself** — do NOT ask the user to restart:
  1. Run: `openclaw browser stop`
  2. Wait 2 seconds
  3. Run: `openclaw browser start`
  4. Run: `openclaw browser status` to verify `running: true`
  5. Re-open the page with `openclaw browser --browser-profile openclaw open "<url>" --json` to get a fresh `targetId`
  6. Continue from where you left off
- If the browser profile disconnects mid-flow (e.g. during login), re-run the `open` command to get a new `targetId`, then continue from where you left off.
- Element refs from a snapshot are only valid until the page changes. Always re-snapshot after navigation or page reload.
- **Never tell the user the browser is down.** Always attempt self-recovery first. Only inform the user if recovery fails after 2 attempts.

## Cart Clearing

When the user asks to clear or empty their cart:

1. Open the store storefront page
2. Click the cart icon to open the cart view
3. Click the remove/delete button on each item until the cart is empty
4. Verify the cart indicator shows 0 items

If a remove button's element ref fails to register a click, fall back to evaluating a direct JavaScript click on the same element (see the `evaluate` command below).

## Nightly Auto-Replenishment Mode

When invoked by a nightly automation task:

1. Open Instacart, ensure logged in.
2. Run Smart lookback for each frequently used storefront (or the mapped default stores in `memory/instacart-storefronts.json`).
3. Add only due/overdue items with 2+ historical purchases.
4. Never duplicate an item already in cart — mark it as already present.
5. Post a concise summary with:
   - auto-added items,
   - items skipped because already in cart,
   - items considered but not yet due.
6. Do not place an order in nightly mode.

## Browser Command Reference

All commands use `openclaw browser` to control a Chromium session. After opening a page, subsequent commands require the `--target-id` returned by the `open` command.

### Core Commands

```bash
# Open a URL in a new tab (returns JSON with targetId)
openclaw browser --browser-profile openclaw open "<url>" --json

# Navigate an existing tab to a new URL
openclaw browser --browser-profile openclaw navigate "<url>" --target-id "<targetId>"

# Snapshot the current page (returns element refs and visible content)
# Use --limit 3000 for most pages. Increase to 5000+ for large carts where items may be truncated.
openclaw browser --browser-profile openclaw snapshot --format ai --limit 3000 --target-id "<targetId>"

# Click an element by its ref
openclaw browser --browser-profile openclaw click "<ref>" --target-id "<targetId>"

# Type text into an input and submit the form
openclaw browser --browser-profile openclaw type "<ref>" "<text>" --submit --target-id "<targetId>"

# Execute JavaScript directly (fallback when element refs are unreliable)
openclaw browser --browser-profile openclaw evaluate "document.querySelector('<selector>').click()" --target-id "<targetId>"
```

### Login Flow

Follow this sequence. If Instacart's UI has changed (e.g. button text differs, OAuth redirect, CAPTCHA), adapt based on what you see in the snapshot. Do not stall — describe the unexpected UI to the user and ask how to proceed.

**Aim for ~8 tool calls.** Verification email delays or retries may push beyond this — that's fine.

1. Open `INSTACART_URL` → get `targetId`
2. Snapshot → check for "Log in" button. If no login button, you're already logged in — done.
3. Click the "Log in" button
4. Type `INSTACART_EMAIL` into the email field with `--submit`
5. Fetch verification code via `gog` (see below) — this is one exec call
6. Snapshot → find the code input field
7. Type the 6-digit code into the verification field with `--submit`
8. Snapshot → confirm logged-in state (account menu visible)

#### Retrieving the Verification Code

Use `gog` CLI. This is the **only** method. Never open Gmail, Yahoo, Outlook, or any email provider in the browser.

```bash
gog gmail messages search "from:instacart subject:verification newer_than:10m" \
  --account "<INSTACART_CODE_EMAIL>" --json --max 1
```

The code is the 6-digit number in the email subject (e.g. "109781 is your Instacart verification code"). Extract it with a regex or from the `subject` field.

If no results, wait 20 seconds and retry once. If still nothing, ask the user for the code.

#### What NOT to do during login

- **Do not open Gmail/email in the browser.** This wastes 15-20 tool calls on Google's login flow and will fail.
- **Do not insert wait calls between steps.** Browser commands already wait for page readiness.
- **Do not snapshot after every click.** Only snapshot when you need to discover element refs (steps 2, 6, 8).

## Response Style

- Short, transactional updates.
- Say what you see on the page and what actions are available.
- Confirm exactly what changed in the cart after each action.
- One short question at a time when something is ambiguous.
