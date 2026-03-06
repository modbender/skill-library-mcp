# Generect API Filter Reference

## Lead Search Filters (`/leads/by_icp/`)

| Filter | Type | Example |
|--------|------|---------|
| `job_title` | string[] | `["CEO", "Founder"]` |
| `location` | string[] | `["United States", "Germany"]` |
| `industry` | string[] | `["Software Development"]` |
| `company_headcount_range` | string[] | `["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10001+"]` |
| `company_name` | string[] | `["Google", "Meta"]` |
| `seniority_level` | string[] | `["Director", "VP", "C-Suite", "Manager"]` |
| `job_function` | string[] | `["Sales", "Marketing", "Engineering"]` |
| `keyword` | string | Free-text search across profiles |
| `page` | int | Pagination (starts at 1) |
| `per_page` | int | Results per page (max 25) |

## Company Search Filters (`/companies/by_icp/`)

| Filter | Type | Example |
|--------|------|---------|
| `industry` | string[] | `["Information Technology"]` |
| `location` | string[] | `["San Francisco"]` |
| `headcount_range` | string[] | `["51-200"]` |
| `company_type` | string[] | `["Privately Held", "Public Company"]` |
| `founded_year_min` | int | `2020` |
| `founded_year_max` | int | `2025` |
| `keyword` | string | Free-text company search |
| `page` | int | Pagination |
| `per_page` | int | Results per page |

## Lead Response Fields

Each lead object contains:
- **Identity:** `full_name`, `first_name`, `last_name`, `headline`, `linkedin_url`
- **Current job:** `job_title`, `company_name`, `company_website`, `company_industry`, `company_headcount_range`, `job_started_on`, `job_description`
- **Company:** `company_city`, `company_country`, `company_state`, `company_location`
- **History:** `jobs[]` (all positions), `educations[]`, `certifications[]`
- **Other:** `skills[]`, `languages[]`, `is_premium`, `is_job_seeker`

## Company Response Fields

Each company object contains:
- **Identity:** `name`, `domain`, `linkedin_link`, `linkedin_id`, `website`
- **Profile:** `description`, `tagline`, `industry`, `company_type`, `founded_year`
- **Size:** `headcount_exact`, `headcount_range`
- **Location:** `hq_city`, `hq_country`, `hq_state`, `hq_street`, `hq_postal_code`
- **Other:** `logo_url`, `specialities[]`, `hashtags[]`, `crunchbase_urn`
