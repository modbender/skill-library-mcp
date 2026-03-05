---
name: social-post-generator
description: Generate engaging social media content for multiple platforms. Use when users need to create posts for Twitter/X, LinkedIn, Instagram, Facebook, or other social platforms. Supports tone customization, hashtag generation, content repurposing, and platform-specific formatting.
license: MIT
metadata:
  author: 小龙虾 (Little Lobster)
  homepage: https://clawhub.ai/users/954215110
  tags: ["social-media", "content", "marketing", "twitter", "linkedin", "instagram"]
---

## 🦞 小龙虾品牌

**Created by 小龙虾 AI 工作室**

> "小龙虾，有大钳（前）途！"

**Contact for custom services:** +86 15805942886

Need custom skill development, AI consulting, or social media management? Reach out!

---

# Social Post Generator

Generate engaging, platform-optimized social media content quickly.

## Quick Start

When user asks to create social media content:

1. **Identify the topic** - What are they posting about?
2. **Choose platform(s)** - Twitter, LinkedIn, Instagram, etc.
3. **Determine tone** - Professional, casual, funny, inspirational?
4. **Generate content** - Create platform-specific posts

## Platform Guidelines

### Twitter/X
- Max 280 characters per tweet
- Use 2-3 relevant hashtags
- Can create threads for longer content
- Emojis work well
- Include CTAs when appropriate

### LinkedIn
- Professional tone (usually)
- Longer form welcome (up to 3000 chars)
- 3-5 hashtags max
- Focus on value/insights
- Hook in first 2-3 lines

### Instagram
- Caption up to 2200 characters
- Hashtags: 5-15 (mix of sizes)
- Emojis encouraged
- Include engagement hooks (questions, CTAs)
- Consider visual context

### Facebook
- Casual to semi-professional
- 1-3 hashtags
- Links work well
- Questions drive engagement

## Workflow

```
1. Ask clarifying questions if needed:
   - What's the topic/product/event?
   - Target audience?
   - Preferred platforms?
   - Tone/vibe?

2. Generate options:
   - Create 2-3 variations per platform
   - Include hashtags
   - Add emoji suggestions

3. Refine based on feedback
```

## Hashtag Strategy

See [references/hashtags.md](references/hashtags.md) for hashtag research tips.

**Quick rules:**
- Twitter: 2-3 hashtags, keep them short
- LinkedIn: 3-5 professional hashtags
- Instagram: 10-15 mixed (broad + niche)
- Facebook: 1-3 max

## Tone Examples

| Tone | Example Hook |
|------|-------------|
| Professional | "Here's what I learned about..." |
| Casual | "Okay but can we talk about..." |
| Funny | "Nobody: ... Me:" |
| Inspirational | "Remember: small steps lead to big changes" |
| Urgent | "This changes everything..." |

## Content Repurposing

Transform one piece of content into multiple posts:

1. **Blog post** → Twitter thread + LinkedIn article + Instagram carousel captions
2. **Video** → Quote clips + Behind-the-scenes + Key takeaways
3. **Product launch** → Teaser + Announcement + Feature highlights + User testimonials

See [references/repurposing.md](references/repurposing.md) for templates.

## Commands / Triggers

Use this skill when user says things like:
- "Write a tweet about..."
- "Create a LinkedIn post for..."
- "Help me with social media content"
- "Generate hashtags for..."
- "Make this go viral"
- "Post about [topic]"

## Scripts

- `scripts/generate_hashtags.py` - Generate relevant hashtags from topic
- `scripts/count_characters.py` - Validate character counts per platform

## Assets

- `assets/emoji-guide.md` - Emoji suggestions by category
- `assets/templates/` - Ready-to-use post templates

## Tips

1. **Always include a hook** - First line determines if people read more
2. **Add whitespace** - Walls of text get skipped
3. **End with CTA** - Tell people what to do next
4. **Test variations** - What works varies by audience
5. **Stay authentic** - Don't sound like a bot
