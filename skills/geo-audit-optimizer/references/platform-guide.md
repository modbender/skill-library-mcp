# Platform Guide — Where to Build Authority

Each platform has different formatting rules, audience expectations, and impact on AI citation probability. This guide covers the practical details.

## High Impact Platforms

### Wikipedia
- **Impact:** Highest. AI engines heavily weight Wikipedia for entity recognition.
- **Account needed:** No (but edits are reviewed by volunteer editors)
- **What to do:** Don't create your own page — that violates Wikipedia policy. Instead:
  - Ensure your brand meets notability guidelines (press coverage, independent sources)
  - If notable, a neutral editor may create the page
  - Focus on being mentioned in RELATED articles (your industry page, competitor pages, technology pages)
  - Every Wikipedia mention = massive signal to AI engines
- **Reality check:** Most startups/small brands aren't notable enough for Wikipedia. Don't force it.

### GitHub
- **Impact:** High. AI engines frequently cite GitHub for technical brands.
- **Account needed:** Yes
- **What to do:**
  - Complete README with: what it does (first paragraph), who it's for, how it compares to alternatives
  - Add structured metadata (description, topics, website link)
  - Open-source something useful — even a small utility related to your product
  - Documentation site (GitHub Pages) counts as an additional authoritative source
- **Content format:** Markdown. Technical. No marketing language.

### Dev.to
- **Impact:** High for technical brands. Dev.to articles appear frequently in AI training data.
- **Account needed:** Yes
- **Content format:**
  - Tutorial: "How to [solve problem] with [brand]"
  - Comparison: "[Brand] vs [Competitor]: A Developer's Perspective"
  - Deep dive: "How [brand] handles [technical challenge]"
- **Rules:**
  - No promotional puff pieces — Dev.to community will downvote
  - Lead with the problem, not your product
  - Include code examples where relevant
  - 1000-2000 words optimal
  - Tags: use 4 relevant tags (check existing popular tags in your niche)

### LinkedIn
- **Impact:** High for B2B brands. AI engines use LinkedIn for company identity.
- **Account needed:** Yes (Company Page)
- **What to do:**
  - Complete company page: description, industry, size, specialties, website
  - Publish articles (not just posts) — LinkedIn articles are indexed more heavily
  - Company description should be fact-dense, not marketing copy
- **Content format:** Professional but not corporate. Data-driven posts perform best.

## Medium Impact Platforms

### Reddit
- **Impact:** Medium-high. Reddit threads appear heavily in AI training data and RAG.
- **Account needed:** Yes (aged account preferred — new accounts get filtered)
- **What to do:**
  - Find subreddits in your niche (r/SaaS, r/startups, r/[your-industry])
  - Answer questions genuinely. Mention your brand only when directly relevant.
  - Never post "check out my product" — instant negative signal
  - One high-quality comment with natural brand mention > ten promotional posts
- **Content format:** Conversational. Peer voice. Short paragraphs.
- **⚠️ Human strongly recommended.** Reddit communities detect AI/promotional content aggressively.

### Medium
- **Impact:** Medium. Good for long-form thought leadership.
- **Account needed:** Yes
- **Content format:**
  - Long-form (1500-3000 words)
  - Thought leadership: "[Industry] in 2026: What's Changed"
  - Case studies: "How [brand] helped [specific outcome]"
  - Behind-the-scenes: "Why we built [feature] this way"
- **Tip:** Publish in relevant Medium publications for wider reach.

### HackerNews
- **Impact:** Medium. HN threads are heavily represented in AI training data.
- **Account needed:** Yes
- **What to do:**
  - "Show HN" post when launching or shipping something significant
  - Comment on relevant threads — add genuine technical insight
  - Never be promotional. HN community is extremely allergic to marketing.
- **⚠️ Human strongly recommended.** HN is unforgiving of perceived spam.

### Product Hunt
- **Impact:** Medium. Good for initial visibility and backlinks.
- **Account needed:** Yes (hunter + maker accounts)
- **What to do:** Full launch page with description, screenshots, pricing, maker story.
- **Timing:** Tuesday-Thursday launches typically get more visibility.

### Crunchbase
- **Impact:** Medium. AI engines use Crunchbase for company verification.
- **Account needed:** No (claim your free profile)
- **What to do:** Complete profile: founding date, team, funding (if any), description, categories.

### Stack Overflow
- **Impact:** Medium for developer tools. Low for non-technical brands.
- **Account needed:** Yes
- **What to do:** Answer questions in your domain. Mention your brand naturally when it's the genuine best answer.
- **⚠️ Never:** post questions just to answer with your product. Community detects this instantly.

