---
name: content-research
description: Research trending topics and generate platform-specific content. Triggers on "research [topic]", "what's new in [topic]", "content for [platform]", "create posts about [topic]". Supports Reddit, X/Twitter, Discord, LinkedIn with multiple content angles per platform.
---

# Content Research

Two-phase workflow: **Research** → **Create**

---

## Phase 1: Research

**Triggers:** `research [topic]`, `what's new in [topic]`

### 1. Search

Use web search to find recent news:
```
web_search(query="[topic] news", freshness="pw")
```

**Query patterns:**
- News: `[topic] news`
- Reddit: `site:reddit.com [topic]`
- X/Twitter: `site:x.com [topic]`

### 2. Fetch Articles

Extract article content:
```
web_fetch(url="[URL]", maxChars=8000)
```

### 3. Filter

- **7-day cutoff** — discard older content
- Skip "what is X" explainers
- Skip price predictions / TA
- Prioritize: launches, partnerships, updates, drama, milestones

### 4. Present

```markdown
## [Topic] Research — [Date]

1. **[Headline]** - [Source] - [X days ago]
   [2-3 sentence summary]
   
2. **[Headline]** - [Source] - [X days ago]
   [2-3 sentence summary]

[up to 5 items, newest first]
```

---

## Phase 2: Content Creation

**Triggers:** `create content for [platform]`, `#3 for reddit`

### Platform Formats

#### Reddit
- Hook title (no clickbait)
- 2-4 conversational paragraphs
- Include source link
- End with discussion prompt

**Angles:**
1. **News share** — Straightforward reporting
2. **Discussion** — "What do you think..."
3. **Analysis** — Your take on implications
4. **ELI5** — Simple explanation
5. **Contrarian** — Devil's advocate

#### X/Twitter
- Under 280 chars (or thread)
- Hook first line
- Line breaks for readability

**Angles:**
1. **Breaking** — Just facts, urgency
2. **Hot take** — Engagement bait opinion
3. **Thread** — Multi-tweet breakdown
4. **Quote dunk** — React to announcement
5. **Meme** — Casual/funny

#### Discord
- Bullet lists (no tables)
- Wrap links: `<https://...>`
- Bold/CAPS for emphasis

**Angles:**
1. **Alert** — One-liner + link
2. **Summary** — Key bullets
3. **Discussion** — Ask for reactions
4. **Thread** — Detailed breakdown
5. **Meme** — Community vibe

#### LinkedIn
- Professional tone
- Lead with insight
- 3-5 short paragraphs
- End with question

**Angles:**
1. **Industry insight** — What it means
2. **Lessons** — What we learn
3. **Prediction** — Where it's heading
4. **Career** — Professional implications
5. **Case study** — Deep dive

---

## Brand Voice (Optional)

For branded content, create a `brand-config.md` file with your voice guidelines:

```markdown
# Brand: [Name]

## Voice
- [Tone descriptor]
- [Communication style]

## Avoid
- [Things not to say]

## Include
- [Required elements]
```

When generating branded content, reference your brand config for consistency.

---

## Example Session

```
User: research defi

Agent: [Returns 5 findings from past 7 days]

User: 2 for reddit

Agent: [5 Reddit angles for finding #2]

User: angle 3

Agent: [Ready-to-post content]
```
