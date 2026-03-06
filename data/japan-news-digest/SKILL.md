---
name: japan-news-digest
description: Fetch and summarize top Japanese news into a categorized,
  digestible daily digest.
---


# Japan News Digest

Fetch, categorize, and summarize top Japanese news.

**Use when** user asks for Japanese news, daily digest, or what's happening in Japan.

**Triggers**: "Japan news", "日本のニュース", "news digest", "today's news Japan"

## Requirements

- `web_search` and `web_fetch` tool access
- No API keys needed

## Instructions

1. **Fetch news** — Run 2-3 searches:
   ```
   web_search("Japan news today", country="JP", count=10)
   web_search("日本 ニュース 今日", search_lang="ja", count=10)
   ```
   For specific topics:
   - Tech/AI: `"日本 AI テクノロジー 最新"`
   - Business: `"日本 経済 ビジネス"`
   - Politics: `"日本 政治 国会"`

2. **Read promising articles** with `web_fetch` — pick 5-8 most interesting/important articles.

3. **Categorize**:
   - 🏛️ Politics & Society
   - 💰 Business & Economy
   - 🤖 Technology & AI
   - 🌏 International
   - 🎌 Culture & Entertainment

4. **Output format**:
   ```
   ## 📰 Japan News Digest
   **Date:** YYYY-MM-DD

   ### 🔥 Top Story
   **[Headline](URL)**
   2-3 sentence summary. Key takeaway.

   ### 🤖 Technology
   **[Headline](URL)**
   Summary. (Source: NHK)

   ### 💰 Economy
   **[Headline](URL)**
   Summary. (Source: 日経)

   ---
   📌 = Important | 🔥 = Breaking | 💡 = Interesting
   *Sources: NHK, 日経, 朝日, Reuters Japan*
   ```

5. **Optional**: Save to `~/news-digests/YYYY-MM-DD.md` if requested.

## Guidelines

- Default language: **Japanese summaries**. Switch to English on request.
- Prioritize relevance tags: 🔥 breaking > 📌 important > 💡 interesting
- Always attribute sources
- Don't extract paywalled content — summarize from available preview text
- Include 5-8 articles per digest (not too long, not too short)

## Edge Cases

- **No major news**: Include trending topics or interesting features instead.
- **Duplicate stories**: Merge coverage from multiple sources, cite all.
- **English-only request**: Search with English queries and summarize in English.
- **Specific topic request**: Focus search and categories on that topic only.
