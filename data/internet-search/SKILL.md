---
name: internet-search
description: "How to use the internet_search tool effectively — category routing, query formulation, and multi-search strategies. Use whenever web search is needed: current events, research papers, community opinions, or any information beyond training knowledge."
---

# Internet Search

Queries a self-hosted SearXNG instance aggregating multiple search engines.

## Category Routing

Always set `category` based on the nature of the query.

| Category   | When to use                                                         | Engines                                          |
|------------|---------------------------------------------------------------------|--------------------------------------------------|
| `general`  | Default. Facts, how-tos, products, people, broad web.               | Brave, Bing, DDG, Startpage, Qwant, Wikipedia…  |
| `news`     | Recent events, breaking news, anything time-sensitive.              | Bing News, DDG News                              |
| `academic` | Research papers, studies, medical literature, preprints.            | arXiv, Google Scholar, PubMed                    |
| `social`   | Opinions, community recommendations, "what do people think about X".| Reddit                                           |

## Query Formulation

Write queries as a search engine expects — keywords, not full sentences:

```
# Bad
"what is the fastest async runtime for rust"

# Good
"rust async runtime benchmarks 2025"
```

- **news**: include a time anchor — `"OpenAI o3 release 2025"` not just `"OpenAI o3"`
- **academic**: use field terminology — `"transformer attention efficiency survey"`
- **social**: phrase as community search — `"reddit best mechanical keyboard 2025"`

## Count

- `count=5` (default) — sufficient for most tasks
- `count=10` — comparing many options, checking consensus
- `count=3` — quick fact checks

## Multi-Search Strategy

Fire multiple focused searches rather than one broad one:

```
# Bad: one vague search
internet_search("best way to deploy Node.js")

# Good: three targeted searches
internet_search("Node.js Docker deployment best practices 2025")
internet_search("Node.js PM2 vs Docker production", category="social")
internet_search("Node.js zero-downtime deployment strategies")
```

Combine `general` + `social` for factual + sentiment coverage:

```
internet_search("Bun runtime performance vs Node.js benchmarks")
internet_search("Bun runtime production experience", category="social")
```

## When NOT to Use

- Things you already know with high confidence
- Stable API docs or well-known syntax — use training knowledge
- Repeating a search that already answered the question

## Common Mistakes

| Mistake                                   | Fix                                           |
|-------------------------------------------|-----------------------------------------------|
| `general` for a research paper            | Use `category="academic"`                     |
| Searching "what happened today"           | Use `category="news"` with a specific topic   |
| One broad search for a multi-part question| Break into 2–3 focused searches               |
| Repeating a failed search verbatim        | Rephrase with different keywords              |
| `count=20` for a simple fact              | Default `count=5` is almost always enough     |
