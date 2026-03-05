---
name: job-hunter
description: Comprehensive job search assistant for finding, evaluating, and applying to job opportunities. Use when a user needs help with job hunting, job searching, finding openings, evaluating job fit, preparing applications, writing cover letters, interview preparation, salary research, or tracking applications. Supports multi-source job search across LinkedIn, Indeed, Glassdoor, and more with automated fit scoring against a candidate profile.
---

# Job Hunter

End-to-end job search assistant — from finding opportunities to landing interviews.

## Quick Start

### 1. Set up candidate profile

Create a profile JSON for the user. Use the template at `{baseDir}/references/profile-template.json` as a starting point. Ask the user about:
- Target roles and seniority level
- Key skills and tools
- Location preferences (cities + remote)
- Salary expectations
- Dealbreakers and excluded companies
- Preferred industries/domains

Save as `profile.json` in the workspace.

### 2. Search for jobs

Use the `web_search` tool with multiple queries to cast a wide net:

```
site:linkedin.com/jobs "[role]" "[city]"
site:indeed.com "[role]" "[city]"  
site:glassdoor.com/job "[role]" "[city]"
"[role]" "[city]" hiring 2025 2026
```

Expand keywords — don't just search one title. See `{baseDir}/references/search-strategies.md` for keyword expansion patterns.

Alternative: run the search script if Brave API is available:
```bash
{baseDir}/scripts/search_jobs.sh "CX Manager" --location "Amsterdam" --days 7
```

### 3. Evaluate fit

For each job found, run fit analysis:
```bash
python3 {baseDir}/scripts/analyze_fit.py --profile profile.json --jobs jobs.json --threshold 50
```

Or evaluate manually using this framework:
- **Skill match** (40%): Does user have 60%+ of required skills?
- **Seniority match** (25%): Right level — not over/under qualified?
- **Location match** (15%): Compatible location or remote?
- **Domain match** (10%): Preferred industry/domain?
- **Red flags** (10%): Excluded companies? Dealbreakers?

Score: 🟢 75+ great | 🟡 55-74 good | 🟠 40-54 stretch | 🔴 <40 skip

### 4. Present results

For each job, present:
- **Role & Company** with direct link
- **Fit score** with color indicator
- **Why it's a match** (top 3 skill matches)
- **Gaps to address** (missing skills to highlight as "eager to learn")
- **Salary estimate** if available
- **Recommendation**: Apply / Maybe / Skip

## Application Support

### Cover letters
Read `{baseDir}/references/cover-letter-guide.md` for structure and tone guidelines. Generate tailored cover letters that:
- Reference specific company details (not generic)
- Map user's experience to top 2-3 job requirements
- Include quantified achievements
- Stay under 350 words

### Interview prep
Read `{baseDir}/references/interview-prep.md` for complete preparation framework. Help with:
- Company research summaries
- STAR stories for key requirements
- Tailored "tell me about yourself" script
- Salary negotiation talking points
- Questions to ask the interviewer

### Salary research
```bash
bash {baseDir}/scripts/salary_research.sh "Job Title" "Location"
```
Cross-reference 3+ sources. In the Netherlands: factor in 8% holiday allowance, possible 13th month, pension.

## Daily Brief Format

When running as a scheduled job search brief:

1. **New opportunities** — jobs found in last 24h with fit scores and direct links
2. **Application status** — updates on pending applications
3. **Action items** — what to apply to today, follow-ups due
4. **Market intel** — industry trends, salary movements, hiring patterns

## Tracking

Maintain a job tracker with:
- Company, role, date found, source URL
- Fit score and recommendation
- Status: `new` → `applied` → `screening` → `interview` → `offer`/`rejected`/`ghosted`
- Applied/skipped with reason
- Contact info and follow-up dates

## Tips for Agents

- **Never apply on behalf of the user** — present opportunities, let them decide
- **Don't overwhelm** — 3-5 quality matches beat 20 mediocre ones
- **Track excluded companies** — never suggest the same company twice after rejection
- **Be honest about fit** — stretches are okay to flag, but don't oversell poor matches
- **Respect dealbreakers** — if user said no customer service, don't suggest it even if "it's a great company"
- **Update the profile** — as you learn user preferences, refine the profile
- **Celebrate wins** — applied to a job? Got an interview? Acknowledge it
