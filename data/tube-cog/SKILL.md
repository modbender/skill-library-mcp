---
name: tube-cog
description: YouTube content creation powered by CellCog. Create YouTube videos, Shorts, thumbnails, scripts, long-form content, educational videos, tutorials, vlogs. AI-powered YouTube creator tools.
metadata:
  openclaw:
    emoji: "📺"
author: CellCog
dependencies: [cellcog]
---

# Tube Cog - YouTube Content Powered by CellCog

Create YouTube videos that get views - from Shorts to long-form tutorials to eye-catching thumbnails.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**Quick pattern (v1.0+):**
```python
# Fire-and-forget - returns immediately
result = client.create_chat(
    prompt="[your YouTube content request]",
    notify_session_key="agent:main:main",
    task_label="youtube-content",
    chat_mode="agent"  # Agent mode for most content
)
# Daemon notifies you when complete - do NOT poll
```

---

## What Content You Can Create

### YouTube Shorts

Vertical, snackable content for discovery:

- **Quick Tips**: "Create a 45-second Short explaining one JavaScript trick"
- **Reactions/Commentary**: "Make a Short reacting to a viral tech moment"
- **Teasers**: "Create a Short teasing my upcoming full video on AI"
- **Trending Formats**: "Make a 'Things that just make sense' Short for programmers"
- **Behind-the-Scenes**: "Create a BTS Short of my content creation process"

**Example prompt:**
> "Create a 50-second YouTube Short: 'The VS Code shortcut that changed my life'
> 
> Hook: 'Stop coding like it's 2010'
> Demo: Show the multi-cursor feature
> Reaction: Mind-blown moment
> CTA: 'Full tutorial on my channel'
> 
> Fast-paced, screen recording style with facecam energy."

### Long-Form Videos

In-depth content that builds audience:

- **Tutorials**: "Create a 15-minute tutorial on building a REST API with Python"
- **Explainers**: "Make a 10-minute video explaining how blockchain works"
- **Reviews**: "Create a comprehensive review of the new MacBook Pro"
- **Documentaries**: "Make a mini-documentary about the history of video games"
- **Essays**: "Create a video essay on why minimalism is becoming popular"

**Example prompt:**
> "Create a 12-minute YouTube video: 'Build Your First AI App in 2026'
> 
> Structure:
> - Hook (30 sec): Show the finished app
> - Intro (1 min): What we're building and why
> - Setup (2 min): Environment and dependencies
> - Core tutorial (7 min): Step-by-step coding
> - Testing (1 min): Run and demo
> - Outro (30 sec): Next steps and subscribe CTA
> 
> Style: Educational, friendly, clear explanations. Code on screen with voiceover."

### Thumbnails

Click-worthy images that drive views:

- **Reaction Thumbnails**: "Create a thumbnail with shocked face and bold text"
- **Tutorial Thumbnails**: "Make a clean thumbnail for a coding tutorial"
- **Versus Thumbnails**: "Create an X vs Y comparison thumbnail"
- **Listicle Thumbnails**: "Make a '10 Things' style thumbnail"
- **Story Thumbnails**: "Create an intriguing thumbnail that hints at drama"

**Example prompt:**
> "Create a YouTube thumbnail for: 'I Built an App in 24 Hours'
> 
> Elements:
> - Person looking stressed/determined
> - Timer showing 24:00:00
> - Code on screen in background
> - Bold text: '24 HOURS'
> 
> Colors: Dark background, yellow/orange accents
> Style: High contrast, readable at small size"

### Scripts & Outlines

Content planning before production:

- **Full Scripts**: "Write a complete script for a 10-minute video on productivity"
- **Video Outlines**: "Create a detailed outline for a product review"
- **Hook Variations**: "Give me 5 different hooks for my video about investing"
- **CTA Scripts**: "Write compelling end-screen call-to-action scripts"

---

## YouTube Specs

| Format | Dimensions | Duration |
|--------|------------|----------|
| Standard Video | 1920×1080 (16:9) | Any length |
| Shorts | 1080×1920 (9:16) | Up to 60 seconds |
| Thumbnail | 1280×720 | - |

---

## Video Styles

| Style | Best For | Characteristics |
|-------|----------|-----------------|
| **Educational** | Tutorials, explainers | Clear, structured, helpful |
| **Entertainment** | Vlogs, reactions | Personality-driven, dynamic |
| **Professional** | B2B, corporate | Polished, trustworthy |
| **Documentary** | Essays, deep dives | Cinematic, researched |
| **Fast-Paced** | Shorts, compilations | Quick cuts, high energy |

---

## Chat Mode for YouTube Content

| Scenario | Recommended Mode |
|----------|------------------|
| Shorts, thumbnails, scripts, standard tutorials | `"agent"` |
| Documentary-style content, complex video essays, multi-part series planning | `"agent team"` |

**Use `"agent"` for most YouTube content.** Shorts, thumbnails, and standard videos execute well in agent mode.

**Use `"agent team"` for complex narratives** - documentaries, video essays, or content requiring deep research and storytelling craft.

---

## Example Prompts

**Educational tutorial:**
> "Create a YouTube tutorial: 'Docker for Beginners - Full Course'
> 
> Length: 20 minutes
> Audience: Developers who've never used Docker
> 
> Chapters:
> 1. What is Docker and why use it? (3 min)
> 2. Installing Docker (2 min)
> 3. Your first container (4 min)
> 4. Dockerfile basics (4 min)
> 5. Docker Compose (4 min)
> 6. Real-world example (3 min)
> 
> Style: Screen recording with clear voiceover. Beginner-friendly, no jargon."

**Engaging Short:**
> "Create a YouTube Short: 'AI wrote my entire codebase'
> 
> Hook: 'I let AI write 100% of my code for a week'
> Content: Quick montage of AI coding, my reactions, the chaos
> Twist: 'And it actually... worked?'
> CTA: 'Full video on my channel'
> 
> Fast cuts, meme energy, relatable programmer humor."

**Click-worthy thumbnail:**
> "Create a thumbnail for: 'Why I Quit My $300K Job'
> 
> Show: Professional person walking away from office building
> Expression: Confident, peaceful
> Text: '$300K → QUIT' in bold
> Style: Cinematic, slightly desaturated, text pops
> 
> Must be readable at small sizes."

---

## Tips for Better YouTube Content

1. **Hook in 5 seconds**: YouTube viewers decide instantly. Front-load the value or intrigue.

2. **Thumbnails matter more than titles**: A great video with bad thumbnail won't get clicked. Invest in thumbnail quality.

3. **Retention > Length**: A tight 8-minute video beats a padded 20-minute video. Respect viewer time.

4. **Chapters improve watch time**: Structure long videos with clear chapters. Helps SEO too.

5. **End screens work**: Ask for subscribes when viewers are most engaged (after delivering value).

6. **Shorts feed long-form**: Use Shorts to drive traffic to your main channel content.