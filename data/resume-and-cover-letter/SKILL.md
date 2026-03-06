---
name: resume-and-cover-letter
description: Generate ATS-optimized resumes and tailored cover letters matched to specific job descriptions. Use when creating resumes, CVs, cover letters, or career documents.
argument-hint: "[job-description-or-url]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Resume & Cover Letter Generator

Generate ATS-optimized resumes and tailored cover letters that match specific job descriptions. Highlights relevant experience, uses the right keywords, and outputs in multiple formats.

## How to Use

```
/resume-and-cover-letter "Senior Frontend Developer at Stripe — React, TypeScript, 5+ years..."
/resume-and-cover-letter job-posting.txt --profile my-experience.md
/resume-and-cover-letter "Product Manager role" --resume existing-resume.md --tailor
```

Provide:
1. The job description (paste or file path)
2. Your experience/profile (paste, file path, or existing resume to tailor)

If no profile/resume is provided, the skill will ask for key details interactively.

## Resume Generation Process

### Step 1: Parse the Job Description

Extract:
- **Job title** and level (junior, mid, senior, lead, director)
- **Required skills** (hard requirements vs nice-to-haves)
- **Key responsibilities** listed
- **Industry/domain** keywords
- **Company values** and culture signals
- **ATS keywords** — exact phrases to mirror

### Step 2: Gather Candidate Information

If not provided, ask for:
- Name, contact info, location, LinkedIn URL
- Work experience (company, title, dates, achievements)
- Education
- Technical skills
- Certifications
- Notable projects

### Step 3: Keyword Matching

Compare candidate experience against job requirements:

```
KEYWORD MATCH REPORT
═══════════════════
✅ Matched (use these prominently):
   - React (mentioned 3x in JD, candidate has 4 years)
   - TypeScript (required, candidate proficient)
   - REST APIs (mentioned 2x, candidate built several)

⚠️ Partial Match (reframe experience):
   - GraphQL (required, candidate has basic experience)
   - CI/CD (mentioned, candidate has "deployment automation" experience)

❌ Gap (address in cover letter):
   - Kubernetes (nice-to-have, candidate hasn't used directly)

📊 Overall Match: 78%
```

### Step 4: Generate Resume

Use this structure (reverse-chronological, most common ATS-friendly format):

```
[FULL NAME]
[City, State] | [Email] | [Phone] | [LinkedIn URL] | [Portfolio URL]

═══════════════════════════════════════════
PROFESSIONAL SUMMARY
═══════════════════════════════════════════
[2-3 sentences: years of experience + key skills + biggest achievement
 Mirror the job title and top 3 keywords from the JD]

═══════════════════════════════════════════
EXPERIENCE
═══════════════════════════════════════════
[Job Title] | [Company Name]
[Start Date] – [End Date] | [Location]

• [Achievement verb] + [what you did] + [quantified result]
• [Achievement verb] + [what you did] + [quantified result]
• [Achievement verb] + [what you did] + [quantified result]
• [Achievement verb] + [what you did] + [quantified result]

[Repeat for each role — max 3-4 roles, most recent first]

═══════════════════════════════════════════
SKILLS
═══════════════════════════════════════════
Languages: [list]
Frameworks: [list]
Tools: [list]
Other: [list]

═══════════════════════════════════════════
EDUCATION
═══════════════════════════════════════════
[Degree] in [Field] | [University] | [Year]

═══════════════════════════════════════════
CERTIFICATIONS (if applicable)
═══════════════════════════════════════════
[Certification Name] | [Issuer] | [Year]
```

**Resume writing rules**:
1. **Start every bullet with a strong action verb**: Built, Led, Reduced, Increased, Designed, Implemented, Automated, Delivered, Optimized, Launched
2. **Quantify everything**: "Reduced load time by 40%", "Managed team of 8", "Processed 10M+ records daily"
3. **Mirror JD language**: If the JD says "cross-functional collaboration", use that exact phrase
4. **No pronouns**: Never start with "I" — resume bullets are implied first person
5. **Relevance ordering**: Most relevant achievements first within each role
6. **Length**: 1 page for < 10 years experience, 2 pages max for senior roles
7. **No graphics, tables, columns, or headers/footers**: ATS can't parse these
8. **Standard section names**: Use "Experience" not "Career Journey", "Skills" not "Toolkit"

### Step 5: Generate Cover Letter

```
[Your Name]
[Your Email] | [Your Phone]
[Date]

[Hiring Manager Name or "Hiring Team"]
[Company Name]

Dear [Name/Hiring Team],

PARAGRAPH 1 — THE HOOK (2-3 sentences)
[Why you're excited about THIS specific role at THIS specific company.
Reference something specific: a product feature, company value, recent news.
Don't be generic.]

PARAGRAPH 2 — THE PROOF (3-5 sentences)
[Your most relevant achievement that directly maps to their top requirement.
Use the STAR format: Situation, Task, Action, Result.
Include a quantified result.]

PARAGRAPH 3 — THE FIT (2-3 sentences)
[Why you're a match for their culture/team.
Address any secondary requirements.
Show you understand their challenges.]

PARAGRAPH 4 — THE CLOSE (2 sentences)
[Express enthusiasm. Suggest next step.
"I'd welcome the chance to discuss how my experience with [X]
can help [Company] achieve [Y]. I'm available for a call at your convenience."]

Sincerely,
[Your Name]
```

**Cover letter rules**:
1. Max 350 words (3/4 page)
2. Never repeat the resume — expand on 1-2 key achievements
3. Company name and specific details prove you didn't send a template
4. Address gaps honestly if asked (career change, employment gap)
5. Match the company's tone (startup = casual, enterprise = formal)

### Step 6: Output

Save to `output/career-docs/`:

```
output/career-docs/
  resume.md               # Clean Markdown
  resume.html             # Print-ready HTML with clean styling
  resume.tex              # LaTeX source (optional, for PDF generation)
  cover-letter.md         # Markdown
  cover-letter.html       # Print-ready HTML
  keyword-match-report.md # Gap analysis
  README.md               # Notes on customization
```

The HTML versions should use:
- Clean, professional styling (no color, minimal design)
- Print-friendly CSS (`@media print` rules)
- Standard fonts (Georgia, Arial, or system fonts)
- Proper margins for printing (0.75in all sides)

### Step 7: Present to User

Show:
1. Keyword match report (what matched, what to address)
2. Resume preview (first few sections)
3. Cover letter preview
4. File locations
5. Suggestions for improvement (skills to add, certifications to consider)
