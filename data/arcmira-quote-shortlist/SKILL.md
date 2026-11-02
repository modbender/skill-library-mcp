---
name: arcmira-quote-shortlist
description: Search YouTube and podcast transcripts for a spoken quote or a shortlist of clips on a topic. Return each passage with its timestamp and source recording using Arcmira MCP.
---

# Find a quote for a clip shortlist

Use a connected Arcmira account. If the tools are missing, open the [MCP setup guide](https://arcmira.com/docs/mcp-server). The [API docs](https://arcmira.com/docs) cover direct access.

1. Call `arcmira_describe` with `topic: "search"` for the current search arguments and response fields.
2. Search for the user's phrase in `arcmira_execute_read`. Preserve their date window when supplied. For a named show, resolve its channel ID first. Put the phrase in `query`.

   This example finds up to three candidate clips about vibe coding from the past 90 days.

   ```js
   const result = await arcmira.search({ query: 'vibe coding', after: arcmira.daysAgo(90), limit: 3 });
   return result.chunks.map(({ text, video_title, channel_name, start_seconds, watch_url }) => ({ text, video_title, channel_name, start_seconds, watch_url }));
   ```

3. Read the whole passage before selecting a sentence. Keep enough context to preserve its meaning. If you cannot identify the speaker, cite the show and leave the speaker unnamed. The timestamp locates the passage. Listen to the recording before presenting it as a precise edit point.
4. Return one row per distinct moment with the quotation, show, episode title, timestamp and returned source link. If fewer passages fit, report how many you found and the window you searched. Coverage depends on the indexed catalog and account access.
