# Changelog

All notable changes to the Ahrefs skill will be documented in this file.

## [1.2.0] - 2026-02-18

### Added
- **Keywords Explorer**: Complete keyword research capabilities
  - Search volume, keyword difficulty, CPC data
  - Related keywords and keyword ideas
  - SERP analysis and features
  - Batch keyword metrics
- **Rank Tracker**: Position monitoring and tracking
  - Project-based rank tracking
  - Historical position data
  - Competitor rankings comparison
  - Share of voice metrics
  - SERP feature tracking
- **Site Audit**: Technical SEO analysis
  - Site health scoring
  - Issue detection by severity
  - Internal link analysis
  - Page performance metrics
  - Duplicate content detection
- **SERP Overview**: Search results analysis
  - Top 100 organic results
  - Domain metrics for ranking pages
  - SERP feature identification
- **Batch Analysis**: Bulk processing capabilities
  - Process up to 100 domains/URLs per request
  - Batch keyword metrics
  - Cost-efficient bulk operations
- **Brand Radar**: Brand monitoring and mentions
  - Brand mention tracking
  - Unlinked mention identification
  - Share of voice comparison
  - Sentiment analysis
  - Top mentioning domains
- **API Unit Management**: Cost optimization guidance
  - Unit consumption tracking
  - Cost optimization tips
  - Rate limit handling
- **Common Workflows**: Practical workflow patterns
  - Keyword research workflow
  - Competitive analysis workflow
  - Technical SEO audit workflow
  - Content strategy workflow
  - Batch domain analysis workflow

### Enhanced
- Expanded core capabilities documentation
- Added detailed endpoint references for all new features
- Improved usage examples with real-world scenarios
- Enhanced error handling guidance

### Documentation
- `references/keywords-explorer.md` - Complete Keywords Explorer API reference
- `references/rank-tracker.md` - Rank Tracker API reference
- `references/site-audit.md` - Site Audit API reference
- `references/batch-analysis.md` - Batch processing guide
- `references/brand-radar.md` - Brand monitoring reference

### Notes
- Rank Tracker and Site Audit require pre-configured projects
- Brand Radar availability varies by plan
- Batch processing reduces API unit costs by 90-95%

## [1.1.0] - 2026-02-18

### Added
- **Plan configuration**: Users can now specify their Ahrefs API plan (lite/standard/advanced/enterprise) in `.env` file
- **Advanced filtering support**: Added examples for filtering keywords by position (first page rankings)
- **Geographic filtering**: Added examples for filtering backlinks by country/TLD (e.g., Australian `.au` domains)
- **Plan-specific documentation**: Clear breakdown of features available at each plan tier
- **Enterprise API examples**: Added working examples with correct field names (`best_position`, `sum_traffic`, `links_to_target`)
- **Detailed setup instructions**: Step-by-step guide for configuring API token and plan

### Changed
- Updated SKILL.md with plan-aware capabilities
- Enhanced Prerequisites section with plan information
- Improved documentation structure for better clarity

### Fixed
- Corrected field names for organic keywords endpoint (`best_position` instead of `position`)
- Corrected field names for refdomains endpoint (`links_to_target` instead of `backlinks`)
- Fixed URL encoding issues in PowerShell examples
- Updated examples to work with enterprise API tier

### Notes
- Basic plans can access summary metrics (metrics, backlinks-stats, domain-rating)
- Advanced/Enterprise plans required for detailed filtering and large dataset queries
- Rate limits vary by plan tier

## [1.0.0] - 2026-02-01

### Initial Release
- Basic Ahrefs API integration
- Domain overview queries
- Backlinks stats
- Organic keywords and traffic metrics
- Domain rating
- Top pages analysis
- PowerShell and Bash examples
