---
name: steel-browser
description: Control cloud browser sessions via Steel.dev for web automation and computer-use agents. Use when you need to browse the web, fill forms, click elements, take screenshots, scrape content, or build browser automation loops. Uses Playwright selectors (CSS/text/aria) instead of pixel coordinates — more reliable than e2b-desktop for pure web tasks. Supports residential proxies and CAPTCHA solving.
---

# Steel Browser Skill

Cloud browser-use via [Steel.dev](https://steel.dev) + Playwright Python SDK.
Ideal for web automation, scraping, form filling, and AI agent browser loops.

## Prerequisites

```bash
pip install steel-sdk playwright
export STEEL_API_KEY=your_key_here
```

Get your API key at https://app.steel.dev → Settings → API Keys (free: 100 browser hours).

Steel API key should be set in OpenClaw config or environment:
```bash
openclaw config set env.STEEL_API_KEY "your_key"
```

## State Management

- `start_session.sh` saves session ID to `~/.steel_state`
- All scripts auto-load it from there
- Override anytime with `export STEEL_SESSION_ID=<id>`
- Sessions persist until `release_session.sh` or timeout

## Scripts

| Script | Usage | Description |
|---|---|---|
| `start_session.sh` | `[--proxy] [--captcha] [--timeout MS]` | Create session; prints SESSION_ID + VIEWER_URL |
| `release_session.sh` | `[SESSION_ID]` | Release session |
| `list_sessions.sh` | _(none)_ | List active sessions |
| `navigate.sh` | `URL [--wait-until networkidle]` | Go to URL |
| `screenshot.sh` | `[OUTPUT.png] [--full-page]` | Take screenshot |
| `click.sh` | `SELECTOR` | Click by CSS/text/aria selector |
| `click_coords.sh` | `X Y [--right] [--double]` | Click at pixel coords (fallback) |
| `type.sh` | `SELECTOR "text"` | Fill input field |
| `press_key.sh` | `KEY` | Press key (e.g. `Enter`, `Control+a`) |
| `scroll.sh` | `AMOUNT\|--to-bottom\|--to-top\|SELECTOR` | Scroll page |
| `hover.sh` | `SELECTOR` | Hover over element |
| `select.sh` | `SELECTOR VALUE` | Select dropdown option |
| `get_content.sh` | `[--html] [SELECTOR]` | Extract page text or HTML |
| `eval_js.sh` | `"js expression"` | Execute JavaScript, print result |
| `wait_for.sh` | `SELECTOR [TIMEOUT_MS]` | Wait for element to appear |
| `get_url.sh` | _(none)_ | Print current URL and page title |

## Selector Examples

Steel uses Playwright selectors — much more powerful than pixel coords:

```bash
# By CSS
click.sh "#submit-button"
click.sh ".nav-link:first-child"

# By text content
click.sh "text=Sign in"
click.sh "button:has-text('Continue')"

# By aria label
click.sh "[aria-label='Search']"
click.sh "[placeholder='Email address']"

# XPath
click.sh "xpath=//button[@type='submit']"
```

## Browser-Use Agent Loop Pattern

```bash
SCRIPTS="skills/steel-browser/scripts"

# 1. Start session (add --proxy --captcha for tough sites)
source <($SCRIPTS/start_session.sh)
echo "Session: $SESSION_ID"
echo "Watch at: $VIEWER_URL"

# 2. Navigate
$SCRIPTS/navigate.sh "https://example.com"

# 3. Agent loop
while true; do
  $SCRIPTS/screenshot.sh /tmp/screen.png
  
  # Get page text for LLM context
  CONTENT=$($SCRIPTS/get_content.sh)
  
  # LLM decides action...
  ACTION=$(echo "$CONTENT" | llm_decide /tmp/screen.png)
  
  case "$ACTION_TYPE" in
    click)    $SCRIPTS/click.sh "$SELECTOR" ;;
    type)     $SCRIPTS/type.sh "$SELECTOR" "$TEXT" ;;
    navigate) $SCRIPTS/navigate.sh "$URL" ;;
    done)     break ;;
  esac
done

# 4. Release
$SCRIPTS/release_session.sh
```

## vs E2B Desktop

| Feature | Steel Browser | E2B Desktop |
|---|---|---|
| Selectors | Playwright CSS/text/aria ✅ | Pixel coords only |
| Proxy support | ✅ Residential proxies | ❌ |
| CAPTCHA solving | ✅ Built-in | ❌ |
| Non-browser tasks | ❌ | ✅ Desktop apps, terminal |
| Session viewer | ✅ Live URL | ✅ VNC stream |

Use **Steel** for web automation. Use **E2B Desktop** for desktop apps / full OS control.
