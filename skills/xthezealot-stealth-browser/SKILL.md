# Stealth Browser

Use `/stealth-browser` to access websites with advanced bot protection.

## Commands

- `/stealth-browser open <url>` - Fetch page HTML
- `/stealth-browser screenshot <url>` - Take full-page screenshot  
- `/stealth-browser pdf <url>` - Save page as PDF
- `/stealth-browser parallel <url1> <url2> [url3...]` - Fetch multiple URLs in parallel

## Examples

```
/stealth-browser open https://www.bazaraki.com/adv/6203561_2-bedroom-detached-house-for-sale/
/stealth-browser screenshot https://example.com
/stealth-browser pdf https://example.com
/stealth-browser parallel https://site1.com https://site2.com https://site3.com
```

## Parallel Browsing

The `parallel` command fetches multiple URLs simultaneously using isolated browser contexts:
- Each URL gets its own isolated context (cookies, storage, etc.)
- Much faster than sequential fetching
- Results returned as formatted JSON

## How It Works

Uses Playwright Extra with Stealth Plugin to mask automation signatures:
- Removes `navigator.webdriver` flag
- Spoofs Chrome plugins and permissions
- Fakes WebGL/Canvas fingerprints
- Mimics real user behavior

Bypasses Cloudflare, reCAPTCHA, and most bot detection.