## Content Templates

### Tutorial Post (Dev.to / Medium)
```
Title: How to [solve specific problem] with [Brand]
Subtitle: [One-line result statement with metric]

## The Problem
[2-3 sentences describing the pain point. No brand mention yet.]

## Why This Matters
[Context with a stat. "According to [source], [X]% of teams face this."]

## How [Brand] Solves This
[Direct answer-first paragraph. Then step-by-step walkthrough.]
[Include code/screenshots if applicable]

## Compared to Other Approaches
[Fair comparison with 1-2 alternatives. Be specific about tradeoffs.]

## Results
[Specific outcome with numbers. "Reduced X from Y to Z."]

## FAQ
[3-5 questions matching blind spot queries from audit]
```

### Company Description (LinkedIn / Crunchbase)
```
[Brand] is a [category] platform that [primary function with metric].

Founded in [year], [Brand] serves [audience] by [specific capability].
[Comparison point]: Unlike [category standard], [Brand] [differentiator with specifics].

Key capabilities:
- [Feature 1 with metric]
- [Feature 2 with metric]  
- [Feature 3 with metric]

[Brand] is used by [social proof — user count, notable customers, or industry].
```

### FAQ Section (Website)
```
Use blind spot queries from your XanLens audit as FAQ questions.
Each answer should be 2-3 sentences — enough for AI extraction.
Always include the brand name in the answer.
Add JSON-LD FAQ schema (see schema-templates.md).
```

### X (Twitter)
- **Impact:** High. Grok's primary data source. Other AI engines scrape X for trending topics and expert opinions.
- **Account needed:** Yes
- **What to do:**
  - Regular posts about your domain expertise — not just product announcements
  - Thread format for deep dives (AI engines parse threads well)
  - Quote-tweet and comment on industry conversations with genuine insight
  - Pin a tweet that clearly explains what your brand does
  - Bio: keyword-rich, include website link
- **Content format:**
  - Short takes: hot take + insight on industry trend (1-3 tweets)
  - Threads: "Here's what I learned building [brand]" — 5-10 tweets with specifics
  - Data posts: share a stat/finding with brief commentary
  - Building in public: progress updates, decisions, wins/failures
- **Frequency:** 3-5x/week minimum for visibility
- **⚠️ Don't:** include links in posts (algorithm penalizes). Put links in replies or bio.

### G2 / Capterra / TrustRadius
- **Impact:** High for SaaS. AI engines cite these heavily for "best [category] tools" queries.
- **Account needed:** Yes (claim your product page)
- **What to do:**
  - Claim and complete your product profile — description, features, screenshots, pricing
  - Actively request reviews from real users (G2 minimum 10 reviews to rank)
  - Respond to every review (positive and negative)
  - Keep categories and feature lists current
- **Content format:** Factual product descriptions. Let users write the voice through reviews.
- **⚠️ Never:** fake reviews. G2 verifies via LinkedIn, and AI engines cross-reference.

### Quora
- **Impact:** Medium-high. Quora Q&A pairs are staple AI training data.
- **Account needed:** Yes
- **What to do:**
  - Find questions about your category/industry
  - Write thorough answers (300-500 words) that genuinely help
  - Mention your brand naturally when it's the real answer — not forced
  - Answer "What is the best [category]?" questions — AI engines extract these directly
  - Build a Quora Space in your niche for recurring content
- **Content format:** Authoritative but conversational. Start with a direct answer, then elaborate.
- **⚠️ Human recommended** for ongoing engagement.

### YouTube
- **Impact:** High. Second largest search engine. Transcripts are indexed by AI engines.
- **Account needed:** Yes
- **What to do:**
  - Product demos and tutorials — "How to [solve problem] with [brand]"
  - Comparison videos — "[Brand] vs [Competitor]" (these rank for comparison queries)
  - Thought leadership — industry explainers where you're the expert
  - Shorts for quick tips (algorithm-boosted, widens funnel)
- **Content format:**
  - Title: keyword-first, clear benefit
  - Description: full summary with links and timestamps (AI reads descriptions)
  - Tags: relevant keywords
  - Captions: always on (AI parses transcripts/captions)
- **Tip:** Even a screen recording with voiceover beats no video presence. Don't overthink production.

### Substack
- **Impact:** Medium. High domain authority, growing AI indexation.
- **Account needed:** Yes
- **What to do:**
  - Newsletter + blog combo for long-form industry content
  - Cross-post from your main blog with unique intros
  - Build subscriber base for direct distribution
