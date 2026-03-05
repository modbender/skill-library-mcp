---
slug: reddit-researcher
display_name: Reddit Researcher
version: 1.0.0
tags: [latest]
credentials:
  - name: reddit_oauth
    type: oauth2
    required: false
    description: Reddit OAuth credentials for authenticated API access with higher rate limits. If not provided, falls back to anonymous access with limited rate limits.
env_vars:
  - name: REDDIT_CLIENT_ID
    required: false
    description: Reddit app Client ID from https://www.reddit.com/prefs/apps
  - name: REDDIT_CLIENT_SECRET
    required: false
    description: Reddit app Client Secret from https://www.reddit.com/prefs/apps
  - name: REDDIT_USER_AGENT
    required: false
    description: Custom user agent string (e.g., "ResearchBot/1.0 by u/username")
tools:
  - curl
  - jq
---

# Reddit Researcher

## Description

Research and analyze Reddit discussions by searching posts, reading comments, and summarizing community sentiment on any topic. Useful for gathering user opinions, troubleshooting insights, market research, and trend analysis.

## Use Cases

- **Product Research**: Find user complaints, feature requests, and feedback about products or services
- **Troubleshooting**: Discover common issues and solutions users are discussing
- **Market Analysis**: Understand community sentiment about brands, technologies, or trends
- **Competitive Intelligence**: See what users say about competitors
- **Content Research**: Gather information and perspectives on specific topics

## Setup

### Creating a Reddit Application

To access the Reddit API with higher rate limits, you need to create a Reddit app:

1. **Go to Reddit Apps Page**
   - Visit: https://www.reddit.com/prefs/apps
   - Log in to your Reddit account

2. **Create a New App**
   - Scroll to the bottom and click "Create App" or "Create Another App"
   - Select **"script"** as the app type (for personal/research use)

3. **Fill in App Details**
   - **Name**: Your app name (e.g., "ResearchBot")
   - **Description**: Brief description of what the app does
   - **About URL**: Your website or GitHub profile (optional)
   - **Redirect URI**: Use `http://localhost:8080` (required but not used for script apps)

4. **Get Your Credentials**
   After creating the app, you'll see:
   
   - **Client ID**: The string under the app name (e.g., `abc123def456ghi`)
   - **Client Secret**: Click "edit" to reveal the secret (e.g., `jkl789mno012pqr`)

5. **Configure Environment**
   ```bash
   export REDDIT_CLIENT_ID="your_client_id_here"
   export REDDIT_CLIENT_SECRET="your_client_secret_here"
   export REDDIT_USER_AGENT="ResearchBot/1.0 by u/yourusername"
   ```

### Environment Variables

For higher rate limits and authenticated access:

- `REDDIT_CLIENT_ID` - From Reddit app registration
- `REDDIT_CLIENT_SECRET` - From Reddit app registration
- `REDDIT_USER_AGENT` - Custom user agent string (e.g., "MyResearchBot/1.0 by u/username")

### Security Best Practices

**Least-Privilege Credentials:**
- Create a dedicated Reddit account for API access (do not use your personal/main account)
- Use the "script" app type which has minimal permissions (read-only by default)
- Never commit credentials to version control
- Rotate credentials periodically
- For production use, consider using a secrets manager instead of environment variables

**Rate Limiting:**
- Anonymous access is limited to ~30 requests/minute
- OAuth access increases to 100 requests/minute
- Implement request throttling to avoid being rate-limited or banned

### Authentication

**Anonymous Access (Limited)**:
- Base URL: `https://www.reddit.com`
- Rate limit: ~30 requests per minute
- Add `.json` to any Reddit URL to get JSON data

**OAuth Access (Recommended)**:
```bash
# Get access token
curl -X POST https://www.reddit.com/api/v1/access_token \
  -H "User-Agent: $REDDIT_USER_AGENT" \
  --basic -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -d "grant_type=client_credentials"
```

Use the access token:
```
Authorization: Bearer $ACCESS_TOKEN
User-Agent: $REDDIT_USER_AGENT
```

