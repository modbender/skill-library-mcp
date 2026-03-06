---
name: arena-research
description: >
  General-purpose Are.na research agent. Searches Are.na for curated collections,
  references, visual inspiration, and linked resources across any topic. Explores the
  connection graph between channels to discover adjacent ideas and key curators.
  Use when: (1) user says "arena research", "search arena for", "search are.na for",
  "what's on arena about", "find arena channels about", "who's curating [topic]",
  "explore arena for", "/arena-research", (2) user is working on something where
  curated human-collected references would be valuable (design research, cultural
  analysis, art direction, conceptual exploration, reading lists, visual references),
  (3) user wants to discover how people organize ideas around a topic — the channel
  structure IS the insight. NOT for: posting content, account management, or
  real-time/breaking news (use x-research for that).
---

# Arena Research

General-purpose agentic research over Are.na. Decompose any research question into
targeted searches, explore channels, follow the connection graph to discover adjacent
ideas, identify key curators, deep-dive linked content, and synthesize into a sourced
briefing.

For API details (endpoints, auth, response format): read `references/arena-api.md`.

## When to Use Arena vs Other Sources

- **Are.na** — curated references, visual research, design thinking, cultural analysis,
  reading lists, how people organize ideas. High signal, human-curated, long-tail.
- **X/Twitter** (x-research) — real-time reactions, dev discourse, product launches,
  breaking news, expert hot takes. Fast-moving, high volume.
- **Web search** — factual answers, documentation, current events, specific URLs.

Are.na is a library, not a firehose. The value isn't just what people saved — it's
*how they organized it* and *what else they connected it to*.

## CLI Tool

All commands run from this skill directory:

```bash
cd ~/clawd/skills/arena-research
source ~/.config/env/global.env
```

### Search

```bash
bun run arena-search.ts search "<query>" [options]
```

**Options:**
- `--type Channel|Block|Text|Image|Link|User|Group` — filter result type (default: all)
- `--sort score|created|updated|connections|random` — sort order (default: score)
- `--scope all|my|following` — search scope (default: all, `my`/`following` require auth)
- `--per N` — results per page (default: 24, max: 100)
- `--page N` — page number
- `--quick` — quick mode: 10 results, 1hr cache, channels only, sort by connections
- `--save` — save to `~/clawd/drafts/arena-research-{slug}-{date}.md`
- `--json` — raw JSON output
- `--markdown` — formatted markdown output

**Examples:**
```bash
bun run arena-search.ts search "tools for thought" --type Channel --sort connections
bun run arena-search.ts search "brutalist web design" --quick
bun run arena-search.ts search "cybernetics" --type Link --per 50
bun run arena-search.ts search "spatial computing" --scope my
```

### Channel

```bash
bun run arena-search.ts channel <slug-or-id> [options]
```

**Options:**
- `--sort position|created|updated` — content sort (default: position)
- `--type Text|Image|Link|Attachment|Embed|Channel` — filter content type
- `--per N` / `--page N` — pagination
- `--connections` — show channels that share blocks with this one (graph traversal)
- `--save` / `--json` / `--markdown`

**Examples:**
```bash
bun run arena-search.ts channel arena-influences
bun run arena-search.ts channel arena-influences --type Link --per 50
bun run arena-search.ts channel arena-influences --connections
```

### Block

```bash
bun run arena-search.ts block <id> [options]
```

**Options:**
- `--connections` — show which channels this block appears in (graph traversal)
- `--json`

**Examples:**
```bash
bun run arena-search.ts block 3235876
bun run arena-search.ts block 3235876 --connections
```

### User

```bash
bun run arena-search.ts user <slug-or-id> [options]
```

**Options:**
- `--per N` / `--page N`
- `--json`

### Me

```bash
bun run arena-search.ts me
```

Shows authenticated user's profile and channels. Requires `ARENA_ACCESS_TOKEN`.

### Cache

```bash
bun run arena-search.ts cache clear
```

## Research Loop (Agentic)

When doing deep research (not just a quick search), follow this loop:

### 1. Decompose the Question into Search Strategies

Turn the research question into 3-5 search queries approaching the topic from
different angles.

Think about the topic at multiple levels of abstraction:
- **Direct terms**: The obvious keywords (`spatial computing`, `brutalist web design`)
- **Adjacent concepts**: Related fields (`haptic interfaces`, `concrete architecture`)
- **Practitioner language**: How Are.na users actually name things (`tools for thought`,
  `digital gardens`, `vernacular web`)
- **Broader category**: The umbrella topic (`interaction design`, `web aesthetics`)
- **Specific references**: Known works, people, or projects in the space

Start with channels sorted by connections to find the most-connected collections first:

```bash
bun run arena-search.ts search "tools for thought" --type Channel --sort connections --per 20
```

### 2. Search and Assess Channels

Run each query. After each search, assess:
- **Which channels have real depth?** Look at item counts in results. Channels with
  2-3 items are stubs. Channels with 50+ items are serious collections.
- **Who owns them?** If the same user or group appears across multiple relevant channels,
  they're a key curator worth exploring directly.
- **Are there channels I should explore in full?** Pick the top 3-5 by content count
  and relevance.

Also search for blocks directly to find specific linked content:

```bash
bun run arena-search.ts search "cybernetics" --type Link --sort connections --per 20
```

### 3. Explore Top Channels

For each promising channel, fetch its contents:

```bash
bun run arena-search.ts channel tools-for-thought --per 50
```

To see only external links (the most valuable for research deep-dives):

