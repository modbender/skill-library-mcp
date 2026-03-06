---
name: resume-cog
description: "7 seconds. That's how long a recruiter spends on your resume. CellCog makes every second count — #1 on DeepResearch Bench (Feb 2026) to research your target role, ATS optimization, and state-of-the-art PDF design. AI resume builder, cover letters, CV, LinkedIn optimization, career documents, portfolio — professional and personalized, not template-stuffed."
metadata:
  openclaw:
    emoji: "📝"
author: CellCog
dependencies: [cellcog]
---

# Resume Cog - AI Resume Builder Powered by CellCog

**7 seconds.** That's how long the average recruiter spends on your resume. CellCog makes every second count.

#1 on DeepResearch Bench (Feb 2026) — CellCog researches your target role, understands what hiring managers look for, optimizes for ATS systems, and generates beautifully designed PDFs that get interviews. Not another template filler — a research-first resume engine.

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**Quick pattern (v1.0+):**
```python
result = client.create_chat(
    prompt="[your resume request]",
    notify_session_key="agent:main:main",
    task_label="resume-task",
    chat_mode="agent"
)
```

---

## What You Can Create

### Resumes & CVs

Build resumes that pass ATS filters and impress humans:

- **Modern Resumes**: "Create a modern, ATS-friendly resume for a senior product manager"
- **Career Change Resumes**: "Build a resume that positions my finance background for a tech PM role"
- **Academic CVs**: "Create a detailed academic CV for a postdoc in computational biology"
- **Executive Resumes**: "Design an executive resume for a VP of Engineering with 15 years experience"
- **Entry-Level Resumes**: "Build a compelling resume for a recent CS graduate with internship experience"

**Example prompt:**
> "Create an ATS-optimized resume for:
> 
> Name: Sarah Chen
> Target Role: Senior Product Manager at a B2B SaaS company
> 
> Experience:
> - Stripe (2021-present): Led payments platform, grew merchant revenue 40%
> - Slack (2018-2021): Launched 3 enterprise features, drove $12M ARR
> - Microsoft (2016-2018): Associate PM on Azure DevOps
> 
> Education: Stanford MBA, UC Berkeley CS
> Skills: Product strategy, data analysis, cross-functional leadership, SQL, A/B testing
> 
> Clean, modern design with blue accents. Highlight metrics and impact."

### Cover Letters

Compelling cover letters that complement your resume:

- **Role-Specific**: "Write a cover letter for the Senior PM position at Notion"
- **Career Change**: "Write a cover letter explaining my transition from consulting to product"
- **Internal Transfer**: "Draft an internal transfer letter for moving from engineering to product"

**Example prompt:**
> "Write a compelling cover letter for:
> 
> Applicant: Sarah Chen (use the resume we just created)
> Target: Senior Product Manager at Notion
> 
> Key angles:
> - My experience building collaboration tools at Slack is directly relevant
> - I'm passionate about Notion's mission of making tools that feel like your own
> - Highlight the payments platform growth at Stripe as evidence of scaling ability
> 
> Tone: Professional but authentic, not corporate-speak."

### LinkedIn Optimization

Optimize your professional presence:

- **Profile Rewrite**: "Rewrite my LinkedIn headline and summary to attract recruiters for ML engineering roles"
- **About Section**: "Create a compelling LinkedIn About section based on my resume"
- **Experience Bullets**: "Transform my resume bullets into LinkedIn-style achievement descriptions"

### Portfolio Documents

Showcase your work:

- **Case Studies**: "Create a product management case study document from my Stripe experience"
- **Design Portfolios**: "Build a portfolio PDF showcasing my top 5 UX projects"
- **Writing Samples**: "Format my blog posts into a professional writing portfolio"

---

## Why CellCog for Resumes?

| Generic Resume Builders | CellCog Resume Cog |
|------------------------|-------------------|
| Pick a template, fill in blanks | Researches your target role first |
| Same advice for everyone | Tailored to specific companies and industries |
| Basic ATS keyword stuffing | Deep understanding of what ATS systems scan for |
| Template designs | State-of-the-art PDF generation, custom every time |
| Text only | Can include charts, visual elements, custom layouts |

---

## Chat Mode for Resumes

| Scenario | Recommended Mode |
|----------|------------------|
| Single resume or cover letter | `"agent"` |
| Complete career package (resume + cover letter + LinkedIn + portfolio) | `"agent"` |
| Career strategy with multiple role-specific resume variants | `"agent team"` |

**Use `"agent"` for most resume work.** It handles individual documents and even multi-document packages excellently.

---

## Tips for Better Resumes

1. **Provide real details**: Don't say "I worked on projects" — give specific metrics, tools, and outcomes. CellCog can't invent your achievements.

2. **Name the target role**: "Resume for a PM" is vague. "Resume targeting Senior PM roles at B2B SaaS companies in fintech" gives CellCog direction.

3. **Include metrics**: Revenue numbers, user counts, percentage improvements — quantifiable results make resumes stand out.

4. **Specify design preferences**: "Modern and minimal", "traditional corporate", "creative with color" — or let CellCog choose based on your industry.

5. **Trust PDF output**: CellCog's PDF generation produces better designs than any Word template.
