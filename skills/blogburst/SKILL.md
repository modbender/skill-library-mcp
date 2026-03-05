---
name: BlogBurst - AI Social Media Agent
description: Autonomous AI marketing agent. Chat naturally to generate content, manage auto-pilot, check analytics, and post to 9 platforms (Twitter/X, LinkedIn, Bluesky, Telegram, Discord, Reddit, TikTok, YouTube, Threads). One command to automate your entire social media.
homepage: https://blogburst.ai
metadata:
  {"openclaw": {"emoji": "🚀", "requires": {"env": ["BLOGBURST_API_KEY"]}, "primaryEnv": "BLOGBURST_API_KEY"}}
---

# BlogBurst - AI Social Media Marketing Agent

Your autonomous AI marketing agent. Talk naturally — it generates content, publishes to 9 platforms, runs auto-pilot daily posting, tracks analytics, and learns what works.

**One message to do anything:**
- "Post about my product launch on Twitter and LinkedIn"
- "Turn on auto-pilot, 3 posts per day"
- "How did my posts perform this week?"
- "Repurpose this article: https://myblog.com/post"

## Setup

1. Sign up free at [blogburst.ai](https://blogburst.ai)
2. Dashboard > Settings > API Keys > Create key
3. Set environment variable:
```bash
export BLOGBURST_API_KEY="your-key"
```

All requests use: `X-API-Key: $BLOGBURST_API_KEY`
Base URL: `https://api.blogburst.ai/api/v1`

---

## API 1: Agent Chat (Recommended — does everything)

Chat with your AI marketing agent. It can generate content, check analytics, manage auto-pilot, view trending topics, and more — all through natural conversation. The agent has tools and will execute actions automatically.

**Endpoint**: `POST /assistant/agent-chat-v2`

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "Generate a Twitter post about my product"}
  ],
  "language": "en"
}
```

Multi-turn conversation — send the full message history each time:
```json
{
  "messages": [
    {"role": "user", "content": "Generate a Twitter post about my product"},
    {"role": "assistant", "content": "Here's your Twitter post..."},
    {"role": "user", "content": "Now make one for LinkedIn too"}
  ],
  "language": "en"
}
```

**Response**:
```json
{
  "reply": "I've generated a Twitter post for you. Ready to copy and post!",
  "data_referenced": ["marketing_strategy", "analytics_7d"],
  "agent_name": "Nova",
  "actions_taken": [
    {
      "tool": "generate_content",
      "result": {
        "success": true,
        "data": {
          "platform": "twitter",
          "content": "Week 3 building BlogBurst. 15 followers, 40 posts published. Best post got 5 likes on Bluesky. Small numbers, real progress.\n\nThe AI agent now picks topics based on what actually performed well last week. No more guessing.",
          "image_urls": ["https://..."],
          "copy_only": true
        }
      }
    }
  ]
}
```

**What users can say** (the agent understands natural language):
- "Generate a post for Twitter/Bluesky/LinkedIn/all platforms"
- "What's trending in my space?"
- "How are my posts doing this week?"
- "Turn on auto-pilot" / "Pause auto-pilot"
- "What did you post today?"
- "What platforms do I have connected?"
- "Show me my recent activity"

**When to use**: This is the PRIMARY API. Use it for any user request about social media content, analytics, automation, or marketing. It handles everything through conversation.

---

## API 2: Generate Platform Content (Quick one-shot)

Generate optimized content for multiple platforms at once. Use this for fast, direct generation without conversation.

**Endpoint**: `POST /blog/platforms`

**Request**:
```json
{
  "topic": "5 lessons from building my SaaS in public",
  "platforms": ["twitter", "linkedin", "bluesky"],
  "tone": "casual",
  "language": "en"
}
```

**Parameters**:
- `topic` (required): The title or topic (5-500 chars)
- `platforms` (required): Array from: twitter, linkedin, reddit, bluesky, threads, telegram, discord, tiktok, youtube
- `tone`: professional | casual | witty | educational | inspirational (default: professional)
- `language`: Language code (default: en)

**Response**:
```json
{
  "success": true,
  "topic": "5 lessons from building my SaaS in public",
  "twitter": {
    "thread": [
      "1/ 5 months building a SaaS in public. Here are the lessons nobody talks about...",
      "2/ Lesson 1: Your first 10 users teach you more than 10,000 pageviews.",
      "3/ Lesson 2: Ship weekly. Perfection is the enemy of traction."
    ]
  },
  "linkedin": {
    "post": "I've been building my SaaS in public for 5 months...",
    "hashtags": ["#BuildInPublic", "#SaaS", "#IndieHacker"]
  },
  "bluesky": {
    "posts": ["5 months of building in public. The biggest lesson: your first users don't care about features. They care that you listen."]
  }
}
```

**When to use**: When user wants quick multi-platform content from a topic without ongoing conversation.

---

## API 3: Repurpose Existing Content

Transform a blog post or article (by URL or text) into platform-optimized posts.

**Endpoint**: `POST /repurpose`

**Request**:
```json
{
  "content": "https://myblog.com/my-article",
  "platforms": ["twitter", "linkedin", "bluesky"],
  "tone": "casual",
  "language": "en"
}
```

**Parameters**:
- `content` (required): A URL to an article, or the full text (min 50 chars)
- `platforms` (required): Array from: twitter, linkedin, reddit, bluesky, threads, telegram, discord, tiktok, youtube
- `tone`: professional | casual | witty | educational | inspirational
- `language`: Language code (default: en)

**Response**: Same format as API 2.

**When to use**: When user provides a URL or pastes existing content and wants it adapted for social platforms.

---

## API 4: Auto-Pilot Management

Check and configure the autonomous posting agent.

**Get status**: `GET /assistant/auto-pilot`

**Response**:
```json
{
  "enabled": true,
  "platforms": ["bluesky", "telegram", "discord", "twitter"],
  "posts_per_day": 4,
  "timezone": "America/New_York",
  "last_daily_run": "2026-03-02T08:49:28Z",
  "reactions_enabled": true
}
```

**Configure**: `POST /assistant/auto-pilot`

```json
{
  "enabled": true,
  "posts_per_day": 3,
  "platforms": ["twitter", "bluesky", "telegram"],
  "timezone": "America/New_York"
}
```

**Run immediately**: `POST /assistant/auto-pilot/run-now`

**When to use**: When user wants to start/stop auto-pilot, change posting frequency, or check automation status.

---

## API 5: Trending Topics

Get real-time trending topics from Reddit, HackerNews, Google Trends, and Product Hunt. Updated every 4 hours.

**Endpoint**: `GET /assistant/trending-topics?limit=10`

**Response**:
```json
{
  "topics": [
    {"keyword": "AI agents replacing SaaS", "source": "hackernews", "score": 92},
    {"keyword": "Claude Code launch", "source": "reddit", "score": 87},
    {"keyword": "Open source AI tools", "source": "google_trends", "score": 78}
  ],
  "total": 96,
  "sources": ["reddit", "hackernews", "google_trends", "producthunt"]
}
```

**When to use**: When user asks about trends, hot topics, or what's popular to write about.

---

## API 6: Brainstorm Titles

Chat with AI to develop compelling titles.

**Endpoint**: `POST /chat/title`

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "I want to write about AI agents"}
  ],
  "language": "en"
}
```

