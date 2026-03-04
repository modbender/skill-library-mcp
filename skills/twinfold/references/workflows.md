# Twinfold — Tool Schemas & Workflows

## Making API Calls

Every tool call follows this pattern:

```bash
curl -X POST https://twinfold.app/api/mcp/tools \
  -H "Authorization: Bearer $TWINFOLD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tool": "twinfold.createPost", "arguments": {"topic": "AI trends"}}'
```

Response format:
```json
{ "result": { "postId": "abc123", "content": "...", ... } }
```

Error format:
```json
{ "error": "Insufficient credits for post generation" }
```

---

## Tool Schemas

### twinfold.createPost

The most powerful tool — full content pipeline in one call.

```json
{
  "tool": "twinfold.createPost",
  "arguments": {
    "topic": "Why AI agents will replace SaaS dashboards",
    "platforms": ["linkedin", "twitter", "instagram"],
    "language": "en",
    "narrativeStyle": "first_person",
    "postLength": "medium",
    "generateImage": true,
    "imageStyle": "realistic",
    "generateFirstComment": true,
    "autoAdapt": true,
    "autoPublish": false,
    "scheduledFor": "2026-02-10T09:00:00Z"
  }
}
```

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| topic | string | *required* | Topic or idea |
| platforms | string[] | ["linkedin"] | Any of: linkedin, twitter, instagram, facebook, threads, bluesky, reddit, tiktok, pinterest, youtube |
| language | string | "en" | ISO code: en, fr, fr-CA, es, de, pt, pt-BR, it, nl, ja, ko, zh, ar |
| narrativeStyle | string | "first_person" | first_person, third_person, storytelling, educational |
| postLength | string | "medium" | short (<150w), medium (200-300w), long (400-600w) |
| generateImage | bool | false | Generate AI image |
| imageStyle | string | "realistic" | realistic, illustrated, minimalist, text_overlay, infographic |
| generateFirstComment | bool | false | Auto-generate first comment with links/hashtags |
| autoAdapt | bool | true | Adapt content per platform |
| autoPublish | bool | false | Publish immediately |
| scheduledFor | string | — | ISO datetime for scheduled publication |

Returns: `{ postId, content, platforms, platformContent, imageUrl, firstComment, language, status, scheduledFor }`

### twinfold.adaptContent

```json
{
  "tool": "twinfold.adaptContent",
  "arguments": {
    "content": "Original LinkedIn post text here...",
    "platform": "twitter",
    "language": "fr-CA"
  }
}
```

Returns: `{ content, platform, language, isThread }` — For Twitter, may return `{ thread: [...] }` if content is split into a thread.

### twinfold.generateHooks

```json
{
  "tool": "twinfold.generateHooks",
  "arguments": {
    "topic": "Remote work productivity",
    "platforms": ["linkedin"],
    "language": "en"
  }
}
```

Returns: `{ hooks: [{ hook, score, type }] }` — 4 hooks with Contrarian/Experience/Curiosity/Actionable types.

### twinfold.generateImage

```json
{
  "tool": "twinfold.generateImage",
  "arguments": {
    "postId": "abc123",
    "prompt": "Modern office with AI holographic displays",
    "style": "realistic",
    "platform": "linkedin"
  }
}
```

If `prompt` is omitted, auto-generates from post content. Image is attached to the post.

### twinfold.getPost

```json
{
  "tool": "twinfold.getPost",
  "arguments": { "postId": "abc123" }
}
```

Returns full post: content, platforms, status, mediaUrls, firstComment, hooks, scheduledFor, publishedAt, settings.

### twinfold.listPosts

```json
{
  "tool": "twinfold.listPosts",
  "arguments": { "status": "draft", "platform": "linkedin", "limit": 5 }
}
```

All params optional. Max limit: 50.

### twinfold.updatePost

```json
{
  "tool": "twinfold.updatePost",
  "arguments": {
    "postId": "abc123",
    "content": "Updated content here",
    "platforms": ["linkedin", "twitter"],
    "firstComment": "Check out our blog: https://...",
    "mediaUrls": ["https://blob.vercel-storage.com/..."],
    "scheduledFor": "2026-02-10T14:00:00Z"
  }
}
```

Cannot edit published posts. Setting `scheduledFor` auto-changes status to SCHEDULED.

### twinfold.deletePost

```json
{
  "tool": "twinfold.deletePost",
  "arguments": { "postId": "abc123" }
}
```

Cannot delete published posts.

### twinfold.publishNow

```json
{
  "tool": "twinfold.publishNow",
  "arguments": { "postId": "abc123" }
}
```

Publishes to all platforms on the post via Upload-Post API. Returns `{ published: true, platforms, uploadPostId }`.

### twinfold.schedulePost

```json
{
  "tool": "twinfold.schedulePost",
  "arguments": { "postId": "abc123", "scheduledFor": "2026-02-10T09:00:00Z" }
}
```

Time must be in the future.

### twinfold.queryTwin

