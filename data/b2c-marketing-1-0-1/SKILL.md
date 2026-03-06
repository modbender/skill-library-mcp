---
name: b2c-marketing
description: B2C mobile app marketing via short-form video content on TikTok, Instagram Reels, and YouTube Shorts. Use when creating, scheduling, or strategizing organic social media content for consumer apps. Covers slideshow generation, caption writing, format research, posting via Post Bridge API, and content performance analysis.
---

# B2C Marketing — Short-Form Video Content Machine

Automate organic B2C app marketing through short-form video on TikTok, Instagram Reels, and YouTube Shorts. This skill is based on a proven method that drove 30,000 downloads in one month with zero ad spend.

## The Growth Playbook

### Phase 1: Account Warmup (Days 1-2)
- Create new account(s) on Instagram and/or TikTok
- Scroll 15 min/day in your target audience niche ONLY
- Follow, comment, and like posts that your app/product is relevant to
- This teaches the algorithm where to push your content — CRITICAL for TikTok especially
- Never buy old accounts — they suck and have a locked-in audience you can't change
- Same email for multiple TikTok accounts is fine

### Phase 2: Research (Ongoing)
- Save any videos you see that you could remake to promote your app
- Study what other apps in your niche are doing
- Browse competitor accounts — sort by Popular on TikTok to see their top performers
- Note caption patterns, video length, hooks, hashtags
- Think creatively about how existing viral formats can showcase YOUR app

### Phase 3: Start Posting (Day 3+)
- Start with 1 post/day per warmed account — quality over quantity
- Every post needs a CTA relevant to your app (in caption, comment, or end of video)
- Views without downloads are useless — always tie content back to your app
- If you can't break 500 views after consistent posting, pause 2-3 days and improve content quality

### Phase 4: Find Your Winner
- Each app's "winning format" is unique — this may take 300+ videos to find
- Keep testing new formats, hooks, and angles
- Once you find a format that pops, DOUBLE DOWN on it
- Make variations of your winner — same hook structure, different content

### Phase 5: Scale with Post Bridge
- Once you have a winning format, scale to 2-6 posts/day
- Use Post Bridge API to upload and schedule across IG, TikTok, YouTube simultaneously
- Instagram as main platform, then reupload to YouTube, TikTok, and others via Post Bridge
- This takes 10x less time than posting manually on each platform

## What the Algorithm Wants

The algo LOVES two things:
1. **Watch time** — short videos (under 10 seconds) get highest completion rates
2. **Comments** — make content that drives people to comment ("what app is this?")

Your two goals with every piece of content: maximize watch time and drive comments.

Don't name the app in the caption — let people ask in comments. This drives engagement AND the algo rewards comment activity.

## Content Strategy

### Key Principles
- Hook in first 1-2 seconds (text overlay or surprising visual)
- "POV:" captions drive curiosity and shares
- Show the app in action, not just talking about it
- Emotional triggers: love, FOMO, curiosity, relatability
- 1 creative, well-thought-out post > 5 pieces of slop
- Log every lesson, iterate on what works

### The Hook Formula

**WINNING formula:** [Another person] + [conflict/doubt] → showed them [app/result] → they changed their mind

- Creates a story in the viewer's head — they picture the reaction
- It's about the HUMAN MOMENT, not the app
- Self-focused hooks about features/price → dead
- Always ask: "Who's the other person, and what's the conflict?"

### Hook Templates (adapt to your niche)
- `pov: [relatable scenario involving your app]`
- `found the cutest/best/most useful [app type] for [audience]`
- `may this type of [emotion] find you [emoji]`
- `[person] didn't believe me until I showed them this`
- `this [feature] is actually insane`
- `how did I not know about this sooner`

### Hashtag Strategy
- Max 4-5 hashtags per post
- Mix broad (#fyp #viral) with niche (#yourappniche)
- Don't include app name in hashtags unless it's already known

### Slideshow Format
AI-generated slideshows for TikTok/Reels — see `references/slideshow-method.md`:
- Use AI image generation for frames
- Add text overlays programmatically
- Great for apps without visual demo content

## Posting via Post Bridge API

Base: `https://api.post-bridge.com` | Auth: `Authorization: Bearer <key>`

### Setup
1. Create Post Bridge account at post-bridge.com ($9/mo, API add-on $14/mo)
2. Connect your social accounts (TikTok, Instagram, YouTube, Twitter, etc.)
3. Get API key from Settings → API
4. Store in workspace `.env`: `POST_BRIDGE_API_KEY=pb_live_xxxxx`

### Posting Flow
1. `POST /v1/media/create-upload-url` → `{ "mime_type": "video/mp4", "size_bytes": <int>, "name": "file.mp4" }`
2. `PUT <upload_url>` with binary file
3. `POST /v1/posts` with caption, media IDs, social_account IDs, optional `scheduled_at`
4. `GET /v1/posts/<id>` to check status

### Platform Configs (pass in `platform_configurations`)
- **TikTok:** `{ draft: true, video_cover_timestamp_ms: 3000 }` — draft lets you add trending sound manually
- **Instagram:** `{ video_cover_timestamp_ms: 3000 }` — normal reel by default
- **YouTube:** `{ video_cover_timestamp_ms: 3000 }` — posts as Short automatically

### Scheduling
- Set `scheduled_at` (ISO 8601 UTC) to schedule ahead
- Omit for instant post
- Stagger posts throughout the day (e.g. 9am + 3pm)

## Performance Tracking

Track every post in a local file:
- Post ID, platform, caption, format type, date
- Check views by browsing platform pages
- Note which hooks/formats perform best
- Weekly review: double down on winners, try new variations of top performers
- If a format stops working, go back to research phase

## Daily Workflow

1. Pick next unposted video from content folder
2. Extract frame → read text overlay → write caption + hashtags
3. Upload media → create post → schedule or post instantly
4. Move video to `posted/` subfolder
5. Set cron to check post status 5 mins after scheduled time
6. Report results (include TikTok caption in copy-paste block if using draft mode)
7. Repeat for each daily post slot
