---
name: content-engine
description: >
  Full-stack content creation pipeline from research to publication. Analyzes top-ranking competitor
  articles, identifies content gaps, generates SEO-optimized blog posts with brand voice, adds meta
  descriptions and internal link suggestions, formats for WordPress/Ghost/Notion/Hugo/Jekyll, and
  creates platform-specific social media promotion posts for LinkedIn, Twitter/X, and Reddit. Use this
  skill for: blog post writing, article creation, SEO content, keyword research, content gap analysis,
  content strategy, content calendar planning, "write a blog post about X", competitor content analysis,
  "what should I write about next", social media post generation from content, content marketing
  automation, editorial workflow, copywriting, long-form content, content optimization, meta description
  generation, or any request involving researching a topic and producing publish-ready content. Replaces
  manually chaining web research, writing, SEO tools, CMS formatting, and social scheduling into one step.
metadata:
  openclaw:
    emoji: "✍️"
---

# Content Engine

From blank page to published, optimized, and promoted — in one workflow. This skill turns a topic or keyword into a researched, drafted, optimized, and publish-ready piece of content.

## Why This Exists

Content creation with OpenClaw today requires manually chaining 4-5 skills: web research, writing, SEO optimization, CMS formatting, and social scheduling. This skill connects the full pipeline so you go from idea to published post in one flow.

## The Pipeline

Content Engine runs in 5 phases. The user can run the full pipeline or start from any phase.

### Phase 1: Research

When the user provides a topic or target keyword:

1. **Competitor analysis**: Use web_search to find the top 5-10 ranking articles for the target keyword
2. **Structure extraction**: For each competitor article, note:
   - Word count (approximate from snippets)
   - H2/H3 headings and structure
   - Key angles and arguments
   - What's missing or weak
3. **People Also Ask**: Search for "[keyword]" and extract related questions
4. **Content gap identification**: What do all competitors cover? What does nobody cover? The gap is the opportunity.
5. **Research brief output**:

```
📊 Research Brief: [Keyword]

Top competitors (by ranking):
1. [Title] — [URL] — ~[word count] words
   Key angle: [one sentence]
2. ...

Common structure:
- All cover: [topics everyone mentions]
- Gap opportunities: [topics nobody covers well]

People Also Ask:
- [question 1]
- [question 2]
- [question 3]

Recommended angle: [your unique take based on gaps]
Recommended word count: [based on competitor average + 20%]
```

### Phase 2: Draft

Generate a structured first draft using the research brief:

1. **Check for brand voice**: look in OpenClaw memory for stored brand guidelines, tone preferences, or writing style notes. If none exist, ask the user on first run and store for future use.
2. **Outline first**: generate an outline with H2/H3 structure before writing. Show the user and get approval (or auto-proceed if they said "just write it").
3. **Write the draft** following these principles:
   - Open with a hook that addresses the reader's problem directly
   - Use the gap opportunities from research as unique sections
   - Include data points and specific examples (from research)
   - Write for the target keyword naturally — no keyword stuffing
   - End with a clear conclusion and call-to-action
4. **Output**: Markdown file saved to workspace

### Phase 3: Optimize

SEO and readability optimization:

1. **Meta description**: Generate a compelling meta description under 155 characters that includes the target keyword
2. **Title tag**: Optimize the title for search (include keyword, keep under 60 chars, make it compelling)
3. **Internal link suggestions**: if the user has provided a sitemap or list of existing content, suggest internal links. Otherwise, note where internal links could go.
4. **Image alt text**: suggest alt text for any images mentioned or planned
5. **Readability check**:
   - Flag paragraphs longer than 4 sentences
   - Flag sentences longer than 25 words
   - Suggest subheadings every 300 words if missing
   - Check for passive voice overuse
6. **Keyword integration check**: verify the target keyword appears in title, first paragraph, at least one H2, and meta description

Output an optimization report appended to the draft:

```
🔍 SEO Optimization Report

Title tag: [optimized title] ([char count])
Meta description: [meta] ([char count])
Target keyword: [keyword]
  └─ In title: ✅
  └─ In first paragraph: ✅  
  └─ In H2: ✅
  └─ In meta: ✅
Readability: [score/assessment]
Suggested internal links: [list or "provide sitemap for suggestions"]
```

### Phase 4: Format & Publish

Format the content for the user's CMS and prepare for publication:

1. **Detect CMS**: check memory for CMS preference. Common options:
   - **WordPress**: use WordPress skill if available, or output HTML-ready content with featured image suggestions
   - **Ghost**: output in Ghost-compatible Markdown
   - **Notion**: create a Notion page via Notion skill if available
   - **Markdown/Hugo/Jekyll**: output as .md with proper frontmatter
   - **No CMS**: just output clean Markdown

2. **Frontmatter generation** (for static site generators):
   ```yaml
   ---
   title: "[optimized title]"
   description: "[meta description]"
   date: [today]
   tags: [relevant tags]
   categories: [relevant categories]
   ---
   ```

3. **Publish or save**: if CMS integration is available, offer to publish directly. Otherwise, save the final file and tell the user where it is.

### Phase 5: Promote

Generate social media promotion content:

1. **Platform-specific posts**: generate posts optimized for each platform:
   - **LinkedIn**: professional tone, 1-3 paragraphs, relevant hashtags
   - **Twitter/X**: hook + link, under 280 chars, 2-3 hashtags
   - **Reddit**: genuine value-add framing (not promotional), suggest appropriate subreddits
   - **Hacker News**: technical angle, factual title
   
2. **Schedule**: if Mixpost or Buffer skill is available, offer to schedule posts
3. **Email newsletter**: offer to generate a newsletter blurb for the article

Output all promotional content in a single block:

```
📢 Promotion Kit for: [Article Title]

LinkedIn:
[post text]

Twitter/X:
[tweet text]

Reddit (suggested subreddits: r/[sub1], r/[sub2]):
[post text]

Newsletter blurb:
[2-3 sentence summary for email]
```

## Usage Modes

### Full Pipeline
**User**: "Write a blog post about AI agent security best practices"
→ Run all 5 phases sequentially, showing output at each stage

### Research Only
**User**: "Research what's ranking for 'openclaw tutorial'"
→ Run Phase 1 only, output the research brief

### Draft from Research
**User**: "I already researched this topic, here are my notes: [notes]. Write the draft."
→ Skip Phase 1, run Phases 2-5

### Optimize Existing Content
**User**: "Optimize this blog post for SEO" + [attached content]
→ Skip Phases 1-2, run Phases 3-5

### Promote Existing Content
**User**: "Generate social posts for this article: [URL or content]"
→ Skip Phases 1-4, run Phase 5 only

## Content Calendar

If the user asks for a content plan or calendar:

1. Research trending topics in their niche using web_search
2. Cross-reference with their existing content (if known) to avoid duplication
3. Suggest 4-8 topics for the next month with:
   - Target keyword
   - Estimated search volume (use web research clues)
   - Difficulty assessment (how strong is the competition?)
   - Recommended publish date
4. Store the calendar in memory for tracking

## Storing Brand Context

On first use, ask the user about their brand voice and store in memory:

- **Tone**: professional, casual, technical, friendly, authoritative?
- **Audience**: developers, marketers, business owners, general public?
- **Formatting preferences**: short paragraphs? lots of headers? code examples?
- **Things to avoid**: jargon level, competitors not to mention, topics to skip
- **Existing content URL**: for internal linking and avoiding duplication

Once stored, use these preferences for every future content generation without asking again.

## Edge Cases

- **No keyword given**: if the user just says "write about AI agents", help them choose a specific keyword first using research
- **Very competitive keyword**: warn the user and suggest long-tail alternatives
- **Existing content**: if the user's site already has a similar article, flag it and suggest updating instead of creating new
- **Multiple languages**: support content creation in any language the user requests, adjusting SEO practices for that language's search engine norms
- **Short-form content**: for social posts or email copy (not blog posts), skip Phases 1 and 3, go straight to writing + formatting