```bash
bun run arena-search.ts channel tools-for-thought --type Link --per 50
```

Look for:
- **Link blocks** with source URLs — these are external references worth deep-diving
- **Text blocks** with content — these are notes, annotations, and original writing
- **Image blocks** — note titles and descriptions, deprioritize for text-based research
- **Nested channels** (type: Channel) — sub-collections worth exploring

### 4. Follow the Connection Graph

This is what makes Are.na research uniquely powerful. Two strategies:

**4a. Block connections — "Where else does this content live?"**

For high-signal blocks (interesting links, well-described text), check which other
channels they appear in:

```bash
bun run arena-search.ts block 3235876 --connections
```

A block in 28 channels means 28 different people thought it was worth saving. The
channels it appears in show you how different people contextualize the same idea.

**4b. Channel connections — "What's adjacent to this collection?"**

For a channel you've identified as high-quality, find other channels that share content:

```bash
bun run arena-search.ts channel arena-influences --connections
```

This surfaces *conceptual neighbors* — channels that share blocks with the one you're
exploring. A channel about "tools for thought" might connect to "cybernetics," "memory
palaces," and "personal knowledge management."

**Graph depth:** One hop is the sweet spot. Block→connections→those channels is enough.
Two hops gets exponential fast. Stop at one hop unless you have a specific reason to
go deeper.

### 5. Identify Key Curators

As you explore, track which users appear repeatedly:
- Same user owns multiple relevant channels
- Same user connected blocks to several channels you've explored
- Users with high follower counts in the space

Fetch their profile and channels:

```bash
bun run arena-search.ts user charles-broskoski
```

### 6. Deep-Dive Linked Content

When blocks are Link-type and have source URLs, use `web_fetch` to read the actual
content. Prioritize links that:
- Appear in many channels (high connection count from step 4a)
- Come from channels with many items or followers
- Point to essays, blog posts, GitHub repos, research papers, or documentation
- Are directly relevant to the research question

Skip deep-diving:
- Social media posts (use x-research)
- Image galleries or portfolios
- Paywalled content
- Dead links (check the `state` field — `available` means it's live)

### 7. Search Your Own Collections

If looking for something you've personally saved:

```bash
bun run arena-search.ts search "query" --scope my
```

Or content from people you follow:

```bash
bun run arena-search.ts search "query" --scope following
```

### 8. Synthesize

Group findings by **theme**, not by search query. Each theme should capture a
conceptual cluster of channels, blocks, and curators.

```markdown
### [Theme/Finding Title]

[1-2 sentence summary of what curators are collecting and how they frame it]

**Key channels:**
- [Channel Title](https://www.are.na/owner/slug) by @username — N items
  [Brief description of scope and quality]
- [Channel Title](https://www.are.na/owner/slug) by @username — N items
  [Brief description]

**Notable content:**
- [Block title](source_url) — found in N channels
  [Why it's significant]

**Key curators:**
- [@username](https://www.are.na/slug) — N channels, N followers
  [What they focus on]

**Connected territory:**
- [Adjacent channel](https://www.are.na/owner/slug) — overlaps via shared blocks
  [What this connection reveals about the topic]
```

### 9. Save

Use `--save` flag or save manually to `~/clawd/drafts/arena-research-{topic-slug}-{YYYY-MM-DD}.md`.

Include a metadata footer:

```markdown
---
## Research Metadata
- **Query**: [original question]
- **Date**: YYYY-MM-DD
- **Source**: Are.na v3 API
- **API calls**: N search queries + N channel fetches + N block connection lookups + N deep-dives
- **Channels explored**: N
- **Blocks scanned**: ~N
- **Search terms used**: [list the actual search strings]
- **Limitations**: [any gaps]
```

## Refinement Heuristics

- **Too many shallow channels?** Filter for items > 10 in results
- **Too few results?** Broaden keywords, try synonyms, drop `--type` filter
- **Want the most-saved content?** Search blocks with `--sort connections`
- **Looking for specific link types?** Use `--type Link` for external references, `--type Text` for notes
- **Channel too large to browse?** Use `--type` and `--sort` on the channel command
- **Want to spider outward?** Pick 3 blocks with most connections, fetch their connections, see what emerges
- **Stuck?** Search for a known reference or thinker, find their channels, explore from there
- **Visual research?** Use `--type Image` — Are.na is heavily used for mood boards and art direction

## Content Types Quick Reference

| Block Type | Key Fields | Research Value |
|-----------|-----------|---------------|
| `Link` | `source.url`, `source.title`, `description` | External references — deep-dive with web_fetch |
| `Text` | `content` (markdown) | Notes, annotations, original writing |
| `Image` | `image.src`, `title`, `description` | Visual references — note title/description |
| `Attachment` | `attachment.url`, `title` | PDFs, documents — may be valuable |
| `Embed` | `embed.url`, `title` | Videos, audio — note but usually can't deep-dive |
| `Channel` | nested channel in contents | Sub-collection — explore if relevant |

## File Structure

```
skills/arena-research/
├── SKILL.md              (this file)
├── arena-search.ts       (CLI entry point)
├── lib/
│   ├── api.ts            (Are.na v3 API wrapper: search, channels, blocks, users)
│   ├── cache.ts          (file-based cache, 15min TTL)
│   └── format.ts         (terminal + markdown formatters)
├── data/
│   └── cache/            (auto-managed)
└── references/
    └── arena-api.md      (Are.na v3 API endpoint reference)
```