```json
{
  "tool": "twinfold.queryTwin",
  "arguments": { "question": "What are my key expertise areas?" }
}
```

### twinfold.addKnowledge

```json
{
  "tool": "twinfold.addKnowledge",
  "arguments": {
    "content": "I've been building AI products for 8 years, specializing in NLP and content generation.",
    "category": "EXPERTISE_DOMAINS"
  }
}
```

Categories: EXPERTISE_DOMAINS, COMMUNICATION_STYLE, VALUES_AND_BELIEFS, INDUSTRY_KNOWLEDGE, PERSONAL_STORIES, OPINIONS_AND_TAKES, AUDIENCE_INSIGHTS

### twinfold.listAccounts

```json
{
  "tool": "twinfold.listAccounts",
  "arguments": {}
}
```

Returns: `{ accounts: [{ id, platform, accountName, language }] }`

### twinfold.getCredits

```json
{
  "tool": "twinfold.getCredits",
  "arguments": {}
}
```

Returns: `{ credits, plan, creditCosts: { POST_GENERATION: 10, ... } }`

### twinfold.getTrends

```json
{
  "tool": "twinfold.getTrends",
  "arguments": { "query": "artificial intelligence", "recency": "7d", "limit": 5 }
}
```

Recency: 1d (today), 7d (this week), 30d (this month), any.

### twinfold.runAutopilot

```json
{
  "tool": "twinfold.runAutopilot",
  "arguments": {}
}
```

Returns: `{ runId, status, topicsFound, postsGenerated, imagesGenerated, creditsUsed }`

### twinfold.getAutopilotQueue / approvePost / rejectPost

```json
{"tool": "twinfold.getAutopilotQueue", "arguments": { "limit": 10 }}
{"tool": "twinfold.approvePost", "arguments": { "postId": "abc123" }}
{"tool": "twinfold.rejectPost", "arguments": { "postId": "abc123" }}
```

### twinfold.repurposeContent

```json
{
  "tool": "twinfold.repurposeContent",
  "arguments": {
    "content": "Full blog post or transcript text here...",
    "platforms": ["linkedin", "twitter", "instagram"],
    "language": "en",
    "numberOfPosts": 1
  }
}
```

Creates actual draft posts in the database. One per platform × numberOfPosts.

### twinfold.planContent

```json
{
  "tool": "twinfold.planContent",
  "arguments": {
    "topic": "AI in healthcare",
    "days": 7,
    "platforms": ["linkedin", "twitter"],
    "language": "en"
  }
}
```

Creates draft posts for each day with unique angles. Returns the plan with post IDs.

### twinfold.createArticle / listArticles

```json
{
  "tool": "twinfold.createArticle",
  "arguments": { "topic": "The future of AI agents", "contentType": "thought_leadership", "length": "standard", "language": "en" }
}
{"tool": "twinfold.listArticles", "arguments": { "status": "draft", "limit": 10 }}
```

### twinfold.getNotifications

```json
{
  "tool": "twinfold.getNotifications",
  "arguments": { "unreadOnly": true, "type": "ACCOUNT_DISCONNECTED", "limit": 10 }
}
```

All params optional. Types: ACCOUNT_DISCONNECTED, PUBLISH_FAILED, CREDITS_LOW, CREDITS_EXHAUSTED, AUTOPILOT_RUN, PAYMENT_FAILED, ACCOUNT_RECONNECTED, GENERAL.

Returns: `{ notifications: [{ id, type, title, message, actionUrl, isRead, createdAt }], total }`.

### twinfold.markNotificationRead

```json
{
  "tool": "twinfold.markNotificationRead",
  "arguments": { "notificationId": "abc123" }
}
```

Or mark all: `{ "all": true }`. Returns: `{ success: true }`.

### twinfold.getNotificationPreferences

```json
{
  "tool": "twinfold.getNotificationPreferences",
  "arguments": {}
}
```

Returns: `{ preferences: { "account-disconnected": { email: true, inApp: true, slack: true, telegram: true }, ... } }`.

### twinfold.getBrandGuide

```json
{
  "tool": "twinfold.getBrandGuide",
  "arguments": {}
}
```

Returns: `{ brandGuide, updatedAt }` — Markdown brand guide content.

### twinfold.setBrandGuide

```json
{
  "tool": "twinfold.setBrandGuide",
  "arguments": { "brandGuide": "# My Brand\n\n## Identity\n..." }
}
```

Free — no credits charged. Returns: `{ success: true, updatedAt }`.

### twinfold.generateBrandGuide

```json
{
  "tool": "twinfold.generateBrandGuide",
  "arguments": {}
}
```

Costs 5 credits. Generates from Twin knowledge and interviews. Returns: `{ brandGuide, updatedAt }`.

### twinfold.listBrandVoices

```json
{
  "tool": "twinfold.listBrandVoices",
  "arguments": {}
}
```

Returns: `{ voices: [{ id, name, isDefault, analysis, avoidAtAllCost, structureTemplates }] }`.

