---
name: build-amazon-affiliate-plugin
description: Create a production-ready WordPress plugin that displays Amazon product ads when users insert Amazon affiliate links. Use when asked to build an Amazon Associates/affiliate WordPress plugin with features like: (1) Detecting Amazon links in post content, (2) Extracting ASIN from URLs, (3) Generating ad units with product info, (4) Admin settings page for affiliate tag and display options, (5) Caching for performance, (6) Gutenberg block support. Follows WordPress best practices and Amazon Associates Program Policies.
---

# Build Amazon Affiliate Ad Plugin

## Quick Start

1. Read [PLUGIN_SPEC.md](references/PLUGIN_SPEC.md) for detailed requirements
2. Read [AMAZON_API.md](references/AMAZON_API.md) for PA-API integration
3. Generate the plugin code following the specifications

## Plugin Requirements Summary

- **Name**: Ad Symbiont
- **Features**:
  - Detect Amazon links (amazon.com, amazon.ca, amazon.co.uk, amzn.to)
  - Extract ASIN from URLs
  - Admin settings: Affiliate tag, display mode (replace/append), styling toggle
  - Fallback to simple HTML ad if no PA-API credentials
  - Caching for ad units (transients)
  - Gutenberg block support
  - WordPress 6.x compatible
  - Secure: sanitize/escape all inputs/outputs

## Output

Generate:
1. Complete plugin PHP file
2. CSS/JS assets if needed
3. Installation instructions
4. Expansion options documentation

Save all files to: `/home/imjohnathan/.openclaw/workspace/skills/build-amazon-affiliate-plugin/`
