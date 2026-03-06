# API Reference - Work Application Skill

## CLI Commands

### `profile show`
Display the master profile.
```bash
python3 scripts/work_application.py profile show
```
Output: Name, title, email, phone, location, skills count, experiences count.

### `profile validate`
Validate the adapted profile against CV formatting guardrails.
```bash
python3 scripts/work_application.py profile validate
```
Output: Errors and warnings from validators. Exit code 0 if valid, 1 if errors.

### `render`
Generate an HTML CV from the adapted profile.
```bash
python3 scripts/work_application.py render [--template T] [--color C] [--lang L] [--output FILE]
```
| Option | Default | Description |
|--------|---------|-------------|
| `--template` | config default | classic, modern-sidebar, two-column, creative |
| `--color` | config default | Hex accent color (e.g., #2563eb) |
| `--lang` | config default | fr or en |
| `--output` | stdout | Output file path |

Requires: `allow_export=true`

### `scrape`
Run the job scraper across configured platforms.
```bash
python3 scripts/work_application.py scrape [--platforms P]
```
| Option | Default | Description |
|--------|---------|-------------|
| `--platforms` | all | Comma-separated: free-work,wttj,apec,hellowork,lehibou |

Requires: `allow_scrape=true`, Playwright installed.
Output: Saves to `~/.openclaw/data/work-application/jobs/jobs-found.md`

### `analyze`
Analyze and rank scraped job offers.
```bash
python3 scripts/work_application.py analyze
```
Reads `jobs-found.md`, outputs `jobs-ranked.md` and `jobs-selected.md`.

### `deep-analyze`
Deep analyze jobs by scraping their actual pages for detailed skill matching.
```bash
python3 scripts/work_application.py deep-analyze [--max N]
```
| Option | Default | Description |
|--------|---------|-------------|
| `--max` | 30 | Max number of jobs to deep-analyze |

Requires: Playwright installed. Reads `jobs-found.md`, outputs `jobs-selected.md`.

### `report`
Generate a full multi-dimension analysis report for a single job offer.
```bash
python3 scripts/work_application.py report <url>
```
| Argument | Description |
|----------|-------------|
| `url` | URL of the job offer to analyze (required) |

Analyzes 4 dimensions: skills match (40%), salary vs market (25%), location/remote (20%), company (15%).
Outputs a verdict (Recommande / Possible avec reserves / Non recommande) with score 0-100.
Saves `.md` and `.json` reports to storage under `reports/`.

Requires: Playwright installed.
If `allow_scrape=true`: also scrapes Glassdoor/Indeed for company reviews.
If `report_mode=cv+analysis`: also generates an adapted CV profile.

### `track list`
List tracked candidatures.
```bash
python3 scripts/work_application.py track list [--status S]
```
| Option | Default | Description |
|--------|---------|-------------|
| `--status` | all | en_attente, entretien, negociation, offre, refus, desistement |

### `track add`
Add a new candidature.
```bash
python3 scripts/work_application.py track add COMPANY POSITION [options]
```
| Option | Description |
|--------|-------------|
| `--location` | Job location |
| `--type` | Contract type (default: CDI) |
| `--salary` | Salary range |
| `--source` | Source platform |
| `--url` | Job offer URL |
| `--contact` | Contact name |
| `--email` | Contact email |
| `--phone` | Contact phone |
| `--notes` | Additional notes |

Requires: `allow_tracking=true`

### `track update`
Update candidature status.
```bash
python3 scripts/work_application.py track update COMPANY STATUS
```
Status values: en_attente, entretien, negociation, offre, refus, desistement

Requires: `allow_tracking=true`

### `config`
Display the active configuration.
```bash
python3 scripts/work_application.py config
```

## Profile Schema

The master profile (`profile-master.json`) has this structure:

```json
{
  "name": "string",
  "title": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "linkedin": "string (optional)",
  "github": "string (optional)",
  "portfolio": "string (optional)",
  "summary": {
    "default": "string",
    "adapted": "string (optional)"
  },
  "hard_skills": [
    {"name": "string", "category": "string", "level": "number (1-5)"}
  ],
  "soft_skills": [
    {"name": "string"}
  ],
  "experiences": [
    {
      "title": "string",
      "company": "string",
      "location": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or present",
      "type": "CDI|Freelance|CDD|Stage",
      "achievements": ["string"]
    }
  ],
  "education": [
    {
      "degree": "string",
      "school": "string",
      "year": "string",
      "details": "string (optional)"
    }
  ],
  "certifications": [
    {"name": "string", "issuer": "string", "year": "string"}
  ],
  "languages": [
    {"name": "string", "level": "string"}
  ],
  "projects": [
    {"name": "string", "description": "string", "url": "string (optional)"}
  ]
}
```

## Validator Limits

### Character limits
| Type | Min | Max | Optimal |
|------|-----|-----|---------|
| line | 0 | 90 | 50-75 |
| bullet | 0 | 150 | 80-120 |
| jobTitle | 10 | 60 | 30-50 |
| companyName | 5 | 50 | 20-40 |
| summary | 150 | 400 | 250-350 |
| skillTag | 3 | 25 | 8-15 |

### Count limits
| Type | Min | Max | Optimal |
|------|-----|-----|---------|
| bulletsPerExperience | 2 | 6 | 3-4 |
| experiences | 2 | 6 | 3-4 |
| hardSkills | 5 | 15 | 8-12 |
| softSkills | 3 | 8 | 4-6 |
| summaryLines | 3 | 6 | 4-5 |

## Status Icons

| Key | Icon | Label |
|-----|------|-------|
| en_attente | ⏳ | En attente |
| entretien | 📞 | Entretien |
| negociation | 🤝 | Négociation |
| offre | ✅ | Offre |
| refus | ❌ | Refus |
| desistement | 🚫 | Désistement |