### twinfold.createBrandVoice

```json
{
  "tool": "twinfold.createBrandVoice",
  "arguments": {
    "name": "Thought Leader",
    "analysis": "Tone: Authoritative yet approachable...",
    "avoidAtAllCost": "Never use jargon without explaining it",
    "structureTemplates": "Hook → Story → Insight → CTA",
    "isDefault": true
  }
}
```

### twinfold.updateBrandVoice

```json
{
  "tool": "twinfold.updateBrandVoice",
  "arguments": { "voiceId": "abc123", "name": "Updated Voice", "isDefault": false }
}
```

### twinfold.deleteBrandVoice

```json
{
  "tool": "twinfold.deleteBrandVoice",
  "arguments": { "voiceId": "abc123" }
}
```

### twinfold.generateBrandVoice

```json
{
  "tool": "twinfold.generateBrandVoice",
  "arguments": { "name": "My Voice" }
}
```

Costs 5 credits. AI analyzes Twin knowledge to produce a 12-dimension voice profile. Returns: `{ voice: { id, name, analysis, avoidAtAllCost, structureTemplates } }`.

---

## Workflow Examples

### 1. Trend-Jacking Pipeline

User says: "Find trending AI news and post about it on LinkedIn"

```
1. twinfold.getTrends { query: "artificial intelligence", recency: "1d", limit: 5 }
   → Show trends to user, let them pick one
2. twinfold.createPost { topic: <selected trend>, platforms: ["linkedin"], autoAdapt: true, generateImage: true }
   → postId
3. twinfold.getPost { postId }
   → Show preview to user
4. twinfold.publishNow { postId }
```

### 2. Multilingual Content Blast

User says: "Post about our product launch in English and French on LinkedIn and Twitter"

```
1. twinfold.createPost { topic: "Product launch announcement", platforms: ["linkedin", "twitter"], language: "en", autoAdapt: true }
   → englishPostId
2. twinfold.createPost { topic: "Product launch announcement", platforms: ["linkedin", "twitter"], language: "fr-CA", autoAdapt: true }
   → frenchPostId
3. twinfold.publishNow { postId: englishPostId }
4. twinfold.publishNow { postId: frenchPostId }
```

### 3. Weekly Content Calendar

User says: "Plan a week of LinkedIn content about leadership"

```
1. twinfold.planContent { topic: "leadership", days: 7, platforms: ["linkedin"] }
   → Returns 7 draft posts with IDs
2. Show plan to user for review
3. For each approved post:
   twinfold.schedulePost { postId, scheduledFor: "2026-02-10T09:00:00Z" }
```

### 4. Repurpose Blog Post

User says: "Turn this blog post into social media content"

```
1. twinfold.repurposeContent { content: <blog text>, platforms: ["linkedin", "twitter", "instagram", "threads"] }
   → Creates 4 drafts (1 per platform)
2. twinfold.listPosts { status: "draft", limit: 4 }
   → Show all drafts for review
3. For each: twinfold.publishNow or twinfold.schedulePost
```

### 5. Autopilot Review Workflow

User says: "Check my autopilot queue and approve the good ones"

```
1. twinfold.getAutopilotQueue { limit: 10 }
   → Show posts to user
2. For each post user likes: twinfold.approvePost { postId }
3. For each post user rejects: twinfold.rejectPost { postId }
```

### 6. Brand Setup Pipeline

User says: "Set up my brand voice for content creation"

```
1. twinfold.generateBrandGuide {}
   → AI creates brand guide from Twin interviews
2. twinfold.getBrandGuide {}
   → Show to user for review/edits
3. twinfold.generateBrandVoice { name: "Primary Voice" }
   → AI creates 12-dimension voice profile
4. twinfold.listBrandVoices {}
   → Show voice profile to user
```

Now all content created via `createPost` will use the brand guide and default voice.

### 7. Check for Issues & Alerts

User says: "Any issues with my Twinfold account?"

```
1. twinfold.getNotifications { unreadOnly: true }
   → Show unread notifications to user
2. For any ACCOUNT_DISCONNECTED:
   → "Your X account needs reconnection — go to Settings → Integrations"
3. For any CREDITS_LOW:
   → "You're running low on credits — consider upgrading"
4. twinfold.markNotificationRead { all: true }
   → Clear after user acknowledges
```

### 8. Full Autonomous Pipeline

User says: "Post something interesting about AI for me"

```
1. twinfold.listAccounts {}
   → Discover connected platforms + languages
2. twinfold.getCredits {}
   → Verify sufficient credits
3. twinfold.getTrends { query: "AI", recency: "1d" }
   → Pick highest relevance trend
4. twinfold.createPost {
     topic: <trend.title>,
     platforms: <from accounts>,
     language: <from account settings>,
     autoAdapt: true,
     generateImage: true,
     generateFirstComment: true,
     autoPublish: true
   }
   → Done! Post created, adapted, and published
```
