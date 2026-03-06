# Actor input guide (LurATYM4hkEo78GVj)

Actor source:
- https://console.apify.com/actors/LurATYM4hkEo78GVj/source

Common fields:
- `max_results` (int): number of leads to collect
- `job_titles` (string[]): role targeting (e.g., CEO, Founder)
- `job_title_seniority` (string[]): seniority targeting
- `person_location_country` (string[]): countries
- `person_location_region` (string[]): states/regions
- `employee_size` (string[]): company size buckets
- `industries` (string[]): industry filters
- `email_status` (string): often `verified` for higher quality
- `include_emails` (bool)
- `include_phones` (bool)

Seniority enum (from actor schema):
- `owner`, `cxo`, `partner`, `vp`, `director`, `manager`, `senior`, `entry`, `training`, `unpaid`

Example payload:

```json
{
  "max_results": 1000,
  "job_titles": ["CEO", "Founder"],
  "job_title_seniority": ["cxo", "owner"],
  "person_location_country": ["United States"],
  "employee_size": ["11-50", "51-200"],
  "industries": ["Computer Software"],
  "email_status": "verified",
  "include_emails": true,
  "include_phones": false
}
```
