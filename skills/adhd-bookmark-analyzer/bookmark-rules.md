# Bookmark Analysis Rules - Categorization & Delivery Logic

## Category Definitions

Each bookmark is analyzed and assigned to ONE primary category based on content, keywords, and author context.

### 🤖 AI & Tech Tools
**What qualifies:**
- Product launches, updates, or releases
- Tool reviews and comparisons
- API documentation or pricing changes
- "Show HN" style demos
- AI model announcements

**Keywords:**
`AI, LLM, GPT, Claude, model, API, tool, release, launch, v0, beta, demo, open source, GitHub, product`

**Example tweets:**
- "Claude 4.5 is now available with 200K context"
- "I built a tool that analyzes your X bookmarks"
- "New open-source LLM beats GPT-4 on benchmarks"

---

### 💼 Business & Strategy
**What qualifies:**
- Revenue/MRR reports and milestones
- Growth tactics and playbooks
- Pricing strategies
- Case studies (how X built Y)
- Market analysis and trends

**Keywords:**
`MRR, revenue, $, pricing, growth, strategy, case study, built, launch, customers, sales, conversion, funnel, marketing`

**Example tweets:**
- "How we went from $0 to $50K MRR in 6 months"
- "Pricing psychology: 7 tactics that actually work"
- "Case study: Replacing a $200K ops role with AI"

---

### 🔧 Development & Code
**What qualifies:**
- Code snippets and solutions
- GitHub repositories
- Technical tutorials
- Architecture discussions
- DevOps/deployment strategies

**Keywords:**
`code, repo, GitHub, Python, JavaScript, React, API, database, deploy, Docker, serverless, function, script, debug`

**Example tweets:**
- "Here's how to handle async LLM calls in Python"
- "GitHub repo for AI-powered code review"
- "Thread: Setting up local LLM inference with Docker"

---

### 📖 Threads Worth Reading
**What qualifies:**
- Long-form threads (5+ tweets)
- Storytelling and narratives
- Educational deep-dives
- "Here's everything I learned" posts

**Indicators:**
- Tweet has "🧵" or "Thread:"
- Author says "1/" or "Part 1"
- Multiple tweets in sequence from same author

**Example tweets:**
- "🧵 How I built a $1M AI business (20-tweet thread)"
- "Everything I learned shipping 10 products in 12 months"
- "Thread: The complete guide to AI safety in production"

---

### 📚 Resources
**What qualifies:**
- Books, courses, guides
- Curated lists ("Best X for Y")
- Templates and frameworks
- Reference materials

**Keywords:**
`book, course, guide, list, resources, template, framework, curated, collection, reading list`

**Example tweets:**
- "The 10 best books on AI safety"
- "Free course: Building AI agents from scratch"
- "Ultimate guide to prompt engineering"

---

### 🌟 Other
**Fallback category for:**
- Inspirational quotes
- Memes and humor (relevant to your interests)
- Random interesting facts
- Doesn't fit other categories

---

## Categorization Logic

### Step 1: Fetch Bookmark Data
For each bookmark, extract:
- Tweet text
- Author username
- Thread context (if part of a thread)
- Media (images, videos, links)
- Engagement metrics (likes, retweets)

### Step 2: Analyze Content
```python
def categorize_bookmark(tweet):
    # Check for thread indicators first
    if is_thread(tweet):
        return "Threads Worth Reading"
    
    # Check for code/technical content
    if has_code_snippet(tweet) or mentions_repo(tweet):
        return "Development & Code"
    
    # Check for business/revenue keywords
    if contains_revenue_mention(tweet) or has_business_keywords(tweet):
        return "Business & Strategy"
    
    # Check for tool/product announcements
    if is_product_launch(tweet) or has_tool_keywords(tweet):
        return "AI & Tech Tools"
    
    # Check for resources/guides
    if is_resource_list(tweet) or mentions_course(tweet):
        return "Resources"
    
    # Fallback
    return "Other"
```

### Step 3: Extract Key Insight
For each bookmark, generate a one-sentence summary:
- What's the main point?
- Why did you save this?
- What's actionable here?

**Examples:**
- "New Claude API pricing: $0.25/M output tokens (cheaper than GPT-4)"
- "Case study: AI agent replaced $200K/year ops role"
- "Python async patterns for parallel LLM calls"

### Step 4: Group and Rank
Within each category:
1. Sort by engagement (likes + retweets)
2. Prioritize threads and resources over single tweets
3. Show top 3-5 per category in summary
4. Archive the rest for search

---

## Delivery Settings

