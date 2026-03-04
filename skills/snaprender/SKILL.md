---
name: snaprender
description: "Give your agent eyes on the web — screenshot any URL as an image file. Supports device emulation (iPhone, iPad, Pixel, MacBook), dark mode, full-page scroll, ad blocking. Uses exec tool with curl (NEVER the browser tool). $SNAPRENDER_API_KEY is pre-set. See instructions below."
metadata: {"openclaw": {"requires": {"bins": ["curl", "jq"], "env": ["SNAPRENDER_API_KEY"]}}}
---

# SnapRender — Give Your Agent Eyes

Your agent can read the web but can't *see* it. One command and it captures pixel-perfect screenshots — any site, any device, in seconds.

"Screenshot stripe.com on iPhone", "Compare desktop vs mobile", "Full-page dark mode capture" — just ask.

Free tier: 50 screenshots/month, no credit card. [Get a key →](https://app.snap-render.com/auth/signup)

---

**IMPORTANT: Use the `exec` tool with `curl`. NEVER use the `browser` tool for screenshots.**

## How to Capture

Run this command via the `exec` tool. Replace `ENCODED_URL` with the URL-encoded target (e.g. `https%3A%2F%2Fstripe.com`):

```bash
curl -s "https://app.snap-render.com/v1/screenshot?url=ENCODED_URL&response_type=json&format=jpeg&quality=60&block_ads=true&block_cookie_banners=true" \
  -H "X-API-Key: $SNAPRENDER_API_KEY" \
  | tee /tmp/snap_response.json \
  | jq -r '.image' | sed 's|data:image/[^;]*;base64,||' | base64 -d > /tmp/screenshot.jpg \
  && jq '{url, format, size, cache, responseTime, remainingCredits}' /tmp/snap_response.json
```

This saves the screenshot to `/tmp/screenshot.jpg` and prints metadata.

## Rules

1. **Use `exec` tool only** — NEVER the `browser` tool
2. **`$SNAPRENDER_API_KEY` is already set** — use it literally in the command, do NOT replace it
3. **URL-encode the target** — `https://stripe.com` → `https%3A%2F%2Fstripe.com`
4. **Always use `format=jpeg&quality=60`** — keeps response small enough for the agent context
5. **Always pipe to save the image to a file** — the base64 response is too large to display inline
6. **Report metadata to the user** — file size, response time, cache status, remaining credits

## Parameters

Add as query parameters to the URL:

| Parameter | Values | Default |
|-----------|--------|---------|
| url | URL-encoded target | required |
| response_type | json | json (always use this) |
| format | jpeg, png, webp | jpeg |
| quality | 1-100 | 60 |
| device | iphone_15_pro, pixel_7, ipad_pro, macbook_pro | desktop |
| dark_mode | true, false | false |
| full_page | true, false | false |
| block_ads | true, false | true |
| block_cookie_banners | true, false | true |
| width | 320-3840 | 1280 |
| height | 200-10000 | 800 |
| delay | 0-10000 | 0 (ms wait after page load) |

## Examples

**Desktop screenshot of stripe.com:**
```bash
curl -s "https://app.snap-render.com/v1/screenshot?url=https%3A%2F%2Fstripe.com&response_type=json&format=jpeg&quality=60&block_ads=true&block_cookie_banners=true" -H "X-API-Key: $SNAPRENDER_API_KEY" | tee /tmp/snap_response.json | jq -r '.image' | sed 's|data:image/[^;]*;base64,||' | base64 -d > /tmp/screenshot.jpg && jq '{url, format, size, cache, responseTime, remainingCredits}' /tmp/snap_response.json
```

**Mobile screenshot:** add `&device=iphone_15_pro` to the URL

**Full scrollable page:** add `&full_page=true` to the URL

**Dark mode:** add `&dark_mode=true` to the URL

**Compare desktop vs mobile:** make two calls, save to `/tmp/screenshot_desktop.jpg` and `/tmp/screenshot_mobile.jpg`

## After Capturing

1. Tell the user the screenshot was saved to `/tmp/screenshot.jpg` (or the filename you used)
2. Report metadata: file size, response time, cache status, remaining credits
3. For comparisons, save each screenshot to a different filename

## Errors

- **401**: Invalid API key — check SNAPRENDER_API_KEY
- **429**: Rate limit or quota exceeded — wait or upgrade plan
- **Timeout**: Target site is slow — add `&delay=3000` to wait longer
- **Empty response**: URL unreachable or blocked

## Get an API Key

Free at https://app.snap-render.com/auth/signup — 50 screenshots/month, no credit card.
