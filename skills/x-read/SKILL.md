---
name: x-read
description: Render and summarize a public X (Twitter) link when you need to read the tweet/article content without logging in.
---

# X-Read Skill

## When to use this skill
Use `x-read` whenever you need to capture the text, media links, and basic metadata from a public X/Twitter permalink without using the API, creating an account, or burning Brave search credits. It works best for thread permalink URLs (`https://x.com/<user>/status/<id>`) and articles posted on X that surface their content on the same page.

## Inputs
- `url` (required): The exact permalink you want to render. Include the full `https://x.com/...` path so the Puppeteer browser can navigate directly.

## What happens when you run it
1. Puppeteer launches a sandboxed Chromium instance with a realistic user-agent and loads the URL.
2. The script waits for `article[data-testid="tweet"]` elements, captures the main thread (tweet + up to three replies), and extracts any linked card or media attachments.
3. Media is reprinted as `![](...)` markdown with `ALT` text when available, and the main article body is appended beneath the primary tweet.
4. The output is a short markdown summary listing the thread author, timestamp, text, links, and media so the Telegram chat stays readable.

## Output format
```
## Tweet Thread Summary
Source: <url>

### **MAIN TWEET** by Display Name (@handle)
*2026-02-21T18:24:00Z*
Tweet text …

**Linked Article:** [Title](card URL)
**Media:**
- ![](media1)
- ![](media2)
---
```
Replied tweets follow the same pattern with the `Reply` heading. Media URLs retain the `name=large` parameter for better quality.

## Limitations and troubleshooting
- The skill only reads publicly available tweets. If X blocks the navigation with a login wall, you will see an error that logging in is required.
- Long-form articles sometimes use `article.content`; the script appends that text to the main tweet so you still get the full written piece.
- Because the skill uses a browser, it may take a few extra seconds compared to an API call—expect 5–10 seconds per URL.
- For best results, keep the thread URLs focused and don’t try to feed a feed of multiple unrelated URLs at once; run the tool per link.

## Testing and safety
- The skill is read-only: it never posts, likes, DM’s, or authenticates to X.
- Review the `index.js` script if X changes its DOM selectors (it relies on `data-testid` attributes such as `tweet`, `tweetText`, `User-Name`, and `card.wrapper`).
- Run the skill manually with `openclaw use x-read read_tweet --url <link>` before publishing to confirm the output is what you expect.