### Default Configuration
```yaml
delivery:
  channel: discord
  channelId: "your-channel-id-here"
  frequency: daily
  time: "09:00"  # 9 AM local time
  
summary:
  maxItemsPerCategory: 5
  minBookmarksToNotify: 3  # Don't send if <3 new bookmarks
  includeArchiveLink: true
  
format:
  emoji: true  # Use emoji for categories
  compact: false  # Full summaries vs. compact list
  includeMetrics: true  # Show likes/RT counts
```

### Discord Output Format
```markdown
📚 X Bookmark Summary — [Date]

You saved [N] bookmarks in the last 24 hours. Here's what stood out:

🤖 AI & Tech Tools ([count] bookmarks)
• [Insight 1]
• [Insight 2]
• [Insight 3]

💼 Business & Strategy ([count] bookmarks)
• [Insight 1]
...

[View all bookmarks →] (link to archive)
```

### Alternative: Email Format
```html
<h2>X Bookmark Summary — [Date]</h2>
<p>You saved <strong>[N]</strong> bookmarks. Here are the highlights:</p>

<h3>🤖 AI & Tech Tools</h3>
<ul>
  <li>[Insight with link]</li>
</ul>
```

---

## Processing Schedule

### Option 1: OpenClaw Cron (Recommended)
Add to your agent's cron schedule via OpenClaw:
```bash
openclaw cron add --every "1d" --at "09:00" --message "Analyze my X bookmarks from the last 24 hours and post summary to Discord"
```

Or add to your `HEARTBEAT.md` for heartbeat-based scheduling.

Processes:
- All bookmarks since last run (typically last 24h)
- Skips if no new bookmarks
- Delivers to configured channel

### Option 2: Manual Trigger
Ask your agent:
```
"Analyze my X bookmarks from this week"
"What did I bookmark about AI this month?"
```

### Option 3: Webhook (Real-time)
If you have a way to trigger on new bookmarks:
- Process immediately when you save a bookmark
- Good for instant categorization
- Requires X webhook access (not standard)

---

## Advanced Customization

### Custom Categories
Add your own categories in this file:

```yaml
custom_categories:
  - name: "Indie Hacking"
    emoji: "🚀"
    keywords: ["indie hacker", "solopreneur", "bootstrap", "side project"]
  
  - name: "Design"
    emoji: "🎨"
    keywords: ["design system", "UI", "UX", "Figma", "typography"]
```

### Smart Filters
Exclude certain types:
```yaml
filters:
  excludeRetweets: true  # Only original content
  minLikes: 10  # Ignore low-engagement tweets
  excludeAuthors: ["spammy_account"]  # Blocklist
```

### Summary Customization
```yaml
summary_options:
  groupByDate: false  # Group by category (default) vs. chronological
  showThreads: "expanded"  # Show full threads vs. first tweet only
  linkPreview: true  # Include OpenGraph previews
```

---

## Archive Structure

Bookmarks are saved locally in your workspace:
```
~/.openclaw/workspace/skills/adhd-bookmark-analyzer/bookmark-archive/
```

**Security:** All data stays on your machine. Nothing is sent to external services except your configured delivery channel (Discord/Slack webhook).

### Daily Snapshot
`2026-02-15.json`:
```json
{
  "date": "2026-02-15",
  "bookmarks": [
    {
      "id": "1234567890",
      "text": "...",
      "author": "@username",
      "category": "AI & Tech Tools",
      "insight": "One-sentence summary",
      "url": "https://twitter.com/...",
      "savedAt": "2026-02-15T14:32:00Z"
    }
  ]
}
```

### Searchable Index
`index.json`:
```json
{
  "lastUpdated": "2026-02-15T21:00:00Z",
  "totalBookmarks": 1247,
  "categories": {
    "AI & Tech Tools": 412,
    "Business & Strategy": 308,
    ...
  },
  "searchIndex": [
    {
      "id": "1234567890",
      "keywords": ["AI", "LLM", "pricing"],
      "category": "AI & Tech Tools"
    }
  ]
}
```

---

## Error Handling

### No Bookmarks Found
- Check X authentication
- Verify bookmark privacy settings (must be accessible via API)

### Rate Limiting
- Default: Process max 100 bookmarks per run
- Respect X API rate limits (15 requests/15min for bookmarks)
- If hit limit, resume on next run

### Failed Categorization
- If can't determine category, assign to "Other"
- Log for manual review
- Improve keyword matching based on patterns

---

## Tips for Effective Use

1. **Bookmark everything interesting** — Let the skill filter signal from noise
2. **Review categories weekly** — Adjust keywords if things are miscategorized
3. **Use the archive search** — Your bookmarks become a personal knowledge base
4. **Don't stress about reading everything** — The summary highlights what matters
5. **Refine over time** — Your interests will become clearer through the data

---

**Bottom line:** Stop feeling guilty about unread bookmarks. Let the skill organize them. Read what matters when you need it.
