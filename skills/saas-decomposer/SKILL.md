---
name: saas-decomposer
description: "Web SaaS service decomposition and AI internalization development plan generation. Analyze existing SaaS to identify functions replaceable by AI agents and establish skill-based internalization roadmap. Triggered by 'SaaS analysis', 'service decomposition', 'internalization', 'decompose', 'SaaS replacement', 'build this service with AI', etc."
author: 무펭이 🐧
---

# saas-decomposer

> **SaaS → AIaaS Conversion Analysis Engine**  
> Decomposes existing SaaS services and identifies areas replaceable by AI agent skills to establish internalization roadmap.

## Core Concept: SaaS → AIaaS Conversion Analysis

Mupengism's core vision: **"End of SaaS → AIaaS"**

- The entire $200B SaaS market is flipping
- From selling software era to **installing AI labor era**
- Analyze which parts of existing SaaS functions can be replaced by AI agent skills

---

## Features

### 1. SaaS Service Decomposition (Decompose)

**Input**: SaaS service URL or name

**Process**:
1. Crawl service landing/feature pages with `web_fetch`
2. Extract core function list
3. Decompose each function into atomic tasks
4. Assign AI replaceability score (1-5)
5. Map coverage by existing Mupeng skills

**Output Format**:
```
## [Service Name] Decomposition Results

### Function List
- Function A (AI replacement: ⭐⭐⭐⭐⭐) → Existing skill: copywriting
- Function B (AI replacement: ⭐⭐⭐) → New skill needed
- Function C (AI replacement: ⭐) → Infrastructure development needed

### AI Replacement Rate: 70%
### New Skills Needed: 3
### Estimated Development Time: 2 weeks
```

---

### 2. Internalization Plan

Generate development roadmap based on decomposition results:

- Skill development priority (highest replacement effect first)
- Map existing skill reuse
- Auto-generate new skill spec drafts
- **Cost comparison**: SaaS subscription vs self-skill operation

**Example**:
```
### Internalization Roadmap

#### Phase 1: Quick Wins (1 week)
- [Use existing skill] Automate email templates with copywriting
- [Use existing skill] Automate customer responses with auto-reply

#### Phase 2: New Skill Development (2 weeks)
- lead-scorer: Lead scoring algorithm
- campaign-optimizer: A/B test automation

#### Phase 3: Infrastructure (4 weeks)
- Build data pipeline
- Real-time sync system

### Cost Comparison
- HubSpot Pro: $800/mo → Mupeng skillpack: $120/mo (85% savings)
```

---

### 3. Competitive SaaS Comparative Analysis

Simultaneous decomposition of 3-5 SaaS in same category:

- Function cross-comparison table
- AI replacement area overlap analysis
- **"What % of these SaaS can our skillpack replace"** calculation

**Example**:
```
### Marketing SaaS Comparison

| Function | HubSpot | Mailchimp | ActiveCampaign | Mupeng Replacement |
|----------|---------|-----------|----------------|-------------------|
| Email automation | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ auto-reply |
| Lead scoring | ✅ | ❌ | ✅ | ⭐⭐⭐ (new skill) |
| A/B testing | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ copywriting |
| CRM integration | ✅ | ⚠️ | ✅ | ⭐⭐ (infrastructure needed) |

**Overall Replacement Rate**: 65%
```

---

### 4. Industry-specific SaaS → AIaaS Conversion Templates

Pre-defined industry-specific SaaS decomposition patterns:

#### Marketing
- **SaaS**: HubSpot, Mailchimp
- **Mupeng replacement**: `auto-reply` + `copywriting` + `mail` + `seo-content-planner`

#### Project Management
- **SaaS**: Notion, Jira
- **Mupeng replacement**: `decision-log` + `daily-report` + `git-auto`

#### Customer Management
- **SaaS**: Salesforce, Zendesk
- **Mupeng replacement**: `auto-reply` + `notification-hub` + `data-scraper`

#### Accounting
- **SaaS**: QuickBooks
- **Mupeng replacement**: `invoice-gen` + `tokenmeter`(cost tracking)

#### Content
- **SaaS**: Canva, Buffer
- **Mupeng replacement**: `cardnews` + `social-publisher` + `content-recycler`

#### Student Council (AssoAI Model)
- **SaaS**: EveryTime + Notion + CampusGroups
- **Mupeng replacement**: Ref → `memory/2026-02-09-insight-university-saas.md`

---

## Analysis Framework

```
1. Crawl      — Collect service functions (web_fetch + data-scraper)
2. Decompose  — Break into atomic tasks
3. Score      — AI replaceability score (1-5)
4. Map        — Map to existing Mupeng skills
5. Gap        — Identify missing skills
6. Plan       — Generate development roadmap
7. Compare    — Cost comparison (SaaS vs AIaaS)
```

---

## Usage Examples

### Basic Decomposition
```
User: "Decompose HubSpot"
→ Execute Crawl + Decompose + Score + Map
→ Output decomposition results report
```

### Internalization Plan Generation
```
User: "What do I need to replace Notion with AI?"
→ Execute Decompose + Internalize
→ Output roadmap + cost comparison
```

### Competitive Analysis
```
User: "Compare marketing SaaS"
→ Simultaneously analyze HubSpot, Mailchimp, ActiveCampaign
→ Cross-comparison table + replacement rate calculation
```

---

## Event Bus

### Generated Events
- `events/saas-analysis-YYYY-MM-DD.json` (when analysis complete)

### Consumers
- `business-planner`: Use analysis results in business plans

---

## Reference Files

Memory to reference during analysis:

- `memory/2026-02-09-insight-university-saas.md` — University SaaS market analysis (CampusGroups, EveryTime)
- `memory/2026-02-09-assoai-pitchdeck.md` — AssoAI (Student Council SaaS → AI automation)
- `memory/consolidated/doyak-business-plan.md` — "Reduce SaaS licenses 50%, replace with AI" (Publicis Sapient)
- `memory/research/absorb-frameworks.md` — Framework analysis (MetaGPT, OpenHands, etc.)
- `SOUL.md` — Mupengism vision: "The entire $200B SaaS market is flipping"

---

## AI Replaceability Score Criteria

| Score | Meaning | Examples |
|-------|---------|----------|
| ⭐⭐⭐⭐⭐ | Immediately replaceable (use existing skills) | Auto email response, content generation |
| ⭐⭐⭐⭐ | Replaceable with lightweight skill development (1-2 weeks) | Lead scoring, A/B testing |
| ⭐⭐⭐ | Medium development needed (2-4 weeks) | Workflow engine, dashboard |
| ⭐⭐ | Infrastructure development needed (1-2 months) | Real-time sync, data pipeline |
| ⭐ | Long-term R&D needed (3+ months) | Advanced ML models, complex integrations |

---

## Troubleshooting

### When web_fetch Fails
- Take snapshot with browser tool and analyze
- Prioritize crawling public docs (help center, pricing page)

### When Competitor Info Insufficient
- Reference industry templates first
- Utilize similar category SaaS patterns

### When Cost Comparison Data Missing
- Crawl pricing pages
- Estimate industry average subscription fees

---

🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
