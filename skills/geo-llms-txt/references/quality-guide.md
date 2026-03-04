# llms.txt Quality Guide

## The Factual Tone Rule

AI systems prefer factual, informational content over marketing language.

### ❌ Bad (Promotional)
```
Revolutionary AI-powered platform that transforms your workflow
with cutting-edge technology and unmatched performance.
```

### ✅ Good (Factual)
```
Cloud-based project management tool with task tracking, team collaboration
features, and automated reporting. Supports 10,000+ concurrent users.
```

## Entity-Rich Descriptions

Include specific entities that help AI understand context:

| Instead of... | Use... |
|---------------|--------|
| "Our API" | "REST API with JSON responses, rate limited to 1000 requests/hour" |
| "Integration guide" | "Guide for connecting Salesforce CRM via OAuth 2.0" |
| "Pricing info" | "SaaS pricing: Starter $29/mo, Pro $99/mo, Enterprise custom" |
| "Tutorial" | "Tutorial: Building a React component with TypeScript and Tailwind" |

## Description Formula

For page descriptions, use this structure:

```
[Content Type]: [Topic/Subject] + [Key Detail] + [Target Audience/Use Case]
```

**Examples:**
- "Guide: Setting up PostgreSQL replication for high-availability systems"
- "Reference: Python datetime format codes with timezone handling examples"
- "Case study: How Acme Corp reduced deployment time by 60% using our CI/CD tool"

## Common Mistakes

### 1. Dumping the Sitemap

❌ **Wrong:**
```markdown
## All Pages
- [Page 1](...): ...
- [Page 2](...): ...
(500 more pages...)
```

✅ **Right:**
```markdown
## Top Resources
- [Getting Started Guide](...): ...
- [API Reference](...): ...
- [Architecture Overview](...): ...
(15-40 carefully selected pages)
```

### 2. Using URLs as Link Text

❌ **Wrong:**
```markdown
- [example.com/products/ai-tool](...): ...
```

✅ **Right:**
```markdown
- [AI Writing Assistant](...): ...
```

### 3. Vague Descriptions

❌ **Wrong:**
```markdown
- [Products](...): Information about our products
```

✅ **Right:**
```markdown
- [AI Writing Assistant](...): Browser extension for grammar checking and style suggestions in Google Docs
```

### 4. Duplicate Content

Don't list both:
- `/blog/post-slug`
- `/blog/post-slug/?utm_source=newsletter`

Use canonical URLs only.

### 5. Missing Brand Context

❌ **Wrong:**
```markdown
# Acme Inc

## Products
...
```

✅ **Right:**
```markdown
# Acme Inc

> API-first payment processing platform for SaaS companies

Acme provides developer-friendly payment infrastructure with 
pre-built components for subscription billing, invoicing, and 
revenue recognition. Used by 10,000+ companies including Stripe,
Notion, and Linear.

## Products
...
```

## Section Organization

Order matters — put most important sections first:

1. **Key Pages** — Homepage, about, core offerings
2. **Products/Features** — What you sell
3. **Documentation** — How to use it
4. **Resources** — Blog, guides, case studies
5. **Company** — About, careers, contact

## Writing for AI Comprehension

### Use Clear Hierarchy
```markdown
# Main Topic
## Subtopic
### Specific Point
```

### Include Context
Don't assume the AI knows your industry:

❌ "Implement the flux capacitor pattern"
✅ "Implement flux capacitor caching: store computed values to avoid recalculating expensive operations"

### Define Acronyms
First use: "Customer Relationship Management (CRM)"
Then: "CRM"

### Use Active Voice
❌ "The API is used by developers to..."
✅ "Developers use the API to..."

## Validation Checklist

Before publishing your llms.txt:

- [ ] Brand description is one clear sentence
- [ ] Overview paragraphs are factual (2-3 max)
- [ ] All links work (HTTP 200)
- [ ] No duplicate URLs
- [ ] 15-40 total links
- [ ] Each section has 2-8 links
- [ ] Descriptions are specific and under 15 words
- [ ] No promotional language ("best", "revolutionary", etc.)
- [ ] File is valid markdown
- [ ] Placed at `/llms.txt` on domain root

## Examples by Industry

### SaaS
```markdown
# ProjectFlow

> Project management software for software development teams

ProjectFlow provides Kanban boards, sprint planning, and code 
integration for agile teams. Integrates with GitHub, GitLab, 
and Bitbucket. Used by 50,000+ developers at companies like 
Shopify, GitHub, and Vercel.

## Key Pages

- [Features](...): Kanban, sprints, burndown charts, and team velocity tracking
- [Pricing](...): Free for 5 users, $8/user/mo for teams, $15/user/mo for enterprise
- [Security](...): SOC 2 Type II certified, GDPR compliant, data encryption at rest
```

### E-commerce
```markdown
# GearUp Outdoor

> Direct-to-consumer outdoor gear and apparel retailer

GearUp sells hiking, camping, and climbing equipment. 
Specializes in sustainable materials and fair-trade manufacturing.
Free shipping on orders over $50. 365-day return policy.

## Key Pages

- [Best Sellers](...): Top-rated tents, sleeping bags, and backpacks
- [Sustainability](...): Materials sourcing, carbon-neutral shipping, recycling program
- [Size Guide](...): Measurements and fit recommendations for all apparel
```

### Publisher
```markdown
# TechDeep Dive

> Independent publication covering AI infrastructure and developer tools

TechDeep Dive publishes in-depth analysis of machine learning 
frameworks, MLOps platforms, and AI engineering practices. 
Founded 2019 by former Google ML engineers. 500K monthly readers.

## Key Categories

- [MLOps](...): Guides on model deployment, monitoring, and scaling
- [LLM Engineering](...): Working with GPT-4, Claude, and open-source models
- [Case Studies](...): How companies like Netflix and Airbnb build ML systems
```