## API Reference

### Search Posts

Search for posts across Reddit or within specific subreddits.

#### Search All Reddit

```bash
curl "https://www.reddit.com/search.json?q=OpenCore+problems&sort=new&time=week&limit=25" \
  -H "User-Agent: RedditResearchBot/1.0"
```

#### Search Specific Subreddit

```bash
curl "https://www.reddit.com/r/hackintosh/search.json?q=OpenCore&restrict_sr=1&sort=new&time=week" \
  -H "User-Agent: RedditResearchBot/1.0"
```

**Query Parameters:**
- `q` - Search query (required)
- `sort` - Sort by: `relevance`, `new`, `hot`, `top`, `comments`
- `time` - Time filter: `hour`, `day`, `week`, `month`, `year`, `all`
- `limit` - Number of results (1-100, default 25)
- `after` - Pagination token for next page
- `restrict_sr=1` - Restrict to subreddit (when searching within subreddit)

### Get Subreddit Posts

#### Hot Posts

```bash
curl "https://www.reddit.com/r/hackintosh/hot.json?limit=25" \
  -H "User-Agent: RedditResearchBot/1.0"
```

#### New Posts

```bash
curl "https://www.reddit.com/r/hackintosh/new.json?limit=25" \
  -H "User-Agent: RedditResearchBot/1.0"
```

#### Top Posts (by time period)

```bash
curl "https://www.reddit.com/r/hackintosh/top.json?t=week&limit=25" \
  -H "User-Agent: RedditResearchBot/1.0"
```

**Time periods:** `hour`, `day`, `week`, `month`, `year`, `all`

### Get Post Details and Comments

```bash
curl "https://www.reddit.com/r/hackintosh/comments/ABC123/post_title.json" \
  -H "User-Agent: RedditResearchBot/1.0"
```

**Response Structure:**
- `[0]` - Post data (listing with one post)
- `[1]` - Comments data (listing with comment tree)

### Get User Profile and Posts

```bash
curl "https://www.reddit.com/user/username/submitted.json" \
  -H "User-Agent: RedditResearchBot/1.0"
```

## Response Structure

### Post Object

```json
{
  "data": {
    "children": [{
      "data": {
        "id": "post_id",
        "title": "Post Title",
        "selftext": "Post body text",
        "author": "username",
        "subreddit": "subreddit_name",
        "score": 123,
        "num_comments": 45,
        "created_utc": 1704067200,
        "permalink": "/r/subreddit/comments/id/title/",
        "url": "https://external-link.com" // or "self" post
      }
    }]
  }
}
```

### Comment Object

```json
{
  "data": {
    "body": "Comment text",
    "author": "username",
    "score": 10,
    "created_utc": 1704067200,
    "replies": {
      "data": {
        "children": [...] // Nested replies
      }
    }
  }
}
```

## Research Workflow

### Step 1: Define Research Query

Identify:
- Search terms and keywords
- Relevant subreddits
- Time period of interest
- Sort preference (new for recent, top for popular)

### Step 2: Search and Filter Posts

```bash
# Example: Find recent OpenCore problems
curl "https://www.reddit.com/r/hackintosh/search.json?q=OpenCore+issue+OR+problem+OR+error&sort=new&time=week&limit=50" \
  -H "User-Agent: RedditResearchBot/1.0" | jq '.data.children[].data | {title, score, num_comments, permalink, created_utc}'
```

### Step 3: Fetch Top Post Comments

```bash
# Get full post with comments
curl "https://www.reddit.com/r/hackintosh/comments/POST_ID.json" \
  -H "User-Agent: RedditResearchBot/1.0"
```

### Step 4: Analyze and Summarize

Extract:
- **Common Issues**: Recurring problems mentioned
- **Solutions**: Fixes and workarounds suggested
- **Sentiment**: Overall community attitude
- **Key Insights**: Notable observations or patterns
- **Specific Examples**: Direct quotes or user experiences

