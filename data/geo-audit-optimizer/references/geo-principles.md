# GEO Principles — Generative Engine Optimization

How to make content that AI engines want to cite.

## Core Concept

AI search engines (ChatGPT, Gemini, Perplexity, Grok) don't work like Google. They don't rank pages — they synthesize answers from their training data and RAG sources. To be cited, your content must be:

1. **Extractable** — AI engines pull chunks (75-300 words). Each chunk must be self-contained.
2. **Authoritative** — Multiple independent sources mentioning your brand increase citation probability.
3. **Structured** — Clear headings, FAQ format, and schema markup make extraction easier.
4. **Factual** — Statistics, comparisons, and specifics beat marketing claims.

## The 7 Rules

### 1. Answer-First Formatting
The first 50 words after any H2 heading must directly answer the implied question. AI engines use RAG — if the chunk doesn't contain both question context AND answer, it gets skipped.

**Bad:**
> "In today's rapidly evolving landscape of project management, teams are increasingly looking for solutions that can keep up with their dynamic workflows..."

**Good:**
> "Acme is a project management platform that handles 10K+ tasks per team with real-time sync across desktop and mobile. It replaces Notion and Asana for teams over 50 people."

### 2. Entity Density
Mention the brand by its full name 4-6 times per page. AI engines build entity graphs — "we" and "our tool" don't register.

- Use full brand name in the first paragraph
- Repeat naturally in H2 headings where relevant
- Use in comparison contexts: "[Brand] vs [Competitor]"
- Include in FAQ answers: "Yes, [Brand] supports..."

### 3. Statistical Anchoring
Include at least 1 data point or statistic per 300 words. Princeton 2025 research showed a 40% increase in LLM citation probability when content includes stats and technical specifics.

Types that work:
- Performance metrics: "processes 10,000 requests/second"
- User numbers: "used by 500+ teams"
- Comparison data: "3x faster than [category average]"
- Research citations: "According to [study], [finding]"

### 4. Quotable Statements
Write sentences that AI engines can extract as standalone facts. These become the snippets that appear in AI answers.

**Quotable:** "Acme reduces project setup time from 2 hours to 15 minutes by auto-generating task structures from meeting transcripts."

**Not quotable:** "Our amazing tool will revolutionize how your team works together."

### 5. Comparison Positioning
AI engines frequently answer "What's the best X?" and "X vs Y" queries. Your content must explicitly position against competitors.

- Include a comparison section or page
- Use natural language: "Unlike [competitor], [brand] does X"
- Be specific: "Acme handles 10x more concurrent users than Notion at the same price point"
- Be fair — AI engines cross-reference, and unfair comparisons get filtered

### 6. FAQ as Citation Bait
FAQ sections with JSON-LD schema are the highest-impact single change for GEO. They:
- Match the exact format AI engines use (question → answer)
- Are explicitly structured for extraction
- Cover long-tail queries that competitors miss

Use blind spot prompts from your XanLens audit as FAQ questions. These are the exact queries where AI engines don't know about you.

### 7. Reduce Friction for AI Crawlers
- Add `/llms.txt` — a markdown summary of your brand for AI crawlers
- Don't block AI crawlers in `robots.txt` (GPTBot, Google-Extended, ClaudeBot, PerplexityBot)
- Use JSON-LD structured data (Organization, Product, FAQ, HowTo)
- Keep critical content in HTML, not behind JavaScript renders or login walls

## 8. Anti-AI Detection Writing Rules

All generated content MUST pass as human-written. AI-detectable content hurts credibility on every platform and can get posts removed or shadow-banned.

### Banned Words (instant AI flag — never use these):
- delve, landscape (figurative), tapestry, multifaceted, nuanced (as filler)
- "it's worth noting", "it's important to note", "let's dive in"
- crucial/crucially, moreover, furthermore, additionally
- leverage/leveraging (non-financial), utilize/utilization
- foster, realm, facilitate, comprehensive, robust
- "in conclusion", "to summarize", "in summary"
- "hope this helps", "happy to help", "feel free to ask"
- "great question!", "that's a fantastic point"
- culminate, underscore, paradigm, synergy, holistic

### Formatting Rules:
- **No em dashes (—)** — use commas, periods, or "and" instead
- **Double line breaks** between thoughts (not walls of text)
- **Use contractions** — "don't" not "do not", "it's" not "it is"
- **Vary sentence length** — mix short punchy (3-5 words) with longer ones
- **No hedging chains** — "it might potentially be somewhat useful" → "it's useful"

### Tone Rules:
- Have opinions. Don't be perfectly balanced on everything — humans have biases
- Be specific, not generic. "I've used 4 of these and Raycast is the only good one" beats "there are many great options available"
- Start sentences with "But", "And", "Like", "Honestly" sometimes
- No greetings at the start, no "hope this helps" at the end
- Reference real experience where possible

### Self-Check Before Any Content:
- [ ] No banned words from the list?
- [ ] No em dashes?
- [ ] Contractions used throughout?
- [ ] Sentence lengths actually vary?
- [ ] At least one opinion that isn't perfectly balanced?
- [ ] Would a real person say this out loud?
- [ ] Specific details instead of vague generalities?

## What Doesn't Work

- **Keyword stuffing** — AI engines understand semantics, not keyword frequency
- **Thin content** — 200-word pages don't have enough for meaningful chunk extraction
- **Marketing fluff** — "revolutionary", "cutting-edge", "best-in-class" — AI engines ignore superlatives without evidence
- **Duplicate content across platforms** — AI engines deduplicate. Each piece must be unique.
- **Fake reviews or planted testimonials** — AI engines cross-reference multiple sources

## Measuring Impact

The only reliable way to measure GEO impact is to test with real AI engines. Run a XanLens audit before making changes, implement fixes, wait 7-14 days, then re-audit. Compare:

- Overall score change
- Per-engine improvements (some engines update faster than others)
- Blind spots resolved vs new blind spots
- Category scores (discovery queries matter most)

Generic content scoring rubrics (readability scores, keyword density) do NOT predict AI citation probability. Only testing against real engines does.
