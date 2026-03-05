---
name: work-application
description: "CV generation, job scraping, offer analysis, and application tracking. Use when: (1) generating or adapting a CV/resume for a job offer, (2) scraping job offers from French platforms, (3) analyzing and ranking job offers, (4) generating a full analysis report for a single offer (skills, company, location, salary), (5) tracking candidatures and their status, (6) validating CV content against formatting guardrails. NOT for: cover letter generation (planned), LinkedIn direct messaging, job application submission, salary negotiation coaching."
homepage: https://github.com/rwx-g/openclaw-skill-work-application
compatibility: Python 3.9+ · Playwright (optional, for scraping) · No network required for CV generation
metadata:
  {
    "openclaw": {
      "emoji": "📄",
      "requires": { "env": [] },
      "primaryEnv": "",
      "suggests": ["nextcloud-files"]
    }
  }
ontology:
  reads: [profile-master, profile-adapted, candidatures, jobs, config, market-data]
  writes: [profile-adapted, candidatures, jobs, cv-html, reports, market-data]
  enhancedBy: [nextcloud-files]
---

# Work Application Skill

Job search automation with CV generation, scraping, analysis, and tracking. 4 HTML CV templates (classic, modern-sidebar, two-column, creative), job scraping across 5 French platforms (Free-Work, WTTJ, Apec, HelloWork, LeHibou), keyword-based scoring, deep page analysis, full multi-dimension report (skills/company/location/salary with market data), and candidature tracking via markdown table. Stdlib only (except Playwright for scraping/analysis). Supports local and Nextcloud storage.

Profiles: `~/.openclaw/data/work-application/` · Config: `~/.openclaw/config/work-application/config.json`

## Trigger phrases

Load this skill when the user says anything like:
- "generate my CV", "create a resume", "render my CV"
- "adapt my CV for this job offer", "tailor my resume"
- "scrape job offers", "find jobs", "search for devops positions"
- "analyze job offers", "rank these jobs", "score job matches"
- "deep analyze these jobs", "scrape and analyze job pages"
- "analyze this job offer", "generate a report for this URL", "report on this job"
- "track this application", "log candidature", "update application status"
- "list my applications", "show candidatures"
- "validate my CV", "check CV formatting"
- "show my profile", "what's in my master profile"

## Quick Start

```bash
python3 scripts/work_application.py profile show
python3 scripts/work_application.py render --template classic --output cv.html
python3 scripts/work_application.py report "https://example.com/job-offer"
python3 scripts/work_application.py track list
```

## Setup

```bash
python3 scripts/setup.py       # interactive: profile + permissions + scraper config
python3 scripts/init.py        # validate configuration
```

**config.json** - behavior restrictions (all destructive capabilities disabled by default):

| Key | Default | Effect |
|-----|---------|--------|
| `allow_write` | **`false`** | allow modifying master profile |
| `allow_export` | `true` | allow generating HTML/PDF |
| `allow_scrape` | **`false`** | allow running job scraper + network requests (requires Playwright) |
| `allow_tracking` | `true` | allow logging candidatures |
| `default_template` | `"classic"` | CV template when not specified |
| `default_color` | `"#2563eb"` | accent color |
| `default_lang` | `"fr"` | language (fr/en) |
| `report_mode` | `"analysis"` | report output: `analysis` or `cv+analysis` |
| `readonly_mode` | **`false`** | override: block **all** writes regardless of above |

## Storage & data

| Path | Written by | Purpose |
|------|-----------|---------|
| `~/.openclaw/config/work-application/config.json` | `setup.py` | Permissions and defaults. No secrets. |
| `~/.openclaw/data/work-application/profile-master.json` | `setup.py` | Complete master profile (all experiences, skills, etc.) |
| `~/.openclaw/data/work-application/profile.json` | Agent | Adapted profile for current job offer |
| `~/.openclaw/data/work-application/candidatures.md` | Agent | Application tracking table |
| `~/.openclaw/data/work-application/jobs/jobs-found.md` | Scraper | Raw scraped job offers |
| `~/.openclaw/data/work-application/jobs/jobs-ranked.md` | Analyzer | Scored and ranked offers |
| `~/.openclaw/data/work-application/jobs/jobs-selected.md` | Analyzer | Top selection (CDI + Freelance) |
| `~/.openclaw/data/work-application/market-data.json` | Report | Market salary references (auto-generated, editable) |
| `~/.openclaw/data/work-application/reports/report-*.md` | Report | Full analysis reports (markdown) |
| `~/.openclaw/data/work-application/reports/report-*.json` | Report | Full analysis reports (JSON) |

