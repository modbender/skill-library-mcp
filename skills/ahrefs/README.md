# Ahrefs SEO Analysis Skill

> **Complete Ahrefs API integration for OpenClaw - The most comprehensive SEO analysis skill**

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Full-featured Ahrefs API integration covering Site Explorer, Keywords Explorer, Rank Tracker, Site Audit, SERP Overview, Batch Analysis, and Brand Radar.

## Features

### Site Explorer
- 📊 Domain metrics (DR, UR, traffic, keywords)
- 🔗 Backlinks analysis with geographic filtering
- 📈 Organic keyword research with position filtering
- 🏆 Competitor analysis and comparisons
- 🌏 Country-specific filtering (Advanced/Enterprise)

### Keywords Explorer
- 🔍 Search volume & keyword difficulty
- 💰 CPC estimates & traffic potential
- 🎯 Related keywords & questions
- 📋 SERP analysis & features
- 🔄 Batch keyword processing (up to 100)

### Rank Tracker
- 📍 Position tracking & monitoring
- 📊 Historical ranking data
- 🥊 Competitor rankings comparison
- 📢 Share of voice metrics
- 🎯 SERP feature tracking

### Site Audit
- ✅ Site health scoring
- 🐛 Technical SEO issue detection
- 🔗 Internal link analysis
- ⚡ Page performance metrics
- 📋 Duplicate content detection

### Advanced Features
- 📦 Batch analysis (up to 100 targets)
- 📡 Brand mention monitoring
- 🎯 Unlinked mention discovery
- 💬 Share of voice comparison
- 💵 API unit cost optimization

## Prerequisites

### Ahrefs Subscription

You need an Ahrefs subscription with API access:

| Plan | Features | Best For |
|------|----------|----------|
| **Lite** | Basic metrics, limited filtering | Quick domain checks, basic stats |
| **Standard** | More endpoints, some filtering | Regular SEO audits, basic competitor analysis |
| **Advanced** | Advanced filtering, more data | Professional SEO work, detailed analysis |
| **Enterprise** | Full API access, advanced filtering, high limits | Agencies, large-scale SEO operations |

Get your API token from [Ahrefs Account Settings](https://ahrefs.com/api).

## Installation

### Via OpenClaw

```bash
# Install the skill
openclaw skills install ahrefs

# Or clone from ClawHub
openclaw skills install https://clawhub.com/skills/ahrefs
```

### Manual Installation

1. Clone or download this skill to `~/.openclaw/workspace/skills/ahrefs/`
2. Configure your API credentials (see Configuration below)

## Configuration

Add your Ahrefs API credentials to `~/.openclaw/workspace/.env`:

```bash
# Required
AHREFS_API_TOKEN=your_api_token_here

# Required - Specify your plan tier
AHREFS_API_PLAN=enterprise  # Options: lite, standard, advanced, enterprise
```

### Verify Setup

```bash
grep AHREFS ~/.openclaw/workspace/.env
```

## Usage Examples

### Basic Domain Analysis

```bash
# Get domain overview
openclaw agent --message "Analyze SEO metrics for example.com using Ahrefs"

# Compare two domains
openclaw agent --message "Compare example.com vs competitor.com in Ahrefs"
```

### Advanced Queries (Advanced/Enterprise Plans)

```bash
# First-page keywords only
openclaw agent --message "Show me all keywords ranking in positions 1-10 for example.com"

# Australian backlinks only
openclaw agent --message "Get all backlinks from .au domains pointing to example.com"

# Filtered comparison
openclaw agent --message "Compare example.com vs competitor.com using only first-page keywords and Australian backlinks"
```

## Plan-Specific Features

### All Plans ✓
- Domain Rating & Ahrefs Rank
- Backlinks count (total live/historical)
- Organic keywords count
- Organic traffic estimates
- Keywords in positions 1-3

### Standard & Above ✓
- Organic keywords list (all positions)
- Referring domains list
- Top pages by traffic

### Advanced & Enterprise Only ✓
- **Position filtering**: Filter keywords by position (1-10 for first page)
- **Geographic filtering**: Filter backlinks by country/TLD
- **Large datasets**: Query up to 5,000+ records
- **Detailed metrics**: Access advanced fields like `best_position`, `sum_traffic`

## API Endpoints Reference

See [references/api-endpoints.md](references/api-endpoints.md) for detailed endpoint documentation.

### Quick Reference

```bash
# Basic metrics (all plans)
GET /site-explorer/metrics
GET /site-explorer/backlinks-stats
GET /site-explorer/domain-rating

# List endpoints (standard+)
GET /site-explorer/organic-keywords
GET /site-explorer/refdomains
GET /site-explorer/top-pages

# Advanced filtering (advanced/enterprise)
GET /site-explorer/organic-keywords?where=best_position:lte:10
GET /site-explorer/refdomains (filter .au in client-side)
```

## Troubleshooting

### "Column not found" errors
- Your plan may not support the requested fields
- Check [references/api-endpoints.md](references/api-endpoints.md) for available fields per endpoint
- Enterprise plans have access to all fields

### Rate limiting (HTTP 429)
- Reduce request frequency
- Implement caching for frequently accessed data
- Consider upgrading your plan for higher limits

### Authentication errors (HTTP 401)
- Verify `AHREFS_API_TOKEN` is correctly set in `.env`
- Check your token hasn't expired
- Ensure you're using `AHREFS_API_TOKEN` (not `AHREFS_MCP_TOKEN`)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Links

- [Ahrefs API Documentation](https://ahrefs.com/api/documentation)
- [ClawHub Skill Page](https://clawhub.com/skills/ahrefs)
- [OpenClaw Documentation](https://docs.openclaw.ai)

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/ahrefs-skill/issues)
- OpenClaw Community: [Discord](https://discord.gg/clawd)
