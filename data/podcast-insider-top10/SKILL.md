---
name: podcast_insider_top10
description: Professional analytical digest of top 10 podcast industry news, trends, and business insights from premier global sources.
tags: podcasting, audio, media, industry, analytics
---

# Podcast Insider Top-10 Skill

This skill provides comprehensive podcast industry intelligence by aggregating, analyzing, and synthesizing news from leading global podcasting authorities.

## Objective
Upon request (e.g., "Podcast industry news"), the agent must aggregate information from the specified RSS feeds, analyze market movements, technology shifts, and platform updates, delivering a curated top-10 briefing.

## Curated Sources
1. **Podnews Daily** (https://podnews.net/feed) - The definitive daily news source for the industry.
2. **The Podcast Sessions** (https://thepodsessions.com/feed/) - Industry insights and interviews.
3. **Discover Pods** (https://discoverpods.com/feed/) - Reviews and industry trends.
4. **Pacific Content** (https://pacific-content.com/feed/) - Insights on branded content and strategy.
5. **Podcaster News** (https://podcasternews.com/feed/) - Global podcasting news.
6. **Business of Podcasting** (https://www.thepodcasthost.com/business-of-podcasting/feed) - Monetization and industry growth.
7. **Buzzsprout Blog** (https://www.buzzsprout.com/blog.rss) - Creator-focused news and trends.
8. **Spreaker Blog** (https://blog.spreaker.com/feed/) - Platform updates and technical insights.
9. **Bingeworthy** (https://bingeworthy.substack.com/feed) - High-level content reviews and industry context.
10. **The Audio Insurgent** (https://audioinsurgent.substack.com/feed) - Strategic analysis by industry veterans.
11. **The Squeeze** (https://www.thisisthesqueeze.com/feed) - Deep industry reporting and investigative pieces.

## Instructions & Logic
- **Verification & Synthesis:** Cross-reference major stories appearing across multiple feeds to provide a unified, detailed entry.
- **Trend Spotting:** Look for recurring themes in monetization, AI integration in audio, and platform policy changes.
- **Categorization:** Classify items as "Market Move," "Platform Update," "Content Strategy," or "Tech Innovation."
- **Deep Research:** For significant industry shifts (e.g., Spotify acquisitions, major ad-tech updates), use `web_search` to find broader context and historical data.
- **Importance Ranking:** Rank news based on its potential to impact creators and media owners.

## Formatting Guidelines
- **Headline:** Clear and professional.
- **Strategic Take:** A concise analysis of how this news impacts the global podcasting ecosystem.
- **Source Context:** Provide direct links to primary sources.
- **Output Language:** Respond in the user's preferred language. Translate insights from the source material only if required by the user's language setting.

## Tools
- `web_fetch`: For parsing primary RSS feeds and articles.
- `web_search`: For cross-referencing and deep-dive context.
- `LLM Reasoning`: For summarization, categorization, and strategic analysis.
