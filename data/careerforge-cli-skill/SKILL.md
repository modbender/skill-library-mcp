---
name: careerforge-cv-generator
description: AI-powered CV generator for job applications. Sets up automated job search with CareerForge CLI, manages master resume creation, configures filtering criteria (location, keywords, remote/in-person, schedule), and generates tailored CVs on demand. Use when user wants to automate job search, create/update a master resume, configure job filters, or generate CVs for specific job postings.
---

# CareerForge CV Generator Skill

This skill helps users set up and use CareerForge CLI for automated job search and CV generation.

## Overview

CareerForge is an AI-powered CV generator that uses Google's Gemini 2.5 Pro with a Writer+Judge pattern to create tailored, ATS-optimized CVs.

## Prerequisites

### Step 0: Download CareerForge CLI

Before using this skill, download the CLI wrapper from GitHub:

```bash
cd /root/.openclaw/workspace
git clone https://github.com/alon-mini/CareerForge-cli.git careerforge-cli
cd careerforge-cli
npm install
```

**Repository:** https://github.com/alon-mini/CareerForge-cli

## Setup Workflow

### Step 1: Check/Create Master Resume

Check if user has a master resume at `CV_Master/master_resume.md`.

**If no master resume exists:**
Ask the user a series of questions to create one:

1. **Basic Info:**
   - Full name
   - Title/headline
   - Contact info (email, phone, LinkedIn, portfolio)

2. **Professional Summary:**
   - 2-3 sentences describing their professional identity
   - Key differentiators
   - Career focus

3. **Core Competencies:**
   - Top 5-8 skills (technical and soft skills)

4. **Professional Experience:**
   - For each role: Company, title, dates, location
   - 3-4 bullet points per role highlighting achievements
   - Ask for 2-4 most relevant roles

5. **Education:**
   - Degrees, institutions, dates, relevant coursework/thesis

6. **Languages:**
   - Languages and proficiency levels

**Master Resume Format:**
Save as markdown following this structure:
```markdown
# [Name]

## Contact
- Email: 
- Phone: 
- LinkedIn: 
- Portfolio: 

## Summary
[2-3 sentences]

## Core Competencies
- Skill 1
- Skill 2
...

## Professional Experience

### [Company] | [Title]
*[Dates]*

- Bullet 1
- Bullet 2
...

## Education

### [Degree]
*Institution | Dates*

## Languages
- Language (Proficiency)
```

### Step 2: Configure Job Search Filters

Ask user for filtering preferences:

1. **Location:** (e.g., "Tel Aviv, Israel")
2. **Job Title Keywords:** (e.g., "AI, data analyst, product manager")
3. **Experience Level:** (default: 2-4 years)
4. **Remote/In-person/Hybrid:** (default: in-person only)
5. **Exclude Keywords:** (e.g., "senior, lead, sales")
6. **Companies to Exclude:** (reposting companies)

### Step 3: Configure Schedule

Ask user for cron schedule:
- **Hours:** (default: 8-18 Israel time)
- **Days:** (default: Sunday-Thursday)
- **Timezone:** (default: Asia/Jerusalem)

### Step 4: Configure LLM Model

Ask user for API key:
- **Default:** Google Gemini API key
- **Alternative:** Allow user to specify different model

## Daily Workflow

### Job Search Execution

The cron job runs hourly and:
1. Searches for jobs matching filters
2. Sends job listings to user's Telegram group (separate messages)
3. Each message includes: Title, Company, Location, URL, and instructions

### CV Generation

When user replies to a job message with "CV":
1. Extract job details from the message
2. Run CareerForge CLI to generate tailored CV
3. Send CV PDF back to user

## File Structure

```
workspace/
├── CV_Master/
│   └── master_resume.md          # User's master resume
├── careerforge-cli/              # CLI wrapper (from GitHub)
│   ├── generate_cv_from_json.js
│   ├── package.json
│   └── README.md
├── cvs/                          # Generated CVs output
├── job_search.py                 # Job search script
└── careerforge_config.json       # User's filter settings
```

## Commands

### Setup
```bash
# Download CareerForge CLI from GitHub
git clone https://github.com/alon-mini/CareerForge-cli.git careerforge-cli

# Initialize CareerForge
cd careerforge-cli && npm install

# Create master resume
./scripts/create_master_resume.sh
```

### Daily Use
```bash
# Run job search manually
python3 job_search.py

# Generate CV for specific job
node careerforge-cli/generate_cv_from_json.js job.json
```

## References

- [Master Resume Template](references/master_resume_template.md)
- [Job Search Configuration](references/job_search_config.md)
- [CareerForge CLI Usage](references/cli_usage.md)