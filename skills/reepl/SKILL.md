---
name: LinkedIn Content Creation Skill by Reepl
description: Manage your LinkedIn presence with Reepl -- create drafts, publish and schedule posts, manage contacts and collections, generate AI images, and maintain your voice profile. Requires a Reepl account (reepl.io).
homepage: https://reepl.io
metadata: {"openclaw":{"requires":{"env":["REEPL_MCP_KEY"]},"primaryEnv":"REEPL_MCP_KEY"}}
---

# LinkedIn Content Creation via Reepl

Full LinkedIn content management through Reepl's MCP integration. Write posts in your authentic voice, schedule content, manage drafts, generate AI images, browse your saved content library, and maintain contacts -- all from your AI assistant.

## Prerequisites

1. **Reepl account** -- sign up at [reepl.io](https://reepl.io)
2. **MCP connection** -- connect your account via OAuth (see Setup below)
3. **Gemini API key** (optional) -- required only for AI image generation, link at [Settings > AI Models](https://app.reepl.io/settings/ai-models-api)

## Setup

```
# 1. Visit the OAuth page to connect your Reepl account
https://mcp.reepl.io/oauth/authorize

# 2. Log in with your Reepl credentials (Google or email)

# 3. Copy the API key shown after authorization

# 4. Configure the MCP server endpoint
https://mcp.reepl.io/mcp?key=YOUR_API_KEY
```

If you receive authentication errors at any point, re-authenticate at the URL above.

---

## Available Tools (18 total)

| Tool | Purpose |
|------|---------|
| `create_draft` | Save a new LinkedIn post draft |
| `get_drafts` | List and search your drafts |
| `update_draft` | Edit an existing draft |
| `delete_draft` | Remove a draft |
| `publish_to_linkedin` | Publish a post to LinkedIn immediately |
| `schedule_post` | Queue a post for future publishing |
| `update_scheduled_post` | Change time, content, or settings of a scheduled post |
| `get_published_posts` | View your published LinkedIn posts |
| `get_scheduled_posts` | View your scheduled post queue |
| `get_user_profile` | Get your Reepl account info |
| `get_voice_profile` | Read your voice profile (writing style patterns) |
| `update_voice_profile` | Update voice profile with learned patterns |
| `get_contacts` | Browse saved LinkedIn contacts |
| `get_lists` | Browse your contact lists |
| `get_collections` | Browse your saved post collections |
| `get_saved_posts` | Read posts from a specific collection |
| `get_templates` | Browse your post templates and ideas |
| `generate_image` | Generate an AI image for a post (requires Gemini API key) |

---

## Content Rules

All LinkedIn content MUST be plain text. Never use markdown formatting like **bold**, *italic*, or # headings. LinkedIn does not render markdown -- it will appear literally in the feed, looking AI-generated. Use line breaks, spacing, and natural punctuation for structure instead.

LinkedIn posts have a 3,000 character limit.

---

## Tool Reference

### 1. Create Draft

Save a post idea for later editing or publishing.

```json
{
  "content": "Just wrapped up a deep dive into how AI is reshaping B2B sales.\n\nHere are 3 things I learned...",
  "title": "AI in B2B Sales",
  "mediaUrls": ["https://example.com/image.jpg"]
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Post text (plain text only) |
| `title` | No | Draft title for organization |
| `mediaUrls` | No | Array of image URLs to attach |

### 2. Get Drafts

List and search your saved drafts.

```json
{
  "search": "AI sales",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of drafts to return (default: 20) |
| `search` | No | Filter drafts by keyword |

### 3. Update Draft

Edit an existing draft's content, title, or images.

```json
{
  "draft_id": "abc-123",
  "content": "Updated post content here...",
  "title": "New Title"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | ID of the draft to update |
| `content` | No | Updated post text |
| `title` | No | Updated title |
| `mediaUrls` | No | Updated image URLs (replaces existing) |

### 4. Delete Draft

```json
{
  "draft_id": "abc-123"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | ID of the draft to delete |

---

### 5. Publish to LinkedIn

Publish a post to LinkedIn immediately. This action is irreversible -- always confirm with the user before calling.

```json
{
  "content": "Excited to share that we just hit 10,000 users on Reepl!\n\nBuilding in public has been one of the best decisions we made.\n\nHere's what I'd tell founders who are hesitant to share their journey...",
  "visibility": "PUBLIC"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Post text (plain text only, max 3000 chars) |
| `mediaUrls` | No | Array of image URLs to include |
| `visibility` | No | `PUBLIC` (default) or `CONNECTIONS` |

### 6. Schedule Post

Queue a post for future publishing. Times are rounded to 15-minute intervals.

```json
{
  "content": "Monday motivation: the best time to start was yesterday. The second best time is now.",
  "scheduledFor": "2026-02-17T08:00:00Z",
  "visibility": "PUBLIC"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Post text (plain text only, max 3000 chars) |
| `scheduledFor` | Yes | ISO 8601 timestamp (e.g. `2026-02-17T08:00:00Z`) |
| `mediaUrls` | No | Array of image URLs |
| `visibility` | No | `PUBLIC` (default) or `CONNECTIONS` |

**Scheduling tips:**
- Ask the user for their preferred time rather than picking one yourself.
- If they want suggestions, recommend varied slots: early morning (7-8 AM), lunch (12-1 PM), or end of day (5-6 PM) in their timezone.
- Avoid scheduling all posts at the same time -- spread them for better engagement.

### 7. Update Scheduled Post

Change the time, content, visibility, or images on a post that's already scheduled.

```json
{
  "post_id": "post-456",
  "scheduledFor": "2026-02-18T12:30:00Z",
  "content": "Updated content for the scheduled post..."
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `post_id` | Yes | ID of the scheduled post |
| `scheduledFor` | No | New ISO 8601 timestamp |
| `content` | No | Updated post text |
| `visibility` | No | Updated visibility |
| `mediaUrls` | No | Updated image URLs (replaces existing) |

---

### 8. Get Published Posts

View the user's published LinkedIn posts.

```json
{
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of posts to return (default: 20) |

### 9. Get Scheduled Posts

View posts currently queued for future publishing.

```json
{
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of posts to return (default: 20) |

---

### 10. Get User Profile

Returns the user's name, email, and LinkedIn URL. No parameters required.

### 11. Get Voice Profile

Read the user's voice profile -- writing style patterns learned from their published posts. No parameters required.

Returns:
- `userInstructions` -- guidelines the user has set (topics to avoid/emphasize, brand keywords, custom rules, writing samples)
- `generatedProfile` -- LLM-learned patterns (tone dimensions, vocabulary preferences, hook styles, structure patterns, anti-patterns)
- `allowAutoUpdate` -- whether the generated profile can be updated automatically
- `isActive` -- whether the voice profile is active

**Always read the voice profile before generating content.** This is the key to writing posts that sound like the user, not like an AI.

### 12. Update Voice Profile

Update the voice profile with newly learned patterns after analyzing the user's posts.

```json
{
  "generatedProfile": {
    "schema_version": "1.0",
    "tone": { "primary": "conversational-authoritative" },
    "vocabulary": { "signature_phrases": ["here's the thing", "let me break this down"] },
    "structure": { "hook_patterns": [{ "type": "bold-statement" }, { "type": "question" }] },
    "anti_patterns": { "never_do": ["use corporate jargon", "start with 'I'm excited to announce'"] }
  }
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `allowAutoUpdate` | No | Only change if user explicitly requests |
| `isActive` | No | Toggle voice profile on/off |
| `userInstructions` | No | User-controlled guidelines -- only modify if user explicitly asks |
| `generatedProfile` | No | LLM-learned patterns from analyzing posts |

**Important:** Before updating `generatedProfile`, always check that `allowAutoUpdate` is `true`. If the user has locked their profile, do not update it.

---

### 13. Get Contacts

Browse saved LinkedIn contacts and profiles.

```json
{
  "search": "product manager",
  "limit": 20
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of contacts (default: 20) |
| `search` | No | Filter by name, headline, or keyword |

### 14. Get Lists

Browse the user's contact lists (curated groups of contacts).

```json
{
  "search": "leads",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `search` | No | Filter lists by name |
| `limit` | No | Number of lists (default: 20) |

---

### 15. Get Collections

Browse saved post collections (groups of bookmarked LinkedIn posts).

```json
{
  "search": "inspiration",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `search` | No | Filter collections by name |
| `limit` | No | Number of collections (default: 20) |

### 16. Get Saved Posts

Read posts from a specific collection. Use `get_collections` first to find the collection ID.

```json
{
  "collectionID": "col-789",
  "search": "storytelling",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `collectionID` | Yes | The collection to fetch from |
| `limit` | No | Number of posts (default: 20) |
| `search` | No | Filter posts by keyword |

### 17. Get Templates

Browse post templates and content ideas saved in the user's library.

```json
{
  "search": "product launch",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of templates (default: 20) |
| `search` | No | Filter by keyword |
| `catalogID` | No | Filter by specific catalog |

---

### 18. Generate Image

Generate an AI image for a LinkedIn post using Google Gemini. Requires the user to have linked their Gemini API key in [Reepl settings](https://app.reepl.io/settings/ai-models-api).

```json
{
  "style": "infographic",
  "postContent": "3 ways AI is changing B2B sales in 2026..."
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `style` | Yes | Image style (see table below) |
| `postContent` | No | Post content for context |
| `customPrompt` | If style is `custom` | Your own image prompt |

**Available styles:**

| Style | Output |
|-------|--------|
| `infographic` | Professional data visuals and charts |
| `minimal-illustration` | Clean line art illustrations |
| `bold-text` | Typography and quote cards |
| `screenshot-social-proof` | Mockup screenshots |
| `comic-storyboard` | Comic-style panels |
| `realistic-portrait` | Photorealistic scenes |
| `diagram-flowchart` | Diagrams and process flows |
| `custom` | Your own prompt (requires `customPrompt`) |

**Always show the generated image to the user for approval before publishing.** Pass the returned URL as `mediaUrls` when calling `publish_to_linkedin` or `schedule_post`.

---

## Common Patterns

### Pattern 1: Write a Post in the User's Voice

```
1. get_voice_profile          -- read their writing style
2. Ask user for topic          -- what do they want to write about?
3. Write draft (plain text!)   -- match their tone, hooks, vocabulary
4. Show draft, get feedback    -- iterate until they're happy
5. create_draft OR publish     -- save or go live
```

### Pattern 2: Schedule a Week of Content

```
1. get_voice_profile           -- read writing style
2. get_templates               -- browse content ideas
3. get_saved_posts             -- browse inspiration from collections
4. Write 3-5 posts             -- vary topics, hooks, formats
5. schedule_post (x5)          -- spread across Mon-Fri at varied times
```

### Pattern 3: Repurpose Saved Content

```
1. get_collections             -- find the right collection
2. get_saved_posts             -- browse posts in it
3. Pick a post, rewrite it     -- new angle, user's voice
4. create_draft or publish     -- save or go live
```

### Pattern 4: Post with AI-Generated Image

```
1. Write the post content first
2. generate_image              -- use post content as context
3. Show the image to user      -- get approval
4. publish_to_linkedin         -- pass image URL in mediaUrls
```

### Pattern 5: Analyze and Update Voice Profile

```
1. get_published_posts         -- fetch recent posts (limit: 20)
2. Analyze patterns            -- tone, hooks, vocabulary, structure
3. get_voice_profile           -- check if allowAutoUpdate is true
4. update_voice_profile        -- save learned patterns to generatedProfile
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Session expired or invalid` | OAuth token expired | Re-authenticate at https://mcp.reepl.io/oauth/authorize |
| `Content exceeds 3000 character limit` | Post too long | Shorten the content |
| `draft_id is required` | Missing draft ID | Call `get_drafts` first to find the ID |
| `collectionID is required` | Missing collection ID | Call `get_collections` first to find the ID |
| `GEMINI_NOT_LINKED` | No Gemini API key | User must link key at https://app.reepl.io/settings/ai-models-api |
| `Rate limit exceeded` | Too many requests | Wait a moment and retry |
| `Resource not found` | Invalid ID | The draft/post/collection may have been deleted |

---

## Best Practices

1. **Always read the voice profile first.** Before writing any content, call `get_voice_profile` to understand the user's writing style. Posts should sound like them, not like an AI.
2. **Plain text only.** Never use markdown in post content. No `**bold**`, no `*italic*`, no `# headings`. LinkedIn renders these literally.
3. **Confirm before publishing.** Always show the final content and get explicit confirmation before calling `publish_to_linkedin` or `schedule_post`. These affect the user's real LinkedIn profile.
4. **Vary scheduling times.** Don't default to 9 AM for every post. Ask the user, or suggest varied slots across mornings, lunch, and end of day.
5. **Never fabricate data.** Don't invent engagement metrics, analytics, or post performance numbers. Only report what the API returns.
6. **Respect voice profile locks.** If `allowAutoUpdate` is false, do not modify `generatedProfile`. The user has intentionally locked their voice profile.
7. **Use the library.** Before writing from scratch, check templates and saved posts for inspiration. The user has curated these for a reason.

---

## See Also

- [Reepl](https://reepl.io) -- AI-powered LinkedIn content management platform
- [Reepl Help Center](https://help.reepl.io) -- Documentation and guides
- [MCP Setup Guide](https://mcp.reepl.io) -- Connect your Reepl account to Claude
- [Reepl Chrome Extension](https://chromewebstore.google.com/detail/reepl/geomampobbapgnflneaofdplfomdkejn) -- AI writing assistant for LinkedIn
