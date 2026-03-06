---
name: podcast-publisher
description: Generate valid podcast RSS 2.0 feeds with iTunes extensions for
  Apple Podcasts, Spotify, and more.
---


# Podcast Publisher

Generate podcast RSS feeds ready for directory submission.

**Use when** creating podcast feeds, adding episodes, or setting up a new podcast.

## Requirements

- No external tools or API keys needed
- Output: static XML file, hostable anywhere

## Instructions

1. **Gather metadata** — required fields:

   **Podcast (channel)**:
   | Field | Required | Example |
   |-------|----------|---------|
   | Title | ✅ | "My Tech Podcast" |
   | Description | ✅ | "Weekly deep dives into..." |
   | Author | ✅ | "John Doe" |
   | Artwork URL | ✅ | Must be 3000×3000 JPEG/PNG |
   | Website | ✅ | "https://example.com" |
   | Language | ⬚ | "en-us" (default) |
   | Category | ⬚ | "Technology" |
   | Explicit | ⬚ | false (default) |

   **Per episode**:
   | Field | Required | Example |
   |-------|----------|---------|
   | Title | ✅ | "Episode 1: Getting Started" |
   | Description | ✅ | "In this episode..." |
   | Audio URL | ✅ | Direct link to .mp3/.m4a |
   | Duration | ✅ | "01:23:45" (HH:MM:SS) |
   | Pub date | ✅ | RFC 2822 format |
   | GUID | ⬚ | Auto-generate if not provided |

2. **Generate RSS XML**:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
     <channel>
       <title>TITLE</title>
       <description>DESCRIPTION</description>
       <language>en-us</language>
       <itunes:author>AUTHOR</itunes:author>
       <itunes:image href="ARTWORK_URL"/>
       <itunes:category text="CATEGORY"/>
       <itunes:explicit>false</itunes:explicit>
       <link>WEBSITE_URL</link>

       <item>
         <title>EPISODE_TITLE</title>
         <description>EPISODE_DESCRIPTION</description>
         <enclosure url="AUDIO_URL" length="FILE_SIZE" type="audio/mpeg"/>
         <itunes:duration>HH:MM:SS</itunes:duration>
         <pubDate>Thu, 15 Jan 2025 10:00:00 +0000</pubDate>
         <guid isPermaLink="false">UNIQUE_ID</guid>
       </item>
     </channel>
   </rss>
   ```

3. **Validate** before saving:
   - ✅ Dates in RFC 2822 format (e.g., `Thu, 15 Jan 2025 10:00:00 +0000`)
   - ✅ Audio URLs are direct file links (not streaming pages or YouTube)
   - ✅ Duration format: `HH:MM:SS` or `MM:SS`
   - ✅ GUIDs unique per episode
   - ✅ Artwork is 3000×3000 minimum, JPEG or PNG
   - ✅ XML is well-formed (no unescaped `&`, `<`, `>` in text)

4. **Save** as `feed.xml`.

5. **Add new episodes**: Read existing `feed.xml`, insert new `<item>` at top of items list, save.

## Hosting Options

- **GitHub Pages**: Free, commit `feed.xml` to repo
- **S3 / Cloudflare R2**: Upload XML + audio files
- **Any static host**: Just serve the XML file with `application/rss+xml` content type

## Directory Submission URLs

- Apple Podcasts: [podcastsconnect.apple.com](https://podcastsconnect.apple.com)
- Spotify: [podcasters.spotify.com](https://podcasters.spotify.com)
- Google Podcasts: Auto-indexed from RSS

## Edge Cases

- **Special characters in text**: Escape `&` → `&amp;`, `<` → `&lt;` in titles/descriptions.
- **File size unknown**: Use `0` for `length` attribute — most players handle it.
- **Multiple categories**: Nest `<itunes:category>` elements.
- **Trailer/bonus episodes**: Use `<itunes:episodeType>trailer</itunes:episodeType>`.
- **Seasons**: Add `<itunes:season>1</itunes:season>` and `<itunes:episode>1</itunes:episode>`.

## Validation Tools

- [Podbase Validator](https://podba.se/validate/)
- [Cast Feed Validator](https://castfeedvalidator.com/)
