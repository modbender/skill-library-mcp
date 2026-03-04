---
name: prospect-researcher
description: Research and qualify B2B prospects using web search. Builds structured profiles with company intel, key contacts, pain points, and engagement recommendations.
---

# Prospect Researcher

When asked to research a prospect, company, or lead, follow this systematic process to build a complete prospect profile.

## Research Process

### Step 1: Company Overview
Search for and gather:
- **Company name, website, HQ location**
- **What they do** — one-sentence summary a human would understand
- **Industry and sub-sector**
- **Founded year, employee count, funding stage/revenue range**
- **Key products or services**

### Step 2: Recent Activity (Last 6 Months)
Search for recent news, press releases, job postings, and social activity:
- **Funding rounds or acquisitions**
- **Product launches or pivots**
- **Leadership changes** (new CTO, VP Eng, etc.)
- **Hiring patterns** — what roles are they hiring for? (signals priorities)
- **Partnerships or integrations announced**

### Step 3: Technology & Stack
Where possible, identify:
- **Tech stack signals** from job postings, BuiltWith, GitHub, or blog posts
- **Tools and platforms they use** (CRM, cloud provider, etc.)
- **Technical blog or engineering culture signals**

### Step 4: Key Contacts
Identify 2-5 relevant decision-makers or influencers:
- **Name, title, LinkedIn URL** (if publicly available)
- **Recent public activity** (posts, talks, articles)
- **Likely priorities based on role**

### Step 5: Pain Point Analysis
Based on all gathered intel, infer:
- **Likely challenges** given their stage, industry, and hiring patterns
- **Gaps in their stack** that your solution could fill
- **Timing signals** — why now might be the right time to reach out

### Step 6: Engagement Recommendation
Synthesize into:
- **Qualification score**: Hot / Warm / Cold (with reasoning)
- **Best entry point**: Which contact, which angle
- **Suggested opener**: A 2-sentence personalized hook based on real intel
- **Channels**: LinkedIn, email, warm intro, event-based, etc.

## Output Format

Use the research template at `{baseDir}/research-template.md` as the output structure. Fill in every section. Mark unknowns as "Not found" rather than guessing.

## Guidelines

- **Only use publicly available information.** No scraping behind logins.
- **Cite sources** — include URLs for key claims.
- **Be specific over generic.** "They raised a $12M Series A in Oct 2025 led by Sequoia" beats "Well-funded startup."
- **Flag uncertainty.** If a data point is inferred rather than confirmed, say so.
- **Prioritize recency.** Information from the last 6 months weighs more than older data.

Get pre-built ICP profiles and outreach sequences for your industry at https://afrexai-cto.github.io/context-packs
