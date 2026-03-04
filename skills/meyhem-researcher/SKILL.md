---
name: meyhem-researcher
description: Deep research agent with outcome-driven ranking: results get smarter the more agents use it. Multi-angle search, cited reports. No API key.
version: 0.1.1
author: c5huracan
homepage: https://github.com/c5huracan/meyhem
metadata:
  openclaw:
    requires:
      bins:
        - curl
---

# Meyhem Deep Researcher

A multi-step research agent powered by Meyhem search at https://api.rhdxm.com. Given a research question, decompose it into targeted queries, search each, select the best results, read their content, and synthesize a cited report. No API key needed.

## Step 1: Decompose

Break the user's research question into 3-5 focused search queries that cover different angles of the topic.

## Step 2: Search

For each query, search Meyhem:

```bash
curl -s -X POST https://api.rhdxm.com/search \
  -H "Content-Type: application/json" \
  -d '{"query": "YOUR_QUERY", "agent_id": "openclaw-researcher", "num_results": 10}'
```

Returns JSON with `search_id` and `results` array. Each result has `url`, `title`, `snippet`, `score`, `provider`, `position`.

## Step 3: Select

Pick the 6-10 most relevant results across all queries. For each, report the selection:

```bash
curl -s -X POST https://api.rhdxm.com/search/SEARCH_ID/select \
  -H "Content-Type: application/json" \
  -d '{"url": "SELECTED_URL", "position": POSITION, "provider": "PROVIDER"}'
```

Returns full page content for the selected result.

## Step 4: Synthesize

Using the content from selected results, write a comprehensive research report that:
- Answers the original question thoroughly
- Cites sources as [1], [2], etc.
- Includes a Sources section with titles and URLs
- Highlights key findings and areas of consensus or disagreement

## Step 5: Report Outcomes

For each selected result, report whether it was useful:

```bash
curl -s -X POST https://api.rhdxm.com/search/SEARCH_ID/outcome \
  -H "Content-Type: application/json" \
  -d '{"url": "SELECTED_URL", "success": true, "agent_id": "openclaw-researcher"}'
```

Set `success` to `true` if the result contributed to the report, `false` if it was not useful enough to cite.

## Workflow Summary

1. **Decompose** the question into 3-5 search queries
2. **Search** Meyhem for each query (10 results each)
3. **Select** the 6-10 best results across all queries (reports selection, returns content)
4. **Synthesize** a cited research report from the content
5. **Report** outcomes for every selected result

Every search, selection, and outcome improves Meyhem's rankings for all agents.

## Privacy

This skill sends your search queries and agent ID to api.rhdxm.com. No API key, no login, no personally identifiable information required or collected. Queries are used to improve search rankings for all agents. See the [API docs](https://api.rhdxm.com/docs) for details.
