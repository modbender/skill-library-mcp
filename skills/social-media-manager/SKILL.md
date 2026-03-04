# SKILL: Social Media Manager

## Goal
Automate the creation and scheduling of high-engagement social media content across **any platform** (TikTok, Instagram, X/Twitter, LinkedIn, Facebook, YouTube, and more) using AI generation and the **Postiz API**.

## Supported Platforms
Postiz supports multi-platform publishing. Any platform you connect in Postiz can be targeted:
- **TikTok** — Slideshows, carousels, short videos
- **Instagram** — Reels, carousels, single-image posts
- **X / Twitter** — Text posts, image threads
- **LinkedIn** — Articles, image posts, carousels
- **Facebook** — Posts, stories, reels
- **YouTube** — Shorts, community posts
- **Pinterest, Reddit, Threads**, and more as Postiz adds integrations

## Workflow
1. **Research & Ideation**: Brainstorm hooks using the "Conflict Formula": `[Person] + [Conflict/Doubt] -> [AI Solution] -> [Resolution]`.
2. **Content Generation**: Use AI to generate platform-appropriate content.
   - **Images/Slides**: AI-generated visuals (e.g., Nano Banana Pro, gpt-image-1.5) at platform-optimal resolutions.
   - **Text**: AI-written captions, threads, or articles tailored to each platform's tone and format.
   - **Video thumbnails**: AI-generated cover images for video content.
3. **Platform Adaptation**: Adjust content format per platform:
   - TikTok/Instagram: Portrait 1024x1536, 6-slide carousels
   - X/Twitter: Landscape/square images, concise text
   - LinkedIn: Professional tone, landscape images
   - YouTube Shorts: Portrait video thumbnails
4. **Consistency Check**: Ensure "locked architecture" (same subject/theme, different styles).
   - *Critical*: Write one detailed description of the subject and reuse it in EVERY prompt. Only change the style/lighting/context.
5. **Scheduling & Publishing**: Upload and schedule via Postiz API.
   - Draft mode (`SELF_ONLY`) for review before publishing.
   - Scheduled posts for optimal engagement times.
   - Cross-post the same content across multiple platforms simultaneously.
6. **Notification**: Ping user with the caption and links to review/publish.

## Postiz API Integration
Postiz acts as the universal publishing layer. One API handles all connected platforms.

### Configuration
- **API URL**: `https://api.postiz.com/public/v1`
- **Auth Header**: `Authorization: <API_KEY>` (No Bearer prefix).
- **Media Upload**: `POST /upload` first to get `id` and `path`.
- **Posting Method**: Use `UPLOAD` (Draft) for multi-image content. `DIRECT_POST` works for single-image/text posts.

### Posting Structure
- Top level: `type` ("now" or "schedule"), `date` (ISO 8601), `posts` (array).
- Post level: `integration: { id: "..." }`, `value: [ { content: "...", image: [ { id, path } ] } ]`.
- Settings level: Platform-specific settings (e.g., `__type: "tiktok"`, `__type: "instagram"`, etc.).

### Technical Specs
- **Upload Media**: `curl -X POST {API_URL}/upload -H "Authorization: {KEY}" -F "file=@path/to/file"`
- **Create Post**: `curl -X POST {API_URL}/posts -H "Authorization: {KEY}" -H "Content-Type: application/json" -d '{...}'`
- **List Integrations**: `curl {API_URL}/integrations -H "Authorization: {KEY}"` — use this to discover connected platforms and their integration IDs.

## Prompt Strategy
### The Conflict Formula
Adaptable to any product, service, or brand:
- `[Person] + [Common Pain Point] -> [Your Solution] -> [Success/Resolution]`
- Identify 4-6 pain points per product for content variety.
- Each pain point becomes a unique content series.

### Slide/Carousel Structure
- **Slide 1**: The "Before" or "Conflict" state + Hook Text Overlay
- **Slides 2-5**: The "Transformation" or style options
- **Slide 6**: The "Final Result" / Call to Action

## Success Log
- **2026-02-14**: Posted "Rejected TWICE" carousel (6 slides, Conflict Formula). Fixed API fields: `duet`/`stitch`/`comment` (booleans), `autoAddMusic` ("yes"/"no"), `brand_content_toggle`/`brand_organic_toggle` (booleans). Top-level `shortLink` (bool) and `tags` (array) required.
- **2026-02-13**: Successfully transitioned to `UPLOAD` method for TikTok slideshows. Confirmed that `DIRECT_POST` triggers `ERROR` state for multi-image sequences.

## Failure Log
- **2026-02-13**: API Authentication requires `Authorization: <KEY>` (no Bearer).
- **2026-02-13**: Postiz requires `content_posting_method` and `privacy_level` in settings.
- **2026-02-13**: Draft upload via Postiz requires valid media URLs (uploads.postiz.com) and correct `posts` array structure.
