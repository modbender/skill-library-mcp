# X Bookmark Research Protocol

When asked to "check bookmarks", "sync bookmarks", or similar:

## Step 1 — Sync
```bash
python3 scripts/x-bookmarks-sync.py --detect-new
```

## Step 2 — Check for new
Read `research/x-bookmarks-new.json`. If empty (`[]`), reply "No new bookmarks." and stop.

## Step 3 — Analyze each new bookmark

For each bookmark in the trigger file:

1. **Fetch linked content** — for any external URLs in the tweet (non-X links), use `web_fetch` to get the article/page content.

2. **Quick web search** — one search per bookmark for additional context on the author, tool, or claim.

3. **Write a verdict:**
   - **ARCHIVE** — interesting but no action needed
   - **READ_DEEPER** — worth your time to dig into
   - **ACT_ON** — needs action (tag what kind)
   - **SHARE:person** — relevant to someone in your network
   - **BUILD:project** — connects to an active project

4. **Save brief** to `research/vetted/YYYY-MM-DD-{slug}.md` with YAML frontmatter:
   ```yaml
   ---
   source_url: [tweet URL]
   author: [@handle]
   verdict: [verdict]
   tags: [comma-separated]
   researched: [YYYY-MM-DD]
   ---
   ```

5. **Post to your research channel** — one message per bookmark, tight format:
   - **@author** — one-line summary
   - Key finding (1-2 sentences)
   - Linked resources found
   - Verdict: **VERDICT** — why

## Rules
- Don't try to web_fetch x.com URLs directly — X blocks scrapers. Use the API script.
- Don't spawn sub-agents. Handle all bookmarks yourself in sequence.
- If a bookmark links to a tool or product, search for "[tool name] review" or "[tool name] github".
- Be honest. Most bookmarks are ARCHIVE. Don't inflate verdicts.
- Run `qmd update` once at the end, not per bookmark.

## Cron Setup (optional)
To sync automatically every day at 10 AM, tell your agent:
> "Set up a daily cron at 10 AM to run `python3 scripts/x-bookmarks-sync.py --detect-new` and analyze any new bookmarks."
