# Dievio Filters Cheatsheet

All filters are optional.

## Combination Rules

- Different filter groups use AND.
- Arrays inside one field use OR.

## Core Filter Fields

- `first_name` (string)
- `last_name` (string)
- `job_titles` (string[])
- `job_title_seniority` (string[])
- `job_departments` (string[])
- `employee_size` (string[])
- `company_revenue` (string[])
- `person_location_country` (string[])
- `person_location_region` (string[])
- `person_location_locality` (string[])
- `industries` (string[])
- `industry_keywords` (string[])
- `inferred_salary` (string[])
- `funding_start_date` (year string)
- `funding_end_date` (year string)
- `business_model` (string[])
- `company_location_country` (string[])
- `company_location_region` (string[])
- `company_location_locality` (string[])
- `company_websites` (string[])

## Output / Paging Flags

- `email_status`: `all` | `verified` | `likely`
- `include_emails`: boolean
- `include_phones`: boolean
- `_include_raw`: boolean
- `_per_page`: number
- `_page`: number
- `max_results`: number (max `100000`)

## Allowed Values (Documented)

### `job_title_seniority`

`owner`, `cxo`, `partner`, `vp`, `director`, `manager`, `senior`, `entry`, `training`, `unpaid`

### `job_departments`

`engineering`, `sales`, `marketing`, `finance`, `operations`, `human_resources`, `product`, `design`, `data`, `legal`, `customer_service`, `consulting`, `business_development`, `education`

### `employee_size`

`1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+`

### `business_model`

`b2b`, `b2c`, `b2b2c`, `marketplace`, `saas`, `ecommerce`

### `inferred_salary`

`<20,000`, `20,000-25,000`, `25,000-35,000`, `35,000-45,000`, `45,000-55,000`, `55,000-70,000`, `70,000-85,000`, `85,000-100,000`, `100,000-150,000`, `150,000-250,000`, `>250,000`

### `person_location_country` (examples)

`United States`, `United Kingdom`, `Canada`, `Australia`, `Germany`, `France`, `India`, `China`, `Japan`, `Brazil`, `Mexico`, `Spain`, `Italy`, `Netherlands`, `Sweden`, `Switzerland`, `Singapore`, `Israel`, `United Arab Emirates`, `South Korea`, `Russia`, `Poland`, `Ireland`, `Belgium`, `Austria`, `Norway`, `Denmark`, `Finland`, `New Zealand`

### `person_location_region` (examples)

US states + District of Columbia, plus examples like `England`, `Scotland`, `Wales`, `Northern Ireland`, `Ontario`, `Quebec`, `British Columbia`, `Alberta`, `New South Wales`, `Victoria`, `Queensland`.
