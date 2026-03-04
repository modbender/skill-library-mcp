# Changelog

## [0.1.0] - 2026-03-03

### Added
- Initial release
- Multi-city event discovery: Tel Aviv, Barcelona, New York
- Fetchers: Ticketmaster, Eventbrite, TLV Municipality, Lev Cinema, NYC Open Data
- Browser-based fetchers (Playwright): Time Out IL, Fever, Xceed
- Unified `Event` model with types, age groups, time-of-day classification
- CLI with city, type, age, time, date, free filters
- JSON output mode
- Parallel fetch via ThreadPoolExecutor
- Deduplication + chronological ranking
