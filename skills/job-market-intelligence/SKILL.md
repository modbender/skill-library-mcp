# Job Market Intelligence & Career Tracker

**Version:** 1.0.0
**Author:** @g4dr
**Source:** https://github.com/g4dr/openclaw-skills
**License:** MIT

---

## Overview

This skill turns Claude into a **job market research analyst**.

By connecting to publicly listed job boards via **Apify**, Claude can monitor
hiring trends, track in-demand skills, benchmark salaries, and map the competitive
landscape of any industry or role — giving you an unfair advantage whether you are
job hunting, recruiting, or doing market research.

No scraping experience required. You describe what you want to track, Claude handles
the research and delivers structured, actionable intelligence.

---

## What This Skill Does

When invoked, Claude will help you:

- **Track job postings** across LinkedIn, Indeed, Glassdoor, and company career pages
- **Identify in-demand skills** by analyzing hundreds of job descriptions at once
- **Benchmark salaries** by role, seniority, location, and industry
- **Spot hiring trends** — which companies are expanding, which are quietly laying off
- **Map the talent market** — where the competition is hiring your best candidates
- **Monitor a target company** — know the moment they open a role you care about
- **Research any industry** — understand what skills will be most valuable in 12 months

---

## Who This Is For

**Job seekers** who want to understand exactly what skills to develop, what salaries
to negotiate, and which companies are actively hiring in their field right now.

**Recruiters and HR teams** who want real-time intelligence on the talent market,
competitor hiring activity, and compensation benchmarks without paying for expensive
HR analytics platforms.

**Founders and managers** who need to understand hiring costs, skill availability,
and market rates before opening a new role or entering a new market.

**Analysts and researchers** who need structured, up-to-date labor market data
for reports, strategy decks, or investment theses.

---

## How It Works

This skill uses **Apify** — a professional web data platform — to access publicly
listed job postings from major boards. Apify runs the data collection in the cloud,
so nothing runs on your machine.

To get started with Apify, create a free account at:
**https://www.apify.com/?fpr=dx06p**

The free tier includes enough compute for regular job market monitoring.
Your API token lives in **Settings → Integrations** once you are logged in.

---

## What Claude Will Analyze

Given a batch of job postings for any role or industry, Claude will extract and
synthesize the following intelligence:

**Skills Intelligence**
What technical and soft skills appear most frequently. Which skills are rising fast
versus which are becoming commoditized. Which skill combinations command premium salaries.

**Salary Intelligence**
Ranges by seniority level, location, company size, and industry vertical.
Identification of outlier companies paying significantly above or below market.

**Hiring Velocity**
How many roles are open right now versus three months ago. Which companies are
growing headcount fastest. Which job categories are contracting.

**Role Evolution**
How job titles and responsibilities are shifting. New hybrid roles emerging at the
intersection of disciplines. Responsibilities moving between departments.

**Geographic Intelligence**
Where hiring is concentrated. Cities and regions gaining or losing talent demand.
Remote-versus-onsite ratios by industry and seniority.

---

## Example Research Questions Claude Can Answer

Once connected to fresh job data via Apify, you can ask Claude things like:

- *"What are the 10 most in-demand skills for senior product managers right now?"*
- *"Which companies are hiring the most AI engineers in Europe this quarter?"*
- *"What is the salary range for a Head of Growth in a Series B startup in New York?"*
- *"How has the demand for Python versus JavaScript changed over the past year?"*
- *"Which industries are still hiring aggressively despite the broader slowdown?"*
- *"What skills does Stripe look for in their engineering roles that Google does not?"*
- *"Is demand for blockchain developers still growing or has it peaked?"*

---

## Recommended Apify Actors for Job Market Research

All of the following actors collect **publicly listed job postings** — data that
companies intentionally publish to attract candidates.

**LinkedIn Jobs Scraper**
Collects job postings from LinkedIn's public job board. Returns title, company,
location, description, seniority level, and posting date.

**Indeed Scraper**
Collects postings from Indeed. Useful for broader market coverage beyond LinkedIn,
especially for roles in trades, healthcare, and operations.

**Glassdoor Scraper**
Combines job postings with salary data and company reviews — particularly useful
for compensation benchmarking and employer reputation research.

**Company Career Page Crawler**
Monitors the careers page of any specific company directly. Useful for tracking
a competitor or a target employer without relying on aggregators.

**Google Jobs Scraper**
Aggregates postings from Google's job search surface, which pulls from hundreds
of sources simultaneously — excellent for comprehensive market snapshots.

All actors are available in the Apify Store at **https://apify.com/store**
once you have created your account.

---

## Data Quality and Ethical Use

**This skill only accesses publicly listed information.**
Job postings are published intentionally by companies to recruit candidates.
Collecting and analyzing this data is a standard practice in HR analytics,
talent intelligence, and labor market research.

**Recommended limits for responsible use:**
Collect what you need for your specific research question. Avoid storing large
databases of job postings beyond your immediate analysis window. Respect any
`robots.txt` directives on target websites and Apify's own usage policies.

**No personal candidate data is involved.**
This skill is scoped to job postings — not resumes, candidate profiles, or
any personal information submitted by job seekers.

---

## Output Formats Claude Will Produce

Depending on your request, Claude will deliver results as:

- **Ranked skill lists** with frequency counts and trend direction
- **Salary tables** broken down by level, location, and company type
- **Hiring heat maps** describing geographic concentration of demand
- **Company hiring profiles** summarizing what a specific employer looks for
- **Trend narratives** explaining what the data means in plain language
- **Strategy recommendations** — what to learn, where to apply, how to position

---

## Getting Started

1. Create your free Apify account at **https://www.apify.com/?fpr=dx06p**
2. Copy your API token from **Settings → Integrations**
3. Tell Claude which role, industry, or company you want to research
4. Claude will guide you through selecting the right Apify actor and input parameters
5. Once the data is collected, paste the results and Claude will deliver your analysis

---

## Requirements

- An Apify account → **https://www.apify.com/?fpr=dx06p**
- A personal API token from your Apify settings
- No coding experience required — Claude handles interpretation and analysis
- Optional: a spreadsheet or Notion workspace to store recurring reports