## Example Research Queries

### Product Issues Research

```bash
# Find problems with a product in the last month
curl "https://www.reddit.com/search.json?q=ProductName+issue+OR+bug+OR+problem&sort=new&time=month&limit=50" \
  -H "User-Agent: RedditResearchBot/1.0"
```

### Feature Requests Analysis

```bash
# Find feature requests in a specific subreddit
curl "https://www.reddit.com/r/apple/search.json?q=feature+request+OR+wish+OR+please+add&sort=top&time=month&restrict_sr=1" \
  -H "User-Agent: RedditResearchBot/1.0"
```

### Troubleshooting Research

```bash
# Find solutions to common problems
curl "https://www.reddit.com/r/techsupport/search.json?q=WiFi+disconnecting+fixed+OR+solved&sort=relevance&time=week" \
  -H "User-Agent: RedditResearchBot/1.0"
```

### Competitive Analysis

```bash
# Compare two products
curl "https://www.reddit.com/search.json?q=ProductA+vs+ProductB&sort=top&time=month&limit=25" \
  -H "User-Agent: RedditResearchBot/1.0"
```

## Advanced Search Operators

Reddit supports search operators:

- `title:keyword` - Search in titles only
- `selftext:keyword` - Search in post body only
- `author:username` - Posts by specific user
- `subreddit:name` - Posts in specific subreddit
- `site:example.com` - Posts linking to specific domain
- `url:text` - Posts with URL containing text
- `nsfw:no` - Exclude NSFW content

Example:
```bash
curl "https://www.reddit.com/search.json?q=title:OpenCore+selftext:problem&sort=new&time=week" \
  -H "User-Agent: RedditResearchBot/1.0"
```

## Rate Limiting

- **Anonymous**: ~30 requests per minute
- **OAuth**: 100 requests per minute
- Response headers include rate limit info (when using OAuth)

**Best Practices:**
- Add delays between requests (1-2 seconds)
- Use OAuth for better limits
- Respect 429 responses and back off
- Cache results when possible

## Data Processing with jq

### Extract Post Summaries

```bash
curl -s "https://www.reddit.com/r/hackintosh/new.json?limit=10" \
  -H "User-Agent: RedditResearchBot/1.0" | \
  jq '.data.children[].data | {title, score, num_comments, url: "https://reddit.com" + .permalink}'
```

### Extract Comment Threads

```bash
curl -s "https://www.reddit.com/r/hackintosh/comments/POST_ID.json" \
  -H "User-Agent: RedditResearchBot/1.0" | \
  jq '.[1].data.children[].data | {author, body, score, replies: (.replies.data.children | length)}'
```

### Filter by Score

```bash
curl -s "https://www.reddit.com/r/hackintosh/hot.json?limit=100" \
  -H "User-Agent: RedditResearchBot/1.0" | \
  jq '.data.children[].data | select(.score > 50) | {title, score, num_comments}'
```

## Research Output Format

When summarizing research, structure findings as:

```markdown
## Research Summary: [Topic]

### Overview
Brief description of what was researched and scope.

### Key Findings
1. **Finding 1**: Description with supporting evidence
2. **Finding 2**: Description with supporting evidence
3. **Finding 3**: Description with supporting evidence

### Common Issues/Sentiments
- **Issue 1**: Frequency and context
- **Issue 2**: Frequency and context

### Notable Discussions
1. **[Post Title](link)** - r/subreddit, X comments
   - Key insight or quote
   
2. **[Post Title](link)** - r/subreddit, X comments
   - Key insight or quote

### Recommendations/Conclusions
Based on the research, actionable insights or conclusions.

### Data Points
- Posts analyzed: X
- Comments analyzed: X
- Time period: [dates]
- Primary subreddits: r/x, r/y
```

## Changelog

### v1.0.0

- Initial release
- Search posts across Reddit and subreddits
- Read post details and comment threads
- Analyze and summarize community discussions
- Support for anonymous and OAuth authentication
- Advanced search operators and filtering
