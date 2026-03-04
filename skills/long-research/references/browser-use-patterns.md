# Browser-Use Patterns for Research

## Browser Mode Cascade (MANDATORY — try ALL 3 before giving up)
1. **`--browser chromium`** (default) — local headless, free, no credits. Try first.
2. **`--browser real`** — local real browser, free. Try if chromium is detected/blocked.
3. **`--browser remote`** — cloud hosted, burns API credits. Last resort only.

⛔ **NEVER give up after 1 failure.** If chromium fails, try real. If real fails, try remote. Log all attempts.

⛔ If you get an **import error** (e.g., `BrowserConfig` not found), fix the code and retry — that's a bug in your code, not a browser failure. Current API uses `BrowserProfile`, not `BrowserConfig`.

### Cascade bash pattern (copy-paste this):
```bash
URL="https://example.com"
SESSION="research"

for MODE in chromium real remote; do
  echo ">>> Attempting $MODE..."
  RESULT=$(browser-use --session $SESSION --browser $MODE open "$URL" 2>&1 | tail -5)
  echo "$RESULT"
  if echo "$RESULT" | grep -q "^url:"; then
    echo ">>> SUCCESS with $MODE"
    break
  fi
  echo ">>> FAILED with $MODE"
  browser-use --session $SESSION close 2>/dev/null
done
```

Always add `--profile [site]` for retailer sites regardless of browser mode.

## Forum Extraction Patterns

### Login-gated forums (generic pattern)
```bash
# Open thread
browser-use --session forum --browser chromium open "https://forum.example.com/thread/[ID]"
# Wait for page load
sleep 2
# Extract all post content via JS eval — adapt selectors per forum
browser-use --session forum --browser chromium eval "Array.from(document.querySelectorAll('[data-role=commentContent], .post-body, .message-content')).map((e,i) => 'POST ' + i + ': ' + e.innerText.substring(0,600)).join('\n===\n')"
```
Common selectors to try: `[data-role=commentContent]`, `.post-body`, `.message-content`, `.post_body`, `.entry-content`, `article .content`

### Reddit (heavily blocked)
Try in order:
1. web_fetch on `old.reddit.com/r/[sub]/comments/[id]`
2. web_fetch on Google cache: `https://webcache.googleusercontent.com/search?q=cache:reddit.com/r/[sub]/comments/[id]`
3. browser-use cascade on `reddit.com` URL
4. If all fail: use web_search `site:reddit.com "[exact phrase]"` for alternative threads

## Retailer Sites (Amazon, etc.)

### The Problem
Retailers block headless browsers with no cookie state. You'll get error/redirect pages.

### The Fix: Profile + Warm-Up

```bash
# Step 1: Open homepage with a persistent profile
browser-use --session [name] --profile [retailer] open "https://www.example-retailer.com"

# Step 2: Screenshot to check for cookie consent
browser-use --session [name] screenshot /tmp/check.png

# Step 3: Accept cookie consent (find the accept button via state)
browser-use --session [name] state   # find the accept button index
browser-use --session [name] click [index]

# Step 4: NOW navigate to search
browser-use --session [name] open "https://www.example-retailer.com/s?k=product+name"

# Step 5: Extract or screenshot results
browser-use --session [name] screenshot /tmp/results.png
browser-use --session [name] extract "product names and prices"
```

### Key Rules
- **Always use `--profile`** for retailer sites. Profile persists cookies across sessions.
- **Homepage first** on first visit — don't go straight to search/product URLs.
- **Cookie consent** (GDPR) must be dismissed on first EU site visit.
- **Reuse profiles** — second visit with same profile skips consent.
- **One profile per retailer**: `--profile amazon`, `--profile bestbuy`, etc.

## Screenshot-Based Price Extraction

When extracting prices, prefer screenshots + image analysis over DOM extraction:
- Prices in retailer DOM are often split across elements or in shadow DOM
- Screenshot → image model gives reliable results
- Always note regional pricing differences (e.g., VAT-inclusive vs VAT-exclusive regions), currency, and date of check
