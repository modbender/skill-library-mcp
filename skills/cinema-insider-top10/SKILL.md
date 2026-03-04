---
name: cinema_insider_top10
description: Professional analytical digest of top 10 movie and TV industry news using advanced AI aggregation and cross-referencing.
tags: cinema, movies, tv, production, Hollywood, analytics
---

# Cinema Insider Top-10 Skill

This skill provides high-tier movie and TV industry intelligence by aggregating, deduplicating, and analyzing news from premier international sources.

## Objective
Upon request (e.g., "Cinema news"), the agent must aggregate news from the curated RSS feeds, perform cross-source verification, and deliver a ranked top-10 briefing of the most significant industry events.

## Curated Sources
1. **Variety** (http://variety.com/feed/) - Business and production standards.
2. **Deadline Hollywood** (https://deadline.com/feed/) - Breaking news.
3. **The Hollywood Reporter** (https://www.hollywoodreporter.com/c/movies/feed/) - In-depth industry reporting.
4. **ComingSoon.net**, **Collider**, **Screen Rant**, **ScreenCrush**, **LRMonline**, **Entertainment Weekly**, **TV Insider**, **IMP Awards**.

## Instructions & Logic
- **Verification & Deduplication:** If a story appears in multiple feeds, aggregate all details into a single high-quality entry. Do not repeat the same event.
- **Deep Dive Analysis:** For major "Breaking News" (e.g., major casting, studio deals, or director attachments), use `web_search` to gather additional context, production timelines, or historical significance.
- **Categorization:** Identify each news item as "Production," "Business," "Casting," or "Marketing."
- **Visual Capture:** For highly visual news (e.g., new trailer releases or poster reveals), use the `browser` tool to capture and present a preview if applicable.
- **Ranking:** Order the top 10 by industry impact, placing production and business strategy news above trailers and general entertainment.

## Formatting Guidelines
- **Headline:** Clear and professional.
- **Analytical Take:** A concise explanation of why this news matters for industry professionals.
- **Source Context:** Provide direct links and mention if the news is verified by multiple top-tier outlets.
- **Output Language:** Respond in the user's preferred language, translating the insights from the English source material.

## Tools
- `web_fetch`: For parsing the primary RSS feeds.
- `web_search`: For cross-referencing, verifying "Breaking News," and adding depth.
- `browser`: For visual inspection of sources and capturing media previews.
- `LLM Reasoning`: For summarization, importance ranking, and deduplication.