**Response**:
```json
{
  "success": true,
  "reply": "Great topic! Here are some angles...",
  "suggested_titles": [
    "I Replaced My Marketing Team with an AI Agent",
    "Why AI Agents Are the New SaaS",
    "Building an AI Agent That Posts for Me While I Sleep"
  ]
}
```

---

## API 7: Generate Blog Post

Generate a full blog article from a topic.

**Endpoint**: `POST /blog/generate`

**Request**:
```json
{
  "topic": "I Replaced My Marketing Team with an AI Agent",
  "tone": "casual",
  "language": "en",
  "length": "medium"
}
```

**Parameters**:
- `topic` (required): Title or topic (5-500 chars)
- `tone`: professional | casual | witty | educational | inspirational
- `language`: Language code (default: en)
- `length`: short (500-800 words) | medium (1000-1500) | long (2000-3000)

**Response**:
```json
{
  "success": true,
  "title": "I Replaced My Marketing Team with an AI Agent",
  "content": "Full markdown blog post...",
  "summary": "A concise summary...",
  "keywords": ["AI agent", "marketing automation", "SaaS"]
}
```

---

## Recommended Workflows

### Quick content generation
User says: "Create posts about X for Twitter and LinkedIn"
→ Call **API 2** (`/blog/platforms`)

### Conversational (best experience)
User says: "Help me with my social media" or anything complex
→ Call **API 1** (`/assistant/agent-chat-v2`) — the agent handles everything

### Repurpose existing content
User shares a URL or pastes text
→ Call **API 3** (`/repurpose`)

### Full content pipeline
1. Brainstorm with **API 6** (`/chat/title`)
2. Write blog with **API 7** (`/blog/generate`)
3. Distribute with **API 2** (`/blog/platforms`)

### Automation
User says: "Automate my posting" or "Turn on auto-pilot"
→ Call **API 4** (`/assistant/auto-pilot`)

## Supported Platforms

| Platform | ID | Auto-Publish | Content Style |
|----------|-----|:---:|---------------|
| Twitter/X | twitter | Manual | Threads with hooks (280 chars/tweet) |
| LinkedIn | linkedin | Coming soon | Professional insights + hashtags |
| Bluesky | bluesky | Yes | Short authentic posts (300 chars) |
| Telegram | telegram | Yes | Rich formatted broadcasts |
| Discord | discord | Yes | Community-friendly announcements |
| Reddit | reddit | Manual | Discussion posts + subreddit suggestions |
| TikTok | tiktok | Manual | Hook + script + caption + hashtags |
| YouTube | youtube | Manual | Title + description + script + tags |
| Threads | threads | Coming soon | Conversational posts |

## Links

- Website: https://blogburst.ai
- API Docs: https://api.blogburst.ai/docs
- GitHub: https://github.com/shensi8312/blogburst-openclaw-skill
