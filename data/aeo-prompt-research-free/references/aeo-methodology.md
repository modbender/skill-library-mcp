# AEO Prompt Research Methodology

## What is AEO?

Answer Engine Optimization (AEO) ensures a brand's website gets cited by AI assistants (ChatGPT, Gemini, Perplexity, Claude) when users ask questions in the brand's domain. Unlike SEO (optimizing for search engine rankings), AEO optimizes for being the *source* that AI models reference in their answers.

## Why Prompts, Not Keywords?

People talk to AI differently than they search Google:
- Google: "best crm small business"
- AI: "What's the best CRM for a 10-person startup that needs email integration?"

AEO research discovers these *conversational prompts* — the actual questions people ask AI — and identifies which ones matter for a given brand.

## The Research Process

### Phase 1: Brand Understanding

Crawl the target website to extract:
- **Core offerings** — Products, services, features
- **Target audience** — Who they serve (industry, company size, persona)
- **Value propositions** — What differentiates them
- **Content themes** — What they already write about
- **Competitors** — Who they mention or compete against

Sources: Homepage, about page, product/pricing pages, blog index, meta descriptions.

### Phase 2: Topic Universe Generation

From the brand understanding, generate the *topic universe* — all categories of questions someone might ask an AI that could lead to this brand.

Categories to explore:
1. **Problem-aware prompts** — "How do I solve [problem brand solves]?"
2. **Solution-aware prompts** — "What tools exist for [category]?"
3. **Comparison prompts** — "Compare [brand] vs [competitor]"
4. **Best-of prompts** — "Best [product category] for [use case]"
5. **How-to prompts** — "How to [task brand's product helps with]"
6. **Evaluation prompts** — "Is [brand] good for [specific need]?"
7. **Industry prompts** — "[Industry] trends/best practices"

### Phase 3: Prompt Generation

For each topic category, generate specific prompts a real person would ask an AI assistant. Prompts should be:
- **Natural** — Written how people actually talk to AI
- **Specific** — Include context (company size, industry, use case)
- **Varied** — Cover different intents (research, comparison, how-to, evaluation)
- **Realistic** — Things people actually need answers to

Generate 5-15 prompts per category, then deduplicate and merge similar ones.

### Phase 4: Prioritization

Score each prompt on:
1. **Relevance** (1-5) — How closely does this relate to the brand's core offering?
2. **Volume potential** (1-5) — How likely are many people asking this?
3. **Winability** (1-5) — Can the brand realistically be the best answer?
4. **Intent value** (1-5) — Does this prompt indicate buying/conversion intent?

Priority = (Relevance × 2 + Volume + Winability + Intent) / 5

### Phase 5: Current Coverage Audit

For the top-priority prompts, check:
- Does the brand's website already have content addressing this prompt?
- How well does existing content answer the specific question?
- What gaps exist between the prompt and available content?

Use `site:domain.com [topic]` searches to find existing content.

## Output Format

The final deliverable should include:

```markdown
## AEO Prompt Research: [Brand Name]

### Brand Summary
[2-3 sentence summary of what the brand does and who they serve]

### Priority Prompts

#### Tier 1 (High Priority)
| Prompt | Category | Score | Existing Coverage |
|--------|----------|-------|-------------------|
| "What's the best..." | Best-of | 4.2 | None |

#### Tier 2 (Medium Priority)
[...]

#### Tier 3 (Low Priority / Monitor)
[...]

### Content Gap Analysis
[Which high-priority prompts have no existing content]

### Recommended Next Steps
[Top 3-5 content pieces to create first]
```