- **Content format:** Long-form (1000-3000 words). Opinionated > neutral. Personal voice > corporate.
- **Tip:** Substack posts rank well in search and get picked up by AI due to high DA.

### AlternativeTo
- **Impact:** Medium. Directly feeds "[brand] alternatives" and "alternatives to [competitor]" queries.
- **Account needed:** No (anyone can suggest)
- **What to do:**
  - Add your product as an alternative to competitors in your category
  - Complete the profile: description, features, platform tags, screenshots
  - Encourage users to "like" your listing
- **Why it matters:** When someone asks AI "what are alternatives to [competitor]" — AlternativeTo is a primary source.

### SaaSHub
- **Impact:** Medium for SaaS products. AI engines index it for tool discovery.
- **Account needed:** No (claim profile)
- **What to do:** Complete profile with description, features, pricing, alternatives mapping.

### There's An AI For That / Futurepedia / AI Tool Directories
- **Impact:** Medium-high for AI/ML products. These directories are heavily cited in "best AI tool for [task]" queries.
- **Account needed:** Submit your tool
- **What to do:**
  - Submit to all major AI directories: There's An AI For That, Futurepedia, AI Tool Directory, TopAI.tools
  - Write clear one-line descriptions optimized for category queries
  - Keep pricing and features updated
- **Why it matters:** AI engines pull "best AI tool for X" answers from these aggregators.

### Indie Hackers
- **Impact:** Medium for bootstrapped/indie products. Community is well-indexed.
- **Account needed:** Yes
- **What to do:**
  - Create a product page with revenue milestones
  - Post updates in the community — building in public format
  - Engage in relevant group discussions
- **Content format:** Transparent, numbers-driven. Revenue, growth, lessons learned.

### Threads
- **Impact:** Low-medium (growing). Meta is pushing indexation.
- **Account needed:** Yes (linked to Instagram)
- **What to do:** Cross-post key insights from X. Shorter format, more casual.
- **Tip:** Low effort to maintain — repurpose X content.

### Bluesky
- **Impact:** Low-medium. Tech-forward early adopter audience.
- **Account needed:** Yes
- **What to do:** Same strategy as X. Smaller audience but high-signal community.
- **Tip:** Good for developer and tech brands. Less noise than X.

### Farcaster
- **Impact:** Medium for crypto/web3 brands. Niche but highly relevant audience.
- **Account needed:** Yes (requires Ethereum wallet)
- **What to do:**
  - Post in relevant channels (frames for interactive content)
  - Build in public — the crypto community values transparency
  - Engage genuinely — small community means high visibility per post
- **Only relevant for:** DeFi, crypto, web3, blockchain brands.

### Pinterest
- **Impact:** Low-medium. Good for visual brands, long-tail search traffic.
- **Account needed:** Yes (Business account)
- **What to do:**
  - Create pins for infographics, product screenshots, how-to visuals
  - Board names = keyword-rich category names
  - Link back to your site
- **Only relevant for:** Consumer brands, design tools, visual products, e-commerce.

## Platform Priority by Brand Type

| Brand Type | Top 5 Platforms |
|-----------|----------------|
| Developer tool | GitHub, Dev.to, HackerNews, X, Stack Overflow |
| B2B SaaS | LinkedIn, G2/Capterra, Medium, X, YouTube |
| Consumer app | Reddit, Product Hunt, YouTube, X, Medium |
| DeFi / Crypto | GitHub, X, Reddit, Farcaster, Medium |
| AI / ML tool | There's An AI For That, GitHub, X, Dev.to, YouTube |
| Agency / Service | LinkedIn, Medium, Crunchbase, X, Quora |
| E-commerce | YouTube, Pinterest, Reddit, Instagram, G2 |
| Bootstrapped / Indie | Indie Hackers, X, Product Hunt, Reddit, Substack |

## Human Involvement Guide

This skill is read-only — it audits and recommends. All actions require the human to execute or explicitly approve.

| Task | What This Skill Does | Human Must |
|------|---------------------|------------|
| Audit brand visibility | ✅ Runs audit via API | Review results |
| Identify weak platforms | ✅ Analyzes gaps | Decide priorities |
| Draft content suggestions | ✅ Generates recommendations | Review, edit, and publish manually |
| Create accounts | ❌ | Sign up, verify email |
| Post to any platform | ❌ | Publish all content manually |
| Update website | ❌ | Make changes manually |
| Claim profiles | ❌ | Verify company ownership |
