# Chart Dashboard Links

Generate shareable links to RevenueCat dashboard charts with filters preserved.

## Dashboard URL Format

**IMPORTANT**: Use this exact structure:

```
https://app.revenuecat.com/projects/{project_id}/charts/{chart_name}?range={range_value}
```

- `{project_id}` — The short hex ID (e.g., `56965ae1`), NOT the full `proj56965ae1`
- `{chart_name}` — Chart name like `revenue`, `churn`, `mrr`, etc.
- Project ID goes in the **path**, not as a query parameter

**Correct example:**
```
https://app.revenuecat.com/projects/56965ae1/charts/revenue?range=Last+90+days%3A2025-11-16%3A2026-02-13
```

**WRONG — do not use:**
```
https://app.revenuecat.com/charts/revenue?project=proj56965ae1&chart_start=...&chart_end=...
```

## Query Parameters

### Date Range (`range`) — REQUIRED

The `range` parameter controls the date range. Format: `{preset}:{start_date}:{end_date}`

**You must use this format** — do NOT use `start_date`, `end_date`, `chart_start`, or `chart_end` params.

| Preset | Encoded Value |
|--------|---------------|
| Last 7 days | `range=Last+7+days%3A2026-02-06%3A2026-02-13` |
| Last 28 days | `range=Last+28+days%3A2026-01-16%3A2026-02-13` |
| Last 90 days | `range=Last+90+days%3A2025-11-16%3A2026-02-13` |
| Last 365 days | `range=Last+365+days%3A2025-02-13%3A2026-02-13` |
| Custom | `range=Custom%3A2025-01-01%3A2025-12-31` |

Note: The `:` between parts must be URL-encoded as `%3A`. Spaces become `+`.

### Resolution (`resolution`)

| Value | Meaning |
|-------|---------|
| `day` | Daily granularity |
| `week` | Weekly granularity |
| `month` | Monthly granularity |
| `quarter` | Quarterly granularity |
| `year` | Yearly granularity |

### Segment (`segment_by`)

Dimension to break down the data by. Common values:
- `country` — by country
- `store` — by app store (App Store, Play Store, etc.)
- `product` — by product identifier
- `platform` — by platform (iOS, Android, etc.)
- `offering` — by offering

### Filters

Filters are passed as individual query params with the filter name as key:

| Filter | Example |
|--------|---------|
| `country` | `country=US` |
| `store` | `store=app_store` |
| `product_identifier` | `product_identifier=premium_monthly` |
| `platform` | `platform=iOS` |

Multiple values for the same filter: `country=US&country=DE&country=JP`

### Chart-Specific Selectors

Some charts have special selectors:

**Conversion/Retention charts:**
- `customer_lifetime` — e.g., `30+days`, `60+days`, `90+days`
- `conversion_timeframe` — e.g., `7+days`, `14+days`, `30+days`

**Workflow charts:**
- `path` — workflow path filter
- `workflows_customer_lifetime` — e.g., `initial`

## Constructing a Link

To generate a dashboard link:

1. Start with base: `https://app.revenuecat.com/projects/{project_id}/charts/{chart_name}`
2. Add `range` param with date range
3. Add any filters as query params
4. Add `segment_by` if segmenting
5. Add chart-specific selectors as needed
6. URL-encode all values (spaces → `+`, colons → `%3A`, etc.)

## API to Dashboard Parameter Mapping

When translating from API parameters to dashboard URLs:

| API Parameter | Dashboard Parameter |
|---------------|---------------------|
| `start_date` + `end_date` | `range=Custom%3A{start}%3A{end}` (use `Custom` preset) |
| `segment` | `segment_by` |
| `filters` (JSON array) | Individual query params |
| `selectors` (JSON object) | Individual query params |

**Note**: Do NOT pass `resolution` as a numeric value. The resolution is typically implied by the range preset or omitted.

## Example: Building a Link

User wants: "Revenue chart for last 90 days, segmented by country, filtered to US and Germany"

Calculate dates: if today is 2026-02-13, then 90 days ago is 2025-11-16.

```
https://app.revenuecat.com/projects/56965ae1/charts/revenue?range=Last+90+days%3A2025-11-16%3A2026-02-13&segment_by=country&country=US&country=DE
```

User wants: "Churn chart from August 2025 to now"

Use the `Custom` preset for arbitrary date ranges:

```
https://app.revenuecat.com/projects/56965ae1/charts/churn?range=Custom%3A2025-08-01%3A2026-02-13
```

## Getting Project ID

The project ID can be found via the API:
- `GET /projects` — lists all projects with their IDs
- API returns IDs like `proj56965ae1`
- **For dashboard URLs, strip the `proj` prefix** — use just `56965ae1` in the path
