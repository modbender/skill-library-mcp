---
name: docs-cog
description: "Deep reasoning. Accurate data. Beautiful design. The three things every great document needs — and most AI gets wrong. #1 on DeepResearch Bench (Feb 2026), powered by SOTA search models, and state-of-the-art PDF generation. Create resumes, contracts, reports, proposals, invoices, certificates, and any professional document."
metadata:
  openclaw:
    emoji: "📄"
author: CellCog
dependencies: [cellcog]
---

# Docs Cog - Professional Documents Powered by CellCog

**Deep reasoning. Accurate data. Beautiful design.** The three things every great document needs — and most AI gets wrong.

CellCog gets them right: **#1 on DeepResearch Bench (Feb 2026)** for deep reasoning, **SOTA search models** for factually grounded content, and **state-of-the-art PDF generation** that rivals professional design studios. Resumes, contracts, reports, proposals — delivered in minutes, looking like they took days.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**Quick pattern (v1.0+):**
```python
# Fire-and-forget - returns immediately
result = client.create_chat(
    prompt="[your document request]",
    notify_session_key="agent:main:main",
    task_label="document-task",
    chat_mode="agent"  # Agent mode for most documents
)
# Daemon notifies you when complete - do NOT poll
```

---

## PDF is the Default

**All documents are generated as PDF.** No questions asked.

CellCog excels at creating beautiful, professionally formatted documents. PDF captures AI's full creative capability—perfect typography, layouts, and design. If you need DOCX for editing, explicitly request it in your prompt (quality will be lower).

---

## What Documents You Can Create

### Resume & Career Documents

Build your professional story:

- **Resume/CV**: "Create a modern resume for a software engineer with 5 years of experience"
- **Cover Letter**: "Write a compelling cover letter for a product manager position at Google"
- **LinkedIn Summary**: "Create a professional LinkedIn summary that highlights my transition from finance to tech"
- **Portfolio**: "Build a portfolio document showcasing my UX design projects"

**Example prompt:**
> "Create a modern, ATS-friendly resume for:
> 
> Name: Sarah Chen
> Title: Senior Product Manager
> Experience: 7 years in B2B SaaS
> 
> Work history:
> - Stripe (2021-present): Led payments platform, grew revenue 40%
> - Slack (2018-2021): Launched enterprise features
> - Microsoft (2016-2018): Associate PM on Azure
> 
> Education: Stanford MBA, UC Berkeley CS
> 
> Clean, professional design with blue accents."

### Business Documents

Professional business materials:

- **Proposals**: "Create a consulting proposal for a digital transformation project"
- **Invoices**: "Generate an invoice template for my freelance design business"
- **Business Letters**: "Write a formal partnership inquiry letter"
- **Quotes & Estimates**: "Create a detailed quote for website development services"
- **Meeting Minutes**: "Format these meeting notes into professional minutes"

**Example prompt:**
> "Create a business proposal for 'CloudMigrate' consulting services:
> 
> Client: Acme Corp
> Project: AWS cloud migration
> Timeline: 6 months
> Budget: $150,000
> 
> Include: Executive summary, scope of work, timeline, team bios, pricing breakdown, terms.
> 
> Professional, corporate design."

### Reports & Analysis

Data-driven documents:

- **Business Reports**: "Create a quarterly business review report"
- **Research Reports**: "Format my research findings into a professional report"
- **Analysis Documents**: "Create a competitive analysis document"
- **White Papers**: "Build a white paper on AI in healthcare"
- **Case Studies**: "Create a customer case study showcasing ROI"

**Example prompt:**
> "Create a Q4 2025 business report:
> 
> Title: Quarterly Performance Review
> Company: TechStart Inc.
> 
> Key metrics:
> - Revenue: $2.1M (up 35% YoY)
> - Customers: 150 (up from 98)
> - Churn: 5% (down from 8%)
> 
> Include charts and executive summary. Corporate professional style."

### Legal & Finance Documents

Formal agreements and contracts:

- **Contracts**: "Create a freelance services agreement"
- **NDAs**: "Generate a mutual non-disclosure agreement"
- **Terms of Service**: "Draft terms of service for my SaaS app"
- **Privacy Policies**: "Create a GDPR-compliant privacy policy"
- **MOUs**: "Create a memorandum of understanding between two companies"

**Example prompt:**
> "Create a freelance contractor agreement:
> 
> Client: Acme Corp
> Contractor: Jane Smith (Web Developer)
> Project: E-commerce website redesign
> Duration: 3 months
> Payment: $15,000 (50% upfront, 50% on completion)
> 
> Include: Scope, deliverables, payment terms, IP ownership, confidentiality, termination clauses.
> 
> Professional legal formatting."

### Creative & Marketing Documents

Eye-catching marketing materials:

- **Brochures**: "Create a tri-fold brochure for our fitness studio"
- **Flyers**: "Design a promotional flyer for our summer sale"
- **One-Pagers**: "Create a product one-pager for sales team"
- **Media Kits**: "Build a media kit for our startup"
- **Catalogs**: "Create a product catalog with 20 items"

**Example prompt:**
> "Create a product one-pager for 'TaskFlow' project management software:
> 
> Headline: Finally, a PM tool that doesn't suck
> Key features: AI task prioritization, Slack integration, real-time collaboration
> Pricing: $12/user/month
> Call to action: Start free trial
> 
> Modern, bold design. Blue and white color scheme."

### Education & Training Documents

Learning materials:

- **Lesson Plans**: "Create a lesson plan for teaching Python basics"
- **Training Manuals**: "Build an employee onboarding manual"
- **Worksheets**: "Create practice worksheets for algebra"
- **Course Outlines**: "Design a 12-week data science curriculum"
- **Study Guides**: "Create a study guide for AWS certification"

### Events & Planning Documents

Event materials:

- **Invitations**: "Create elegant wedding invitations"
- **Event Programs**: "Design a conference program booklet"
- **Agendas**: "Create a workshop agenda document"
- **Itineraries**: "Build a detailed travel itinerary"
- **Certificates**: "Create achievement certificates for our hackathon"

### Forms & Certificates

Official documents:

- **Certificates**: "Create a course completion certificate"
- **Awards**: "Design employee of the month award"
- **Badges**: "Create digital badges for our training program"
- **Forms**: "Design a customer feedback form"

---

## Chat Mode for Documents

| Scenario | Recommended Mode |
|----------|------------------|
| Standard documents - resumes, invoices, reports, certificates | `"agent"` |
| Complex documents requiring narrative craft - proposals, white papers, case studies | `"agent team"` |

**Use `"agent"` for most documents.** Resumes, contracts, reports, and standard business documents execute well in agent mode.

**Use `"agent team"` for high-stakes documents** where persuasion and narrative flow matter—investor proposals, detailed white papers, compelling case studies.

---

## Tips for Better Documents

1. **Provide the content**: Don't say "write about my experience" - provide actual details, numbers, and facts.

2. **Specify structure**: "Include: Executive summary, problem, solution, timeline, pricing" gives clear direction.

3. **Design preferences**: "Modern and minimal", "Corporate professional", "Bold and colorful" - describe what you want.

4. **Brand elements**: Mention colors, logos (upload them), or reference existing brand guidelines.

5. **Audience context**: "For investors", "For enterprise clients", "For students" changes tone and detail level.

6. **Trust PDF**: It's the default for a reason. Only request DOCX if you truly need to edit the file afterward.
