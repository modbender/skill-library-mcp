# GA Deep Dive — Future Improvements

## Completed ✅
- [x] Fix 10-metric limit (split queries)
- [x] Fix DAU/MAU ratio calculation
- [x] Add week-over-week growth
- [x] Add campaigns/UTM section
- [x] Add conversions/key events section

## Priority 1 — Next Up
- [ ] Add `--json` flag for machine-readable output
- [ ] Add `--compare` flag for period comparison (vs previous period)
- [ ] Add exit pages analysis (where users leave the site)
- [ ] Add scroll depth if available (percentScrolled)
- [ ] Better error messages (show which section failed)

## Priority 2 — Nice to Have
- [ ] Add `--verbose` flag for full 374 dimensions
- [ ] Add funnel analysis (custom event sequences)
- [ ] Add cohort analysis (retention over time)
- [ ] Demographics (age, gender) if available
- [ ] Content groups (contentGroup dimension)
- [ ] Search terms (internal site search)
- [ ] First user attribution (firstUserSource, firstUserMedium)

## Priority 3 — Advanced
- [ ] Rate limiting (GA4 has quotas)
- [ ] Caching (avoid re-fetching same data)
- [ ] Export to CSV/Excel
- [ ] Email report delivery
- [ ] Slack/Discord integration
- [ ] Automated alerts (engagement drop, traffic spike)

## Research Notes

### API Limits Discovered
- 10 metrics max per request
- 9 dimensions max per request
- 100k rows max per response
- Rate limits: 600 requests/min per project

### Useful Dimensions Not Yet Used
- `audienceName` — GA4 audiences
- `firstUserCampaign` — attribution
- `exitPage` — where users leave (requires funnel)
- `percentScrolled` — engagement depth
- `outbound` — external link clicks
- `linkUrl` — clicked link destinations
- `searchTerm` — internal search

### Reference
- [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/)
- [API Schema Docs](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
