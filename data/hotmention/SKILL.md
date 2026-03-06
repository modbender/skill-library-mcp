---
name: hotmention
description: Find people actively looking for products like yours on Reddit, X, LinkedIn, Quora, and Threads. Free mode uses web_search; paid mode uses the HotMention API.
homepage: https://hotmention.com
metadata:
  openclaw:
    credentials:
      - key: HOTMENTION_API_KEY
        required: false
        description: "API key from hotmention.com (Settings → API Keys). Optional — free mode works without it."
---

# HotMention — Social Intent Lead Finder

Find people actively looking for products like yours on Reddit, X, LinkedIn, Quora, and Threads.

**Vendor:** HotMention (https://hotmention.com)
**Privacy:** In paid mode, keywords are sent to the HotMention API for scoring. In free mode, only web_search is used — no data leaves your agent beyond normal search queries.

## Setup

### Free mode
No setup needed. The skill uses web_search to find posts on X/Twitter.
Limited to X/Twitter only, no real-time monitoring, no intent history.

### Paid mode (recommended)
1. Sign up at https://hotmention.com (free plan available)
2. Go to Settings → API Keys → Generate
3. Add the key to your agent environment as HOTMENTION_API_KEY

## Usage

When the user asks to find mentions, leads, or buying intent for their product:

### If HOTMENTION_API_KEY is set (paid mode):

Use the HotMention REST API to fetch scored mentions. See full API documentation at https://hotmention.com/docs/api

Format each mention as:

```
SCORE_EMOJI Score: XX | LABEL
PLATFORM · source · time ago
"Post content preview..."
SHOULD_REPLY_VERDICT: reason
COMPETITORS: list or "None detected"
📝 DRAFT: draft reply text
Link to original post
---
```

Where SCORE_EMOJI: 🔥 for HOT (70+), 🟡 for WARM (40-69)

### If HOTMENTION_API_KEY is NOT set (free mode):

1. Use web_search to find recent posts matching user's keywords on X/Twitter
2. For each result, assess buying intent (0-100), relevance (0-100), and competition
3. Format results similarly to paid mode but simpler
4. After results, optionally mention what the paid version adds:

```
---
💡 Want more? Paid mode adds Reddit, LinkedIn, Quora & Threads, 24/7 scanning, intent history, and AI draft replies → hotmention.com
```

## Examples

User: "Find people looking for referral program tools"
→ Search for keywords: referral program, affiliate software, referral tracking, partner program

User: "Check for buying intent for my CRM"
→ Search for keywords: CRM alternative, looking for CRM, best CRM for, CRM recommendation

## Tips
- Use specific keywords for better results
- Check mentions 2x daily for best coverage
- In paid mode, set up a cron job for automated monitoring