**Nextcloud storage** (optional): when `storage.backend = "nextcloud"` is set in config, files are stored on the user's Nextcloud instance instead of locally. Authentication is delegated entirely to the [`openclaw-skill-nextcloud`](https://clawhub.ai/Romain-Grosos/nextcloud-files) skill - this skill never handles Nextcloud credentials. The nextcloud skill must be installed separately.

**Cleanup:** `python3 scripts/setup.py --cleanup`

**Uninstall:** `rm -rf ~/.openclaw/data/work-application/ ~/.openclaw/config/work-application/`

## Security model

### Capability isolation

All capabilities are disabled or restricted by default. The agent cannot perform actions until explicitly enabled in `config.json`:

| Capability | Default | What it gates |
|-----------|---------|---------------|
| `allow_write` | `false` | Modify master profile |
| `allow_export` | `true` | Generate HTML/PDF output |
| `allow_scrape` | `false` | Run Playwright browser, make network requests |
| `allow_tracking` | `true` | Append to candidature log |
| `readonly_mode` | `false` | Master kill-switch - blocks all writes |

### Credential isolation

This skill stores **no secrets** and requires **no environment variables**. `config.json` contains only behavioral flags and defaults - never credentials.

- **Local storage** (default): reads/writes files under `~/.openclaw/data/work-application/`. No authentication needed.
- **Nextcloud storage** (optional): delegates all authentication to the **[`openclaw-skill-nextcloud`](https://clawhub.ai/Romain-Grosos/nextcloud-files)** skill, which manages its own credentials (`NC_URL`, `NC_USER`, `NC_APP_KEY` in `~/.openclaw/secrets/nc_creds`). This skill never reads, stores, or handles Nextcloud credentials directly - it imports `NextcloudClient` from the nextcloud skill at runtime. The nextcloud skill must be installed and configured separately (`clawhub install nextcloud-files`).
- **Scraping** (optional, `allow_scrape=true`): Playwright runs without authentication. Job pages are fetched as anonymous HTTP requests. Company review scraping (Glassdoor/Indeed) also runs unauthenticated - no login or API key is used.

### Path traversal protection

All storage operations (local and Nextcloud) validate filenames through `_validate_name()`:
- Rejects absolute paths (`/etc/passwd`, `C:\...`)
- Rejects traversal sequences (`../`, `..\\`, bare `..`)
- Rejects null bytes (`\x00`)
- Normalizes slashes and collapses redundant separators
- LocalStorage additionally resolves the final path and verifies it remains inside the storage root directory

### HTML output safety

All profile fields are passed through `html.escape()` before HTML rendering. No raw user content is inserted into templates. This prevents XSS if the generated CV is served or shared.

### Network boundaries

- **No network calls** by default - CV generation, analysis, tracking are fully offline
- Network calls only happen when `allow_scrape=true`, exclusively via Playwright (headless Chromium)
- **Domains contacted when scraping**: `free-work.com`, `welcometothejungle.com`, `apec.fr`, `hellowork.com`, `lehibou.com` (job platforms), plus the specific job offer URL provided by the user
- **Domains contacted by report** (optional, `allow_scrape=true`): `glassdoor.fr`, `fr.indeed.com` (company reviews - unauthenticated, anonymous)
- **Nextcloud storage** (optional): contacts the user's own Nextcloud instance via the nextcloud skill - no third-party server
- URLs built from user data (company names for review lookup) are properly URL-encoded
- No background network activity, no telemetry, no phone-home

### File output safety

- Reports and CVs are written only to the configured storage directory (`~/.openclaw/data/work-application/` or Nextcloud remote path)
- Filenames derived from user data (company names) are strictly sanitized to ASCII alphanumeric + hyphens
- Subdirectories (`reports/`, `jobs/`) are created inside the storage root only

## Module usage

```python
from scripts._profile import load_master_profile, load_adapted_profile, save_adapted_profile
from scripts._cv_renderer import render_cv
from scripts._validators import validate_profile
from scripts._tracker import log_application, list_applications, update_status
from scripts._report import generate_report, format_report_markdown, save_report
```

## CLI reference

```bash
# Profile
python3 scripts/work_application.py profile show
python3 scripts/work_application.py profile validate

# CV Rendering
python3 scripts/work_application.py render --template classic --output cv.html
python3 scripts/work_application.py render --template modern-sidebar --color "#e63946" --lang en

# Job Scraping
python3 scripts/work_application.py scrape
python3 scripts/work_application.py scrape --platforms free-work,wttj

# Job Analysis
python3 scripts/work_application.py analyze

# Deep Analysis (scrape job pages for detailed matching)
python3 scripts/work_application.py deep-analyze
python3 scripts/work_application.py deep-analyze --max 10

# Report (full multi-dimension analysis of a single offer)
python3 scripts/work_application.py report "https://example.com/job-offer"

# Application Tracking
python3 scripts/work_application.py track list
python3 scripts/work_application.py track list --status en_attente
python3 scripts/work_application.py track add "Thales" "DevOps Engineer" --location Paris --salary "55-65k"
python3 scripts/work_application.py track update "Thales" entretien

# Config
python3 scripts/work_application.py config
```

## Templates

### Adapt CV for a job offer
```python
from scripts._profile import load_master_profile, save_adapted_profile
from scripts._cv_renderer import render_cv
from scripts._validators import validate_profile

# 1. Load master profile
master = load_master_profile()
# 2. Agent adapts profile for the job (select relevant skills, rewrite summary, etc.)
adapted = adapt_for_job(master, job_description)  # agent logic
# 3. Validate
report = validate_profile(adapted)
if not report["valid"]:
    print("Errors:", report["errors"])
# 4. Save and render
save_adapted_profile(adapted)
html = render_cv(adapted, template="classic", color="#2563eb")
```

### Scrape → Analyze → Track
```python
# 1. Scrape jobs
from scripts._scraper import JobScraper, filter_jobs, deduplicate
scraper = JobScraper(config)
jobs = asyncio.run(scraper.scrape_all())
jobs = deduplicate(filter_jobs(jobs, config["scraper"]["filters"]))

# 2. Analyze
from scripts._analyzer import rank_jobs, select_top
ranked = rank_jobs(jobs, master_profile)
selected = select_top(ranked)

# 3. Track top matches
from scripts._tracker import log_application
for job in selected["cdi"][:5]:
    log_application(job["company"], job["title"], location=job.get("location",""))
```

### Quick candidature update
```python
from scripts._tracker import update_status, list_applications
update_status("Thales", "entretien")
active = list_applications(status="en_attente")
```

## CV Templates

| Template | Description | Best for |
|----------|-------------|----------|
| `classic` | Single-column, ATS-optimized | Most applications, ATS systems |
| `modern-sidebar` | Sidebar (35%) + main (65%) | Tech companies, startups |
| `two-column` | Two-column grid (38/62) | Creative roles, design-aware |
| `creative` | Timeline, gradient header | Personal branding, portfolios |

## Status icons

| Status | Icon | Meaning |
|--------|------|---------|
| `en_attente` | ⏳ | Waiting for response |
| `entretien` | 📞 | Interview scheduled |
| `negociation` | 🤝 | In negotiation |
| `offre` | ✅ | Offer received |
| `refus` | ❌ | Rejected |
| `desistement` | 🚫 | Withdrawn |

## Scraper platforms

| Platform | URL | Types | Notes |
|----------|-----|-------|-------|
| Free-Work | free-work.com | Freelance | TJM parsing, remote detection |
| WTTJ | welcometothejungle.com | CDI | Salary ranges, company pages |
| Apec | apec.fr | CDI/Cadre | Executive positions |
| HelloWork | hellowork.com | CDI | Broad coverage |
| LeHibou | lehibou.com | Freelance | IT freelance missions |

## Ideas
- Set `allow_scrape: false` + `allow_export: true` for a CV-only mode
- Use scraper with `allow_tracking: true` to auto-log the best matches
- Adapt CV per job offer, validate, render, then log the application
- Use `readonly_mode: true` for a safe demo mode

## Notes
- **Playwright dependency**: Only needed for scraping. CV generation is stdlib only.
- **Profile structure**: Master profile contains ALL data. Adapted profile is a filtered subset for a specific job.
- **Validators**: Port of the JavaScript validators - same limits and thresholds.
- **i18n**: CV rendering supports French and English section headings.
- **Print-ready**: Generated HTML includes @media print rules and A4 page breaks.

## Combine with

| Skill | Workflow |
|-------|----------|
| **ghost** | Generate CV → publish as Ghost page |
| **nextcloud** | Save rendered CV to Nextcloud |
| **gmail** | Send CV as email attachment |
| **veille** | Monitor job market trends → adapt search queries |

## API reference
See `references/api.md` for CLI command details and profile schema.

## Troubleshooting
See `references/troubleshooting.md` for common errors and fixes.